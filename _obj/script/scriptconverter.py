import os
import shutil
from _obj.script.AJT.aa4scriptconverter import *
from _obj.script.AJT.aa56scriptconverter import *


def batch_export_script(PLATFORM):
    extracted_root_dir = PLATFORM.pak_path
    plat_code = PLATFORM.code
    script_dir = os.path.join(extracted_root_dir,'natives',plat_code,'gamedesign','gs4','scriptbinary')
    print('\n\n--- EXPORTING SCRIPT FILES ---\n\n')
    if os.path.isdir(script_dir): #checking if the game is Apollo Justice Trilogy
        batch_export_user2_AA4(PLATFORM)
        batch_export_user2_AA56(PLATFORM)
    else:
        print("This game doesn't have custom script files, or they are not supported yet.")


def batch_import_script(PLATFORM):
    extracted_root_dir = PLATFORM.pak_path
    plat_code = PLATFORM.code
    script_dir = os.path.join(extracted_root_dir,'natives',plat_code,'gamedesign','gs4','scriptbinary')
    print('\n\n--- IMPORTING SCRIPT FILES ---\n\n')
    if os.path.isdir(script_dir): #checking if the game is Apollo Justice Trilogy
        batch_import_user2_AA4(PLATFORM)
        batch_import_user2_AA56(PLATFORM)
    else:
        print("This game doesn't have custom script files, or they are not supported yet.")

