import os
import shutil
from subprocess import DEVNULL, STDOUT, check_call

msg2_dir_names = ['common','gs4','gs5','gs6','museum']


def batch_export_msg2(PLATFORM):
    extracted_root_dir = PLATFORM.pak_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
    print('\n\n--- EXPORTING MSG.22 FILES ---\n\n')
    msg_root_dir = os.path.join(extracted_root_dir,'natives',plat_code,'gamedesign','text')
    for dir in msg2_dir_names:
        try:
            os.makedirs(os.path.join('msg',dir))
        except:
            pass
        msg2_dir = os.path.join(msg_root_dir,dir)
        print(f'Exporting directory {msg2_dir}...')
        check_call(['REMSG_Converter','-i',msg2_dir,'-m','txt','-l',ext],stdout = DEVNULL)
        for file in os.listdir(msg2_dir):
            if file.endswith('txt'):
                try:
                    os.rename(os.path.join(msg2_dir,file),os.path.join('msg',dir,file))
                except:
                    print(f"Can't export to {os.path.join('msg',dir,file)}, file already exists")


def batch_import_msg2(PLATFORM):
    extracted_root_dir = PLATFORM.pak_path
    patch_root_dir = PLATFORM.patch_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
    msg_root_dir = os.path.join(extracted_root_dir,'natives',plat_code,'gamedesign','text')
    patched_msg_root_dir = os.path.join(patch_root_dir,'natives',plat_code,'gamedesign','text')
    for dir in msg2_dir_names:
        msg2_dir = os.path.join(patched_msg_root_dir,dir)
        for file in os.listdir(os.path.join('msg',dir)):
            if file.endswith('.txt'):
                msg2_file = file[:-4]
                print(f'Importing {os.path.join("msg",dir,file)}...')
                if not os.path.isfile(os.path.join(msg2_dir,msg2_file)):
                    try:
                        os.makedirs(msg2_dir)
                    except:
                        pass
                    shutil.copy(os.path.join(msg_root_dir,dir,msg2_file),os.path.join(msg2_dir,msg2_file))
                check_call(['REMSG_Converter','-i',os.path.join(msg2_dir,msg2_file),'-m','txt','-e',os.path.join('msg',dir,file),'-l',ext],stdout = DEVNULL)
                os.replace(os.path.join(msg2_dir,msg2_file + '.new'),os.path.join(msg2_dir,msg2_file))
