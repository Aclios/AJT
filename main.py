import os
import sys
import shutil
from subprocess import DEVNULL, STDOUT, check_call

from _obj.msg.msg22converter import *
from _obj.script.user2converter import *
from _obj.sound.asrc31converter import *
from _obj.tex.texconverter import *


path_L = []

with open('path_init.txt','rb') as f:
    lines = f.readlines()
    for line in lines:
        try:
            path_data = line.replace(b'\n',b'').replace(b'\r',b'').replace(b'"',b'').split(b'=')
            path_L.append(path_data[1].decode())
        except:
            raise Exception(f"Can't load line {line} from path_init.txt, invalid syntax")

STEAM_PAK_PATH, SWITCH_PAK_PATH, STEAM_PATCH_PATH, SWITCH_PATCH_PATH, EXTENSION, STEAM_MOD_DIR, SWITCH_MOD_DIR = path_L

if EXTENSION not in ['ja','fr','en','de','zhcn','zhtw','ko']:
    raise Exception("Extension must have one of the following values: ['ja','fr','en','de','ko','zhcn','zhtw']")

def main():
    args = sys.argv
    existing_dirs = os.listdir(os.getcwd())
    if '-e' in args:
        if '-png' in args:
            if 'png' in existing_dirs:
                raise Exception('"png" folder already exists, so the process was stopped as a safety measure. Remove it if you really want to extract the files.')
            if '-stm' in args:
                batch_tex_to_png(STEAM_PAK_PATH,'Steam',EXTENSION)
            elif '-nsw' in args:
                batch_tex_to_png(SWITCH_PAK_PATH,'Switch',EXTENSION)
        if '-script' in args:
            if 'script' in existing_dirs:
                raise Exception('"script" folder already exists, so the process was stopped as a safety measure. Remove it if you really want to extract the files.')
            if '-stm' in args:
                batch_export_user2(STEAM_PAK_PATH,'Steam',EXTENSION)
            elif '-nsw' in args:
                batch_export_user2(SWITCH_PAK_PATH,'Switch',EXTENSION)
        if '-msg' in args:
            if 'msg' in existing_dirs:
                raise Exception('"msg" folder already exists, so the process was stopped as a safety measure. Remove it if you really want to extract the files.')
            if '-stm' in args:
                batch_export_msg2(STEAM_PAK_PATH,'Steam',EXTENSION)
            elif '-nsw' in args:
                batch_export_msg2(SWITCH_PAK_PATH,'Switch',EXTENSION)
        if '-sound' in args:
            if 'sound' in existing_dirs:
                raise Exception('"sound" folder already exists, so the process was stopped as a safety measure. Remove it if you really want to extract the files.')
            if '-stm' in args:
                batch_export_srcd(STEAM_PAK_PATH,'Steam',EXTENSION)
            elif '-nsw' in args:
                batch_export_srcd(SWITCH_PAK_PATH,'Switch',EXTENSION)

    elif '-a' in args:
        if '-png' in args:
            if '-stm' in args:
                batch_import_png_steam(STEAM_PAK_PATH,STEAM_PATCH_PATH,EXTENSION)
            elif '-nsw' in args:
                batch_import_png_switch(SWITCH_PAK_PATH,SWITCH_PATCH_PATH,EXTENSION)
        if '-script' in args:
            if '-stm' in args:
                batch_import_user2(STEAM_PATCH_PATH,'Steam',EXTENSION)
            elif '-nsw' in args:
                batch_import_user2(SWITCH_PATCH_PATH,'Switch',EXTENSION)
        if '-msg' in args:
            if '-stm' in args:
                batch_import_msg2(STEAM_PAK_PATH,STEAM_PATCH_PATH,'Steam',EXTENSION)
            elif '-nsw' in args:
                batch_import_msg2(SWITCH_PAK_PATH,SWITCH_PATCH_PATH,'Switch',EXTENSION)
        if '-sound' in args:
            if '-stm' in args:
                batch_import_srcd(STEAM_PAK_PATH,STEAM_PATCH_PATH,'Steam',EXTENSION)
            elif '-nsw' in args:
                batch_import_srcd(SWITCH_PAK_PATH,SWITCH_PATCH_PATH,'Switch',EXTENSION)
        print('\n\n-- Building .pak --\n\n')
        if '-stm' in args:
            try:#retool return an error after building pak
                check_call(['retool','-c',STEAM_PATCH_PATH])
            except:
                shutil.move(os.path.join(os.path.dirname(STEAM_PATCH_PATH),os.path.basename(STEAM_PATCH_PATH) + '.pak'),os.path.join(STEAM_MOD_DIR,'re_chunk_000.pak.patch_001.pak'))
        elif '-nsw' in args:
            try: #retool return an error after building pak
                check_call(['retool','-c',SWITCH_PATCH_PATH])
            except:
                shutil.move(os.path.join(os.path.dirname(SWITCH_PATCH_PATH),os.path.basename(SWITCH_PATCH_PATH) + '.pak'),os.path.join(SWITCH_MOD_DIR,'re_chunk_000.pak.patch_001.pak'))

main()
