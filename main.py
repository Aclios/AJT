import os
import sys
import shutil
from subprocess import DEVNULL, STDOUT, check_call

from _obj.msg.msgconverter import *
from _obj.script.scriptconverter import *
from _obj.sound.asrcconverter import *
from _obj.tex.texconverter import *
import _obj.platform

def main():
    args = sys.argv
    existing_dirs = os.listdir()
    if '-stm' in args:
        PLATFORM = _obj.platform.Steam
    elif '-nsw' in args:
        PLATFORM = _obj.platform.Switch
    elif '-ps4' in args:
        PLATFORM = _obj.platform.PS4
    else:
        print('Error: no platform have been specified')
        return

    if '-e' in args:
        if 'png' in existing_dirs or 'script' in existing_dirs or 'msg' in existing_dirs or 'sound' in existing_dirs:
            print('Error: one or several extracted folders already exist. Delete or move them if you want to extract the files once again.')
            return

        if '-png' in args:
            batch_export_tex(PLATFORM)
        if '-script' in args:
            batch_export_script(PLATFORM)
        if '-msg' in args:
            batch_export_msg(PLATFORM)
        if '-sound' in args:
            batch_export_asrc(PLATFORM)

    elif '-a' in args:
        if '-png' in args:
            batch_import_tex(PLATFORM)
        if '-script' in args:
            batch_import_script(PLATFORM)
        if '-msg' in args:
            batch_import_msg(PLATFORM)
        if '-sound' in args:
            batch_import_asrc(PLATFORM)

        print('\n\n-- Building .pak --\n\n')
        retool = os.path.join('_obj','exttools','retool','retool')
        try:#retool return an error after building pak
            check_call([retool,'-c',PLATFORM.patch_path])
        except:
            shutil.move(os.path.join(os.path.dirname(PLATFORM.patch_path),os.path.basename(PLATFORM.patch_path) + '.pak'),os.path.join(PLATFORM.mod_dir,'re_chunk_000.pak.patch_001.pak'))

if __name__ == '__main__':
    main()
