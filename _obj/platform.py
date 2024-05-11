temp = []

with open('path_init.txt','rb') as f:
    lines = f.readlines()
    for line in lines:
        try:
            path_data = line.replace(b'\n',b'').replace(b'\r',b'').replace(b'"',b'').split(b'=')
            temp.append(path_data[1].decode())
        except:
            raise Exception(f"Can't load line {line} from path_init.txt, invalid syntax")

STEAM_PAK_PATH, SWITCH_PAK_PATH, STEAM_PATCH_PATH, SWITCH_PATCH_PATH, EXTENSION, STEAM_MOD_DIR, SWITCH_MOD_DIR = temp

if EXTENSION not in ['ja','fr','en','de','ko','zhcn','zhtw','all']:
    raise Exception("Extension must have one of the following values: ['ja','fr','en','de','ko','zhcn','zhtw','all']")

class Steam:
    name = 'Steam'
    code = 'stm'
    pak_path = STEAM_PAK_PATH
    patch_path = STEAM_PATCH_PATH
    mod_dir = STEAM_MOD_DIR
    ext = EXTENSION

class Switch:
    name = 'Switch'
    code = 'nsw'
    pak_path = SWITCH_PAK_PATH
    patch_path = SWITCH_PATCH_PATH
    mod_dir = SWITCH_MOD_DIR
    ext = EXTENSION