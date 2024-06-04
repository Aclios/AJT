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
    name = None
    pitch_type = 3
    id = None
    block_size = None
    nsw_unswizzle_list = None
    nsw_swizzle_list = None
    ps4_unswizzle_list = None
    ps4_swizzle_list = None

    def to_png(self,astc_filepath,png_filepath):
        check_call([astcenc,'-dl',astc_filepath,png_filepath],stdout = DEVNULL)

    def from_png(self,png_filepath,astc_filepath):
        check_call([astcenc,'-cl',png_filepath,astc_filepath,f'{block_size[0]}x{block_size[1]}','-thorough'],stdout = DEVNULL)

class ASTC_6x6_UNORM(ASTCEncoding):
    name = "ASTC_6x6_UNORM"
    id = 0x040e
    block_size = (6,6)
    nsw_unswizzle_list = [[12,12,True],[24,48,True],[24,48,True]]
    nsw_swizzle_list = [[24,48,False],[24,48,True],[12,12,True],[6,6,True]]
    ps4_unswizzle_list = [[12,12,False],[24,24,False],[48,48,False]]
    ps4_swizzle_list = [[48,48,False],[24,24,False],[12,12,False],[6,6,False]]

