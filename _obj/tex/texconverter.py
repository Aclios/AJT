import os
import shutil
from PIL import Image
from subprocess import DEVNULL, STDOUT, check_call
from _obj.tex.switch_swizzle import *
from _obj.tex.ps4_swizzle import *
from _obj.tex.format_enum import *
import traceback
from _obj.utils.utils import *

platform_dict = {
1:'nsw',
0xd:'ps4',
0xffffffff:'stm'
}


class UnimplementedFormatError(Exception):
    def __init__(self,message):
        super().__init__(message)


class RETex:
    def __init__(self,tex_filepath):
        with open(tex_filepath,mode='rb') as f:
            self.filepath = tex_filepath
            self.filename = os.path.basename(tex_filepath)
            self.magic = f.read(4)
            if self.magic != b'TEX\x00':
                raise Exception("Error: the file isn't a valid TEX file (bad magic)")
            self.version = readint32(f)
            self.width = readint16(f)
            self.height = readint16(f)
            self.unknown = f.read(2) #always \x01\x00 (?)
            self.img_count = readint8(f) # = 1
            self.mipmap_count = readint8(f) // 16
            self.format_id = readint32(f)
            try:
                self.format = format_dict[self.format_id]
            except KeyError:
                raise UnimplementedFormatError(f'Error: the format {format_dict_completed[self.format_id]} is not implemented yet')
            self.platform_id = readint32(f)
            self.platform = platform_dict[self.platform_id]
            self.flags = f.read(8)
            self.swizzle_depth = readint32(f) #only used by for switch textures
            self.nsw_flags = f.read(4) #flags related to switch swizzling, not sure what they do though
            self.mipmap_header_list = []
            for _ in range(self.mipmap_count):
                if self.platform == 'nsw':
                    self.mipmap_header_list.append(NswMipmapHeader(f))
                else: #PS4 & Steam
                    self.mipmap_header_list.append(StmPS4MipmapHeader(f))
            f.seek(self.mipmap_header_list[0].data_offset)
            self.data_size = self.mipmap_header_list[0].data_size
            self.data = f.read() #you can't read only the data_size because PS4 data_size is a lie
            if self.platform == 'nsw':
                self.data_size = self.mipmap_header_list[0].real_data_size
                self.data += b'\x00' * (self.mipmap_header_list[0].real_data_size - self.mipmap_header_list[0].data_size) #nsw swizzled textures are probably padded in RAM
                self.max_width_tile = self.format.nsw_unswizzle_list[-1][0]
                self.max_height_tile = self.format.nsw_unswizzle_list[-1][1] * (2 ** self.swizzle_depth)
            elif self.platform == 'ps4':
                self.max_width_tile = self.format.ps4_unswizzle_list[-1][0]
                self.max_height_tile = self.format.ps4_unswizzle_list[-1][1]
            else: #Steam. PS4 also has this pitch but since the textures are swizzled, it seems the pitch is useless
                self.width = self.compute_width_from_pitch()
            self.swizzle_width = self.width
            self.swizzle_height = self.height
            if self.platform in ['nsw','ps4']: #taking account to the fact that swizzled textures are "bigger"
                if self.width % self.max_width_tile != 0:
                     self.swizzle_width = ((self.width // self.max_width_tile) + 1) * self.max_width_tile
                if self.height % self.max_height_tile != 0:
                     self.swizzle_height = ((self.height // self.max_height_tile) + 1) * self.max_height_tile


    def compute_width_from_pitch(self): #if the texture isn't swizzled, it's possible that the texture is wider than possible. It's possible to compute the real width from the "pitch"
        if self.format.pitch_type == 1: #BC textures
            return int(((4 * self.mipmap_header_list[0].pitch) / self.format.bpb))
        elif self.format.pitch_type == 2: #R8G8_B8G8, G8R8_G8B8, legacy UYVY-packed, and legacy YUY2-packed formats
            return int(self.mipmap_header_list[0].pitch / 4)
        elif self.format.pitch_type == 3:#other formats
            return int(self.mipmap_header_list[0].pitch * 8 / self.format.bpp)

    def write_to_dds(self,dds_filepath):
        with open(dds_filepath,mode='wb') as f:
            f.write(b'DDS ')
            writeint32(f,124)
            writeint32(f,659463)
            writeint32(f,self.swizzle_height)
            writeint32(f,self.swizzle_width)
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
            writeint32(f,self.format_id)
            writeint32(f,3)
            writeint32(f,0)
            writeint32(f,1)
            writeint32(f,1)
            f.write(self.data)

    def write_to_astc(self,astc_filepath):
        with open(astc_filepath,mode='wb') as f:
            f.write(b'\x13\xab\xa1\x5c')
            writeint8(f,self.format.block_size[0])
            writeint8(f,self.format.block_size[1])
            writeint8(f,1) #this value might be the color space ???
            writeint24(f,self.swizzle_width)
            writeint24(f,self.swizzle_height)
            writeint24(f,1) # ????
            f.write(self.data)

    def import_dds_data(self,dds_filepath):
        with open(dds_filepath,mode='rb') as f:
            f.seek(0x94)
            data = f.read()
        return data

    def import_astc_data(self,astc_filepath):
        with open(astc_filepath,mode='rb') as f:
            f.seek(0x10)
            data = f.read()
        return data


    def export_to_png(self,png_filepath):
        try:
            os.mkdir('temp')
        except:
            pass
        if self.format.type == 'dds':
            ext = '.dds'
            exportfunc = self.write_to_dds
        elif self.format.type == 'astc':
            ext = '.astc'
            exportfunc = self.write_to_astc

        spec_filepath = os.path.join('temp',self.filename + ext)
        exportfunc(spec_filepath)

        if self.platform == 'nsw':
            temp_png_filepath = os.path.join('temp',os.path.basename(png_filepath))
            self.format.to_png(spec_filepath,temp_png_filepath)
            with Image.open(temp_png_filepath) as im:
                deswizzle = NswImageDeswizzle(im,self.format,self.swizzle_depth)
                deswizzled_im = deswizzle.deswizzle(self.width,self.height)
                deswizzled_im.save(png_filepath)
            try:
                os.remove(spec_filepath)
                os.remove(temp_png_filepath)
            except:
                pass

        elif self.platform == 'ps4':
            temp_png_filepath = os.path.join('temp',os.path.basename(png_filepath))
            self.format.to_png(spec_filepath,temp_png_filepath)
            with Image.open(temp_png_filepath) as im:
                deswizzle = PS4ImageDeswizzle(im,self.format)
                deswizzled_im = deswizzle.deswizzle(self.width,self.height)
                deswizzled_im.save(png_filepath)
            try:
                os.remove(spec_filepath)
                os.remove(temp_png_filepath)
            except:
                pass

        else:
            self.format.to_png(spec_filepath,png_filepath)
            try:
                os.remove(spec_filepath)
            except:
                pass


    def import_from_png(self,png_filepath,patch_root_dir):

        if self.format.type == 'dds':
            ext = '.dds'
            importfunc = self.import_dds_data
        elif self.format.type == 'astc':
            ext = '.astc'
            importfunc = self.import_astc_data

        spec_filepath = os.path.join('temp',self.filename + ext)

        if self.platform == 'nsw':
            with Image.open(png_filepath) as im:
                swizzle = NswImageSwizzle(im,self.format,self.swizzle_depth)
                self.width = im.size[0]
                self.height = im.size[1]
                swizzled_im = swizzle.swizzle()
            temp_png_filepath = os.path.join('temp',os.path.basename(png_filepath))
            swizzled_im.save(temp_png_filepath)
            self.format.from_png(temp_png_filepath,spec_filepath)
            self.data = importfunc(spec_filepath)
            data_size = len(self.data)
            for i in range(self.mipmap_count - 1):
                with Image.open(png_filepath) as im:
                    mipmap_im = im.reduce(2*(i+1))
                    mipmap_max_height_tile = self.max_height_tile
                    mipmap_swizzle_depth = self.swizzle_depth
                    while mipmap_max_height_tile > im.height:
                        mipmap_max_height_tile = mipmap_max_height_tile // 2
                        mipmap_swizzle_depth -= 1
                    swizzle = NswImageSwizzle(mipmap_im,self.format,self.swizzle_depth - 1 - i)
                    swizzled_im = swizzle.swizzle()
                temp_png_filepath = os.path.join('temp',os.path.basename(png_filepath))
                swizzled_im.save(temp_png_filepath)
                self.format.from_png(temp_png_filepath,spec_filepath)
                self.data += importfunc(spec_filepath)
            for i in range(self.mipmap_count):
                self.mipmap_header_list[i].data_size = data_size // (4**i)
                self.mipmap_header_list[i].real_data_size = data_size // (4**i)
                if i > 0:
                    self.mipmap_header_list[i].data_offset = self.mipmap_header_list[i-1].data_offset + self.mipmap_header_list[i-1].real_data_size

            try:
                os.remove(spec_filepath)
                os.remove(temp_png_filepath)
            except:
                pass


        elif self.platform == 'ps4':
            with Image.open(png_filepath) as im:
                swizzle = PS4ImageSwizzle(im,self.format)
                self.width = im.size[0]
                self.height = im.size[1]
                swizzled_im = swizzle.swizzle()
            temp_png_filepath = os.path.join('temp',os.path.basename(png_filepath))
            swizzled_im.save(temp_png_filepath)
            self.format.from_png(temp_png_filepath,spec_filepath)
            self.data = importfunc(spec_filepath)
            data_size = len(self.data)
            for i in range(self.mipmap_count - 1):
                with Image.open(png_filepath) as im:
                    mipmap_im = im.reduce(2*(i+1))
                    swizzle = PS4ImageSwizzle(mipmap_im,self.format)
                    swizzled_im = swizzle.swizzle()
                temp_png_filepath = os.path.join('temp',os.path.basename(png_filepath))
                swizzled_im.save(temp_png_filepath)
                self.format.from_png(temp_png_filepath,spec_filepath)
                self.data += importfunc(spec_filepath)
            for i in range(self.mipmap_count):
                self.mipmap_header_list[i].data_size = data_size // (4**i)
                if i > 0:
                    self.mipmap_header_list[i].data_offset = self.mipmap_header_list[i-1].data_offset + self.mipmap_header_list[i-1].data_size
            try:
                os.remove(spec_filepath)
                os.remove(temp_png_filepath)
            except:
                pass


        else: #Steam
            with Image.open(png_filepath) as im:
                self.width = im.size[0]
                self.height = im.size[1]
            self.format.from_png(png_filepath,spec_filepath)
            self.data = importfunc(spec_filepath)
            data_size = len(self.data)
            for i in range(self.mipmap_count - 1):
                with Image.open(png_filepath) as im:
                    mipmap_im = im.reduce(2*(i+1))
                mipmap_path = os.path.join('temp',self.filename + '.png')
                mipmap_im.save(mipmap_path)
                self.format.from_png(mipmap_path,spec_filepath)
                self.data += importfunc(spec_filepath)
            for i in range(self.mipmap_count):
                self.mipmap_header_list[i].data_size = data_size // (4**i)
                if i > 0:
                    self.mipmap_header_list[i].data_offset = self.mipmap_header_list[i-1].data_offset + self.mipmap_header_list[i-1].data_size
            try:
                os.remove(spec_filepath)
                os.remove(mipmap_path)
            except:
                pass

        self.update()

    def update(self):
        stream = self.magic + self.version.to_bytes(4,'little') + self.width.to_bytes(2,'little') + self.height.to_bytes(2,'little') + self.unknown + self.img_count.to_bytes(1) + (self.mipmap_count * 16).to_bytes(1) + self.format_id.to_bytes(4,'little') + self.platform_id.to_bytes(4,'little') + self.flags + self.swizzle_depth.to_bytes(4,'little') + self.nsw_flags
        for mipmap_header in self.mipmap_header_list:
            stream += mipmap_header.tobytes()
        stream += self.data
        with open(self.filepath,mode='wb') as f:
            f.write(stream)

class StmPS4MipmapHeader:
    def __init__(self,f):
        self.data_offset = readint32(f)
        self.padding = readint32(f)
        self.pitch = readint32(f)
        self.data_size = readint32(f)

    def tobytes(self):
        return self.data_offset.to_bytes(4,'little') + self.padding.to_bytes(4,'little') + self.pitch.to_bytes(4,'little') + self.data_size.to_bytes(4,'little')

class NswMipmapHeader:
    def __init__(self,f):
        self.data_offset = readint32(f)
        self.padding = readint32(f)
        self.data_size = readint32(f)
        self.real_data_size = readint32(f) #The textures are padded with \x00 bytes on memory to reach this "real" data size

    def tobytes(self):
        return self.data_offset.to_bytes(4,'little') + self.padding.to_bytes(4,'little') + self.data_size.to_bytes(4,'little') + self.real_data_size.to_bytes(4,'little')

def islocalizedtex(path,ext):
    file, dir = os.path.basename(path), os.path.dirname(path)
    if ext == 'all' and ".tex" in path:
        return True
    if ext in ['en','fr','de']: #literally useful for one file... Yeah
        region = 'europe'
    else:
        region = 'asia'
    if (f'.tex' in file and file.endswith(ext)) or (f'_{ext}_' in file and '.tex' in file) or ((region in file) and '.tex' in file):
        return True
    elif file.endswith('.tex'):
        if not os.path.isfile(path + f'.{ext}'):
            for lang_ext in ['ja','en','de','fr','ko','zhcn','zhtw']:
                if os.path.isfile(path + f'.{lang_ext}'):
                    return True
            return False
    else:
        return False



def batch_export_tex(PLATFORM):
    print('\n\n--- EXPORTING TEXTURES ---\n\n')
    try:
        os.mkdir('temp')
    except:
        pass
    extracted_root_dir = PLATFORM.pak_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
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
                    tex = RETex(truepath)
                    png_filepath = os.path.join(path.replace(root,'png'),file + '.png')
                    tex.export_to_png(png_filepath)
                    fix_png = Image.open(png_filepath)
                    fix_png.save(png_filepath) #fixing texconv exporting pngs that are shown lighter by some softwares, for some reason
                except:
                    traceback.print_exc()
    shutil.rmtree('temp')

def batch_import_tex(PLATFORM):
    print('\n\n--- IMPORTING TEXTURES ---\n\n')
    try:
        os.mkdir('temp')
    except:
        pass
    extracted_root_dir = PLATFORM.pak_path
    patch_root_dir = PLATFORM.patch_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
    for path, _, files in os.walk('png'):
        for file in files:
            truepath = os.path.join(path,file)
            if file.endswith('.png'):
                print(f'Importing {truepath}...')
                texpath = os.path.join(patch_root_dir,'natives',plat_code,truepath[:-4].replace(os.path.join('png',''),''))
                if not os.path.isfile(texpath):
                    if not os.path.isdir(os.path.dirname(texpath)):
                        os.makedirs(os.path.dirname(texpath))
                    try:
                        shutil.copy(texpath.replace(patch_root_dir,extracted_root_dir),texpath)
                    except:
                        pass
                try:
                    tex = RETex(texpath)
                    tex.import_from_png(truepath,patch_root_dir)
                except:
                    traceback.print_exc()
    shutil.rmtree('temp')
