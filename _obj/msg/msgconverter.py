import os
import shutil
from subprocess import DEVNULL, STDOUT, check_call
import traceback

REMSG_Converter = os.path.join('_obj','exttools','REMSG_Converter','REMSG_Converter')

def batch_export_msg(PLATFORM):
    extracted_root_dir = PLATFORM.pak_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
    print('\n\n--- EXPORTING MSG FILES ---\n\n')
    msg_root_dir = os.path.join(extracted_root_dir,'natives',plat_code,'gamedesign','text')
    for dir in os.listdir(msg_root_dir):
        try:
            os.makedirs(os.path.join('msg',dir))
        except:
            pass
        msg_dir = os.path.join(msg_root_dir,dir)
        print(f'Exporting directory {msg_dir}...')
        if ext == 'all':
            check_call([REMSG_Converter,'-i',msg_dir,'-m','csv'],stdout = DEVNULL)
        else:
            check_call([REMSG_Converter,'-i',msg_dir,'-m','txt','-l',ext],stdout = DEVNULL)
        for file in os.listdir(msg_dir):
            if file.endswith('txt') or file.endswith('csv'):
                shutil.move(os.path.join(msg_dir,file),os.path.join('msg',dir,file))


def batch_import_msg(PLATFORM):
    extracted_root_dir = PLATFORM.pak_path
    patch_root_dir = PLATFORM.patch_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
    msg_root_dir = os.path.join(extracted_root_dir,'natives',plat_code,'gamedesign','text')
    patched_msg_root_dir = os.path.join(patch_root_dir,'natives',plat_code,'gamedesign','text')
    print('\n\n--- IMPORTING MSG FILES ---\n\n')
    for dir in os.listdir(msg_root_dir):
        msg_dir = os.path.join(patched_msg_root_dir,dir)
        for file in os.listdir(os.path.join('msg',dir)):
            if file.endswith('.txt'):
                msg_file = file[:-4]
                print(f'Importing {os.path.join("msg",dir,file)}...')
                if not os.path.isfile(os.path.join(msg_dir,msg_file)):
                    try:
                        os.makedirs(msg_dir)
                    except:
                        pass
                    shutil.copy(os.path.join(msg_root_dir,dir,msg_file),os.path.join(msg_dir,msg_file))
                check_call([REMSG_Converter,'-i',os.path.join(msg_dir,msg_file),'-m','txt','-e',os.path.join('msg',dir,file),'-l',ext],stdout = DEVNULL)
                os.replace(os.path.join(msg_dir,msg_file + '.new'),os.path.join(msg_dir,msg_file))
            elif file.endswith('.csv'):
                msg_file = file[:-4]
                print(f'Importing {os.path.join("msg",dir,file)}...')
                if not os.path.isfile(os.path.join(msg_dir,msg_file)):
                    try:
                        os.makedirs(msg_dir)
                    except:
                        pass
                    shutil.copy(os.path.join(msg_root_dir,dir,msg_file),os.path.join(msg_dir,msg_file))
                check_call([REMSG_Converter,'-i',os.path.join(msg_dir,msg_file),'-m','csv','-e',os.path.join('msg',dir,file)],stdout = DEVNULL)
                os.replace(os.path.join(msg_dir,msg_file + '.new'),os.path.join(msg_dir,msg_file))
