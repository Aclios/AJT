from subprocess import DEVNULL, STDOUT, check_call
from PIL import Image
import os
from _obj.utils.utils import *
astcenc = os.path.join('_obj','exttools','astcenc','astcenc')

def read_astc_data(filepath):
    with open(filepath,mode='rb') as f:
        magic = f.read(4)
        if magic != b'\x13\xab\xa1\x5c':
            raise Exception("Error: the file isn't a valid ASTC file (bad magic)")
        f.seek(8)
        height = readint24(f)
        width = readint24(f)
        f.seek(0x10)
        data = f.read()
    return width, height, data

class ASTCEncoding:
    type = 'astc'
    bytes_per_block = None #number of bytes used to encode 1 block of pixel. This block is 6x6 pixels for ASTC_6x6, 8x6 for ASTC_8x6, etc.
    name = None
    pitch_type = 3
    id = None #RE texture id
    block_size = None #block compression size. = (6,6) for ASTC_6x6, (8,6) for ASTC_8x6, etc.

    def to_png(self,astc_filepath,png_filepath):
        check_call([astcenc,'-dl',astc_filepath,png_filepath],stdout = DEVNULL)

    def from_png(self,png_filepath,astc_filepath):
        check_call([astcenc,'-cl',png_filepath,astc_filepath,f'{block_size[0]}x{block_size[1]}','-thorough'],stdout = DEVNULL)

class ASTC_6x6_UNORM(ASTCEncoding):
    bytes_per_block = 16
    name = "ASTC_6x6_UNORM"
    id = 0x040e
    block_size = (6,6)

