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
    bits_per_pixel = None #number of bits used to encode 1 pixel
    bytes_per_block = None #number of bytes used to encode 1 block of pixel. For example, this block is 4x4 pixels for BC encodings, and it's 1x1 (a single pixel) for encodings that don't use block compression, etc.
    type = 'dds'
    name = None
    pitch_type = None #see --> https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide
    id = None #RE texture id. Should match DDS id.
    block_size = None #block compression size. = (4,4) for BC encodings, (1,1) for encodings that don't use block compression, etc.

    def to_png(self,dds_filepath,png_filepath):
        check_call([texconv,'-y','-o',os.path.dirname(png_filepath),'-ft','png',dds_filepath],stdout = DEVNULL)
        with Image.open(png_filepath) as im:
            im.save(png_filepath)

    def from_png(self,png_filepath,dds_filepath):
        check_call([texconv,'-ft','dds','-y','-srgb','-dx10','-f',self.name,'-m','1','-o',os.path.dirname(dds_filepath),png_filepath],stdout = DEVNULL)

class R8G8B8A8_UNORM(DDSEncoding): #texconv don't work for R8G8B8A8, no idea why
    bits_per_pixel = 32
    bytes_per_block = 4
    name = 'R8G8B8A8_UNORM'
    pitch_type = 2
    id = 0x1c
    block_size = (1,1)

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
    bits_per_pixel = 4
    bytes_per_block = 8
    name = 'BC1_UNORM'
    pitch_type = 1
    id = 0x47
    block_size = (4,4)


class BC2_UNORM(DDSEncoding):
    bits_per_pixel = 8
    bytes_per_block = 16
    name = 'BC2_UNORM'
    pitch_type = 1
    id = 0x4a
    block_size = (4,4)

class BC3_UNORM(DDSEncoding):
    bits_per_pixel = 8
    bytes_per_block = 16
    name = 'BC3_UNORM'
    pitch_type = 1
    id = 0x4d
    block_size = (4,4)

class BC4_UNORM(DDSEncoding):
    bits_per_pixel = 4
    bytes_per_block = 8
    name = 'BC4_UNORM'
    pitch_type = 1
    id = 0x50
    block_size = (4,4)

class BC5_UNORM(DDSEncoding):
    bits_per_pixel = 8
    bytes_per_block = 16
    name = 'BC5_UNORM'
    pitch_type = 1
    id = 0x53
    block_size = (4,4)

class BC6H_UF16(DDSEncoding):
    bits_per_pixel = 8
    bytes_per_block = 16
    name = 'BC6H_UF16'
    pitch_type = 1
    id = 0x5f
    block_size = (4,4)


class BC7_UNORM(DDSEncoding):
    bits_per_pixel = 8
    bytes_per_block = 16
    name = 'BC7_UNORM'
    pitch_type = 1
    id = 0x62
    block_size = (4,4)