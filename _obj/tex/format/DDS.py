from subprocess import DEVNULL, STDOUT, check_call
from PIL import Image
import os
from _obj.utils.utils import *

texconv = os.path.join('_obj','exttools','texconv','texconv')

def read_dds_data(filepath):
    with open(filepath,mode='rb') as f:
        magic = f.read(4)
        if magic != b'DDS ':
            raise Exception("Error: the file isn't a valid DDS file (bad magic)")
        f.seek(12)
        height = readint32(f)
        width = readint32(f)
        f.seek(0x54)
        format = f.read(4)
        if format == b'DX10':
            f.seek(0x94)
            data = f.read()
        else:
            f.seek(0x80)
            data = f.read()
    return width, height, data

def write_to_dds(dds_filepath,width,height,format_id,data):
    with open(dds_filepath,mode='wb') as f:
        f.write(b'DDS ')
        writeint32(f,124)
        writeint32(f,659463)
        writeint32(f,height)
        writeint32(f,width)
        writeint32(f,len(data))
        writeint32(f,1)
        writeint32(f,1)
        f.write(b'\x00' * 0x2c)
        writeint32(f,0x20)
        writeint32(f,4)
        f.write(b'DX10')
        f.write(b'\x00' * 0x14)
        writeint32(f,4198408)
        f.write(b'\x00' * 0x10)
        writeint32(f,format_id)
        writeint32(f,3)
        writeint32(f,0)
        writeint32(f,1)
        writeint32(f,1)
        f.write(data)

class DDSEncoding:
    bpp = None #bytes per pixel
    bpb = None #bytes per block
    type = 'dds'
    name = None
    pitch_type = None
    id = None #texture id
    block_size = None
    nsw_unswizzle_list = None
    nsw_swizzle_list = None
    ps4_unswizzle_list = None
    ps4_swizzle_list = None

    def to_png(self,dds_filepath,png_filepath):
        check_call([texconv,'-y','-o',os.path.dirname(png_filepath),'-ft','png',dds_filepath],stdout = DEVNULL)
        with Image.open(png_filepath) as im:
            im.save(png_filepath)

    def from_png(self,png_filepath,dds_filepath):
        check_call([texconv,'-ft','dds','-y','-srgb','-dx10','-f',self.name,'-m','1','-o',os.path.dirname(dds_filepath),png_filepath],stdout = DEVNULL)

class R8G8B8A8_UNORM(DDSEncoding):
    bpp = 32
    name = 'R8G8B8A8_UNORM'
    pitch_type = 2
    id = 0x1c
    block_size = (1,1)
    nsw_unswizzle_list = [[4,2,False],[8,2,False],[8,8,False],[16,8,False]]
    nsw_swizzle_list = [[16,8,False],[8,8,False],[8,2,False],[4,2,False],[1,1,False]]
    ps4_unswizzle_list = [[2,2,False],[4,4,False],[8,8,False]]
    ps4_swizzle_list = [[8,8,False],[4,4,False],[2,2,False],[1,1,False]]

    def to_png(self,dds_filepath,png_filepath):
        width, height, data = read_dds_data(dds_filepath)
        im = Image.frombytes('RGBA',(width,height),data)
        im.save(png_filepath)

    def from_png(self,png_filepath,dds_filepath):
        with Image.open(png_filepath) as im:
            rgba = list(im.getdata())
            width = im.size[0]
            height = im.size[1]
        new_data = bytearray()
        for pix in rgba:
            for value in pix:
                new_data += value.to_bytes(1,'little')
        write_to_dds(dds_filepath,width,height,0x1c,new_data)

class BC1_UNORM(DDSEncoding):
    bpp = 4
    bpb = 8
    name = 'BC1_UNORM'
    pitch_type = 1
    id = 0x47
    block_size = (4,4)
    nsw_unswizzle_list = [[8,8,False],[16,32,False],[32,32,False]]
    nsw_swizzle_list = [[32,32,False],[16,32,False],[8,8,False],[4,4,False]]
    ps4_unswizzle_list = [[8,8,False],[16,16,False],[32,32,False]]
    ps4_swizzle_list = [[32,32,False],[16,16,False],[8,8,False],[4,4,False]]


class BC2_UNORM(DDSEncoding):
    bpp = 8
    bpb = 16
    name = 'BC2_UNORM'
    pitch_type = 1
    id = 0x4a
    block_size = (4,4)
    nsw_unswizzle_list = [[8,8,True],[16,32,True],[16,32,True]]
    nsw_swizzle_list = [[16,32,False],[16,32,True],[8,8,True],[4,4,True]]
    ps4_unswizzle_list = [[8,8,False],[16,16,False],[32,32,False]]
    ps4_swizzle_list = [[32,32,False],[16,16,False],[8,8,False],[4,4,False]]

class BC3_UNORM(DDSEncoding):
    bpp = 8
    bpb = 16
    name = 'BC3_UNORM'
    pitch_type = 1
    id = 0x4d
    block_size = (4,4)
    nsw_unswizzle_list = [[8,8,True],[16,32,True],[16,32,True]]
    nsw_swizzle_list = [[16,32,False],[16,32,True],[8,8,True],[4,4,True]]
    ps4_unswizzle_list = [[8,8,False],[16,16,False],[32,32,False]]
    ps4_swizzle_list = [[32,32,False],[16,16,False],[8,8,False],[4,4,False]]

class BC4_UNORM(DDSEncoding):
    bpp = 4
    bpb = 8
    name = 'BC4_UNORM'
    pitch_type = 1
    id = 0x50
    block_size = (4,4)
    nsw_unswizzle_list = [[8,8,False],[16,32,False],[32,32,False]]
    nsw_swizzle_list = [[32,32,False],[16,32,False],[8,8,False],[4,4,False]]
    ps4_unswizzle_list = [[8,8,False],[16,16,False],[32,32,False]]
    ps4_swizzle_list = [[32,32,False],[16,16,False],[8,8,False],[4,4,False]]

class BC5_UNORM(DDSEncoding):
    bpp = 8
    bpb = 16
    name = 'BC5_UNORM'
    pitch_type = 1
    id = 0x53
    block_size = (4,4)
    nsw_unswizzle_list = [[8,8,True],[16,32,True],[16,32,True]]
    nsw_swizzle_list = [[16,32,False],[16,32,True],[8,8,True],[4,4,True]]
    ps4_unswizzle_list = [[8,8,False],[16,16,False],[32,32,False]]
    ps4_swizzle_list = [[32,32,False],[16,16,False],[8,8,False],[4,4,False]]

class BC6H_UF16(DDSEncoding):
    bpp = 8
    bpb = 16
    name = 'BC6H_UF16'
    pitch_type = 1
    id = 0x5f
    block_size = (4,4)
    nsw_unswizzle_list = [[8,8,True],[16,32,True],[16,32,True]]
    nsw_swizzle_list = [[16,32,False],[16,32,True],[8,8,True],[4,4,True]]
    ps4_unswizzle_list = [[8,8,False],[16,16,False],[32,32,False]]
    ps4_swizzle_list = [[32,32,False],[16,16,False],[8,8,False],[4,4,False]]



class BC7_UNORM(DDSEncoding):
    bpp = 8
    bpb = 16
    name = 'BC7_UNORM'
    pitch_type = 1
    id = 0x62
    block_size = (4,4)
    nsw_unswizzle_list = [[8,8,True],[16,32,True],[16,32,True]]
    nsw_swizzle_list = [[16,32,False],[16,32,True],[8,8,True],[4,4,True]]
    ps4_unswizzle_list = [[8,8,False],[16,16,False],[32,32,False]]
    ps4_swizzle_list = [[32,32,False],[16,16,False],[8,8,False],[4,4,False]]
