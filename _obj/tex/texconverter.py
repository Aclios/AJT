import os
import shutil
from PIL import Image
from subprocess import DEVNULL, STDOUT, check_call
from _obj.tex.switch_swizzle import *


#all the texture format that exist in AJT, but only BC1_UNORM, BC7_UNORM and RGBA8888 are used for assets, the other one are used on stuff like shaders RE Engine files
tex_format_dict = {
0x47:"BC1_UNORM",
0x48:"BC1_UNORM_SRGB",
0x50:"BC4_UNORM",
0x53:"BC5_UNORM",
0x62:"BC7_UNORM",
0x63:"BC7_UNORM_SRGB",
0x1c:"RGBA8888_UNORM"
}

bits_per_pixel_dict = {
"BC7_UNORM":16,
"BC1_UNORM":8
}

def readint32(file):
    return int.from_bytes(file.read(4),'little')

def readint16(file):
    return int.from_bytes(file.read(2),'little')

def readint8(file):
    return int.from_bytes(file.read(1))

def writeint32(file,value):
    file.write(value.to_bytes(4,'little'))


class DDS: #simple DDS reading to get pixel data
    def __init__(self,dds_filepath):
        with open(dds_filepath,mode='rb') as f:
            self.magic = f.read(4)
            if self.magic != b'DDS ':
                raise Exception("Error: the file isn't a valid DDS file (bad magic)")
            f.seek(0x14)
            self.pitch = readint32(f)
            f.seek(0x54)
            format = f.read(4)
            if format == b'DX10':
                f.seek(0x94)
                self.data = f.read()
            else:
                f.seek(0x80)
                self.data = f.read()



class AJTTex:
    def __init__(self,tex_filepath,platform):
        with open(tex_filepath,mode='rb') as f:
            self.filepath = tex_filepath
            self.filename = os.path.basename(tex_filepath)
            self.platform = platform
            self.magic = f.read(4)
            if self.magic != b'TEX\x00':
                raise Exception("Error: the file isn't a valid TEX file (bad magic)")
            self.version = readint32(f)
            if self.version != 719230324:
                raise Exception("Error: TEX version is not correct")
            self.width = readint16(f)
            self.height = readint16(f)
            self.unknown = f.read(2) #always \x01\x00 (?)
            self.img_count = readint8(f) # = 1
            self.mipmap_count = readint8(f) // 16
            self.format_num = readint32(f)
            try:
                self.format = tex_format_dict[self.format_num]
            except KeyError:
                raise Exception("Error: unknown DDS pixel format")
            self.flags = f.read(0x14)
            self.mipmap_header_list = []
            for _ in range(self.mipmap_count):
                if platform == "Steam":
                    self.mipmap_header_list.append(SteamMipmapHeader(f))
                elif platform == "Switch":
                    self.mipmap_header_list.append(SwitchMipmapHeader(f))
            f.seek(self.mipmap_header_list[0].data_offset)
            self.data_size = self.mipmap_header_list[0].data_size
            self.data = f.read(self.data_size)
            if platform == 'Switch':
                self.data_size = self.mipmap_header_list[0].effective_data_size

    def compute_width_from_pitch(self): #on Steam, tex can be wider than the header width. It's possible to compute the real width from the "pitch"
        block = bits_per_pixel_dict[self.format]
        return int(((4 * self.mipmap_header_list[0].pitch) / block))

    def convert_BC_to_png(self,output_dir):
        dds_filepath = os.path.join(output_dir,self.filename + '.dds')
        with open(dds_filepath,mode='wb') as f:
            f.write(b'DDS ')
            writeint32(f,124)
            writeint32(f,659463)
            if self.platform == 'Steam':
                real_width = self.compute_width_from_pitch()
                writeint32(f,self.height)
                writeint32(f,real_width)
            if self.platform == 'Switch':
                self.extendedwidth = self.width
                self.extendedheight = self.height
                if self.height < 256:
                    self.extendedheight = 256
                elif self.height % 512 != 0:
                    self.extendedheight = ((self.height // 512) + 1) * 512
                if self.format == 'BC1_UNORM':
                    if self.extendedwidth % 32 != 0:
                        self.extendedwidth = ((self.width // 32) + 1) * 32
                elif self.format == 'BC7_UNORM':
                    if self.extendedwidth % 16 != 0:
                        self.extendedwidth = ((self.width // 16) + 1) * 16
                writeint32(f,self.extendedheight)
                writeint32(f,self.extendedwidth)
            writeint32(f,self.data_size)
            writeint32(f,1)
            writeint32(f,1)
            f.write(b'\x00' * 0x2c)
            writeint32(f,0x20)
            writeint32(f,4)
            f.write(b'DX10')
            f.write(b'\x00' * 0x14)
            writeint32(f,4198408)
            f.write(b'\x00' * 0x10)
            writeint32(f,self.format_num)
            writeint32(f,3)
            writeint32(f,0)
            writeint32(f,1)
            writeint32(f,1)
            f.write(self.data)
            if self.platform == 'Switch':
                f.write(b'\x00' * (self.mipmap_header_list[0].effective_data_size - self.mipmap_header_list[0].data_size ))
        if self.format in ["BC1_UNORM","BC7_UNORM"]:
            check_call(['texconv','-y','-o',output_dir,'-ft','png',dds_filepath],stdout = DEVNULL)
            if self.platform == 'Switch':
                png_filepath = dds_filepath[:-3] + 'png'
                swizzled_im = Image.open(png_filepath)
                im = ImageDeswizzle(swizzled_im,self.format)
                im = im.deswizzle(self.width,self.height)
                im.save(png_filepath)
            os.remove(dds_filepath)
        else:
            print(f"Ignoring {self.filename}, format {self.format} isn't supported")

    def convert_RGBA_to_png(self,output_dir):
        png_filepath = os.path.join(output_dir,self.filename + '.png')
        extended_width, extended_height = self.width,self.height
        if self.platform == 'Switch':
            if self.height % 128 != 0:
                extended_height = ((self.height // 128) + 1) * 128
            if self.width % 16 != 0:
                extended_width = ((self.width // 16) + 1) * 16
            self.data += b'\x00' * (self.mipmap_header_list[0].effective_data_size - self.mipmap_header_list[0].data_size)
        im = Image.frombytes('RGBA',(extended_width,extended_height),self.data)
        if self.platform == 'Switch':
            swizzled_im = ImageDeswizzle(im,self.format)
            deswizzled_im = swizzled_im.deswizzle(self.width,self.height)
            deswizzled_im.save(png_filepath)
        else:
            im.save(png_filepath)

    def import_png_switch(self,png_path,patch_root_dir): #extremely unefficient way to convert and swizzle images, but since I need to rely on an external exe to convert png to dds...
        gamepath = os.path.join(self.filepath.replace(patch_root_dir + '\\',''))
        unswizzled_im = Image.open(png_path)
        if unswizzled_im.size[0] != self.width: #Steam images can be larger than Switch images (black stripes)
            unswizzled_im = unswizzled_im.crop((0,0,self.width,self.height))
        im = ImageSwizzle(unswizzled_im,self.format)
        swizzled_im = im.swizzle()
        png_swizzled_path = png_path + '_swizzled.png'
        swizzled_im.save(png_swizzled_path)
        if self.format in ["BC1_UNORM","BC7_UNORM"]:
            dds_swizzled_path = png_path + '_swizzled.dds'
            check_call(['texconv','-srgb','-ft','dds','-y','-f',self.format,'-m','1','-o',os.path.dirname(png_swizzled_path),png_swizzled_path],stdout = DEVNULL)
            ddsf = DDS(dds_swizzled_path)
            self.data = ddsf.data
            data_size = ddsf.pitch
            for i in range(self.mipmap_count - 1): #adding mipmaps manually because they need to be swizzled separately.
                im = Image.open(png_path)
                downsized_im = im.reduce(2*(i+1))
                im = ImageSwizzle(downsized_im,self.format)
                swizzled_downsized_im = im.swizzle()
                pnglittle_swizzled_path = png_path[:-3] + f'little.png' + '_swizzled.png'
                swizzled_downsized_im.save(pnglittle_swizzled_path)
                ddslittle_swizzled_path = png_path[:-3] + f'little.png' + '_swizzled.dds'
                check_call(['texconv','-ft','dds','-y','-srgb','-f',self.format,'-m','1','-o',os.path.dirname(pnglittle_swizzled_path),pnglittle_swizzled_path],stdout = DEVNULL)
                little_dds = DDS(ddslittle_swizzled_path)
                self.data += little_dds.data
                os.remove(pnglittle_swizzled_path)
                os.remove(ddslittle_swizzled_path)
            for i in range(self.mipmap_count):
                self.mipmap_header_list[i].data_size = data_size // (4**i)
                self.mipmap_header_list[i].effective_data_size = data_size // (4**i)
                if i > 0:
                    self.mipmap_header_list[i].data_offset = self.mipmap_header_list[i-1].data_offset + self.mipmap_header_list[i-1].effective_data_size
            os.remove(dds_swizzled_path)
        elif self.format == 'RGBA8888_UNORM': #no support of RGBA images with mipmaps, as they are not a thing in AJT
            im = Image.open(png_swizzled_path)
            rgba = list(im.getdata())
            new_data = bytearray()
            for pix in rgba:
                for value in pix:
                    new_data += value.to_bytes(1)
            self.data = new_data
        os.remove(png_swizzled_path)

    def import_png_steam(self,png_path,patch_root_dir):
        gamepath = os.path.join(self.filepath.replace(os.path.join(patch_root_dir,''),''))
        if self.format in ['BC1_UNORM','BC7_UNORM']: #converting to DDS by calling texconv
            dds_path = png_path[:-3] + 'dds'
            check_call(['texconv','-ft','dds','-y','-srgb','-f',self.format,'-m',str(self.mipmap_count),'-o',os.path.dirname(png_path),png_path],stdout = DEVNULL)
            ddsf = DDS(dds_path)
            self.data = ddsf.data
            os.remove(dds_path)
        elif self.format == "RGBA8888_UNORM": #simple RGBA conversion from im data
            im = Image.open(png_path)
            rgba = list(im.getdata())
            new_data = bytearray()
            for pix in rgba:
                for value in pix:
                    new_data += value.to_bytes(1)
            self.data = new_data
        else:
            return None


    def update(self):
        stream = self.magic + self.version.to_bytes(4,'little') + self.width.to_bytes(2,'little') + self.height.to_bytes(2,'little') + self.unknown + self.img_count.to_bytes(1) + (self.mipmap_count * 16).to_bytes(1) + self.format_num.to_bytes(4,'little') + self.flags
        for mipmap_header in self.mipmap_header_list:
            stream += mipmap_header.tobytes()
        stream += self.data
        with open(self.filepath,mode='wb') as f:
            f.write(stream)

class SteamMipmapHeader:
    def __init__(self,f):
        self.data_offset = readint32(f)
        self.padding = readint32(f)
        self.pitch = readint32(f)
        self.data_size = readint32(f)

    def tobytes(self):
        return self.data_offset.to_bytes(4,'little') + self.padding.to_bytes(4,'little') + self.pitch.to_bytes(4,'little') + self.data_size.to_bytes(4,'little')

class SwitchMipmapHeader:
    def __init__(self,f):
        self.data_offset = readint32(f)
        self.padding = readint32(f)
        self.data_size = readint32(f)
        self.effective_data_size = readint32(f) #I think the textures are padded with black pixels to reach this effective data size
    def tobytes(self):
        return self.data_offset.to_bytes(4,'little') + self.padding.to_bytes(4,'little') + self.data_size.to_bytes(4,'little') + self.effective_data_size.to_bytes(4,'little')

def islocalizedtex(path,ext):
    if ext in ['en','fr','de']: #literally useful for one file... Yeah
        region = 'europe'
    else:
        region = 'asia'
    file, dir = os.path.basename(path), os.path.dirname(path)
    if (f'.tex.719230324.{ext}' in file) or (f'_{ext}_' in file and '.tex.719230324' in file) or ((region in file) and '.tex.719230324' in file):
        return True
    elif file.endswith('.tex.719230324'):
        if not os.path.isfile(path + f'.{ext}'):
            for lang_ext in ['ja','en','de','fr','ko','zhcn','zhtw']:
                if os.path.isfile(path + f'.{lang_ext}'):
                    return True
            return False
    else:
        return False



def batch_tex_to_png(extracted_root_dir,platform,ext):
    print('\n\n--- EXPORTING TEXTURES ---\n\n')
    if platform == 'Steam':
        plat_code = 'stm'
    elif platform == 'Switch':
        plat_code = 'nsw'
    root = os.path.join(extracted_root_dir,'natives',plat_code)
    for path, subdirs,files in os.walk(root):
        for file in files:
            truepath = os.path.join(path,file)
            if islocalizedtex(truepath,ext):
                try:
                    os.makedirs(path.replace(root,'png'))
                except:
                    pass
                try:
                    print(f'Exporting {truepath}...')
                    tex = AJTTex(truepath,platform)
                    if tex.format != 'RGBA8888_UNORM':
                        tex.convert_BC_to_png(path.replace(root,'png'))
                        fix_png = Image.open(os.path.join(path.replace(root,'png'),file + '.png'))
                        fix_png.save(os.path.join(path.replace(root,'png'),file + '.png')) #fixing texconv exporting pngs that are shown lighter by some softwares, for some reason
                    else:
                        tex.convert_RGBA_to_png(path.replace(root,'png'))
                except:
                    print(f'An error occured while exporting {truepath}')


def batch_import_png_switch(extracted_root_dir,patch_root_dir,ext):
    for path, _, files in os.walk('png'):
        for file in files:
            truepath = os.path.join(path,file)
            if '_swizzled' in file or '.little' in file:
                os.remove(truepath)
            elif file.endswith('.png'):
                print(f'Importing {truepath}...')
                texpath = os.path.join(patch_root_dir,'natives','nsw',truepath[:-4].replace(os.path.join('png',''),''))
                if not os.path.isfile(texpath):
                    if not os.path.isdir(os.path.dirname(texpath)):
                        os.makedirs(os.path.dirname(texpath))
                    shutil.copy(texpath.replace(patch_root_dir,extracted_root_dir),texpath)
                try:
                    tex = AJTTex(texpath,'Switch')
                    tex.import_png_switch(truepath,patch_root_dir)
                    tex.update()
                except:
                    print(f'Error while importing {truepath}')

def batch_import_png_steam(extracted_root_dir,patch_root_dir,ext):
    for path, _, files in os.walk('png'):
        for file in files:
            truepath = os.path.join(path,file)
            if '_swizzled' in file or '.little' in file:
                os.remove(truepath)
                continue
            elif file.endswith('.png'):
                print(f'Importing {truepath}...')
                texpath = os.path.join(patch_root_dir,'natives','stm',truepath[:-4].replace(os.path.join('png',''),''))
                if not os.path.isfile(texpath):
                    if not os.path.isdir(os.path.dirname(texpath)):
                        os.makedirs(os.path.dirname(texpath))
                    shutil.copy(texpath.replace(patch_root_dir,extracted_root_dir),texpath)
                try:
                    tex = AJTTex(texpath,'Steam')
                    tex.import_png_steam(truepath,patch_root_dir)
                    tex.update()
                except:
                    print(f'Error while importing {truepath}')
