ext_dict = {
"Japanese":"ja",
"English":"en",
"French":"fr",
"Italian":"it",
"German":"de",
"Spanish":"es",
"Russian":"ru",
"Polish":"pl",
"Dutch":"nl",
"Portuguese":"pt",
"Brazilian Portuguese":"ptbr",
"Korean":"ko",
"Traditional Chinese":"zhtw",
"Simplified Chinese":"zhcn",
"Finnish":"fi",
"Swedish":"sv",
"Danish":"da",
"Norwegian":"no",
"Czech":"cs",
"Hungarian":"hu",
"Slovak":"sk",
"Arabic":"ar",
"Turkish":"tr",
"Bulgarian":"bg",
"Greek":"el",
"Romanian":"ro",
"Thai":"th",
"Ukrainian":"ua",
"Vietnamese":"vi",
"Indonesian":"id",
"Fiction":"cc",
"Hindi":"hi",
"Latin America Spanish":"es419"
}

temp = []

with open('path_init.txt','rb') as f:
    lines = f.readlines()
    for line in lines:
        try:
            path_data = line.replace(b'\n',b'').replace(b'\r',b'').replace(b'"',b'').split(b'=')
            temp.append(path_data[1].decode())
        except:
            raise Exception(f"Can't load line {line} from path_init.txt, invalid syntax")

STEAM_PAK_PATH, SWITCH_PAK_PATH, PS4_PAK_PATH, STEAM_PATCH_PATH, SWITCH_PATCH_PATH, PS4_PATCH_PATH, EXTENSION, STEAM_MOD_DIR, SWITCH_MOD_DIR, PS4_MOD_DIR = temp

if EXTENSION not in ext_dict.values() and EXTENSION != "all":
    error_mess = "\nThe extension must be one of the following:\n\n"
    for key in ext_dict:
        error_mess += f'"{ext_dict[key]}" ({key})\n'
    error_mess += f'\nYou can also use the "all" extension to extract all files.\n'
    raise Exception(error_mess)

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

class PS4:
    name = 'PS4'
    code = 'ps4'
    pak_path = PS4_PAK_PATH
    patch_path = PS4_PATCH_PATH
    mod_dir = PS4_MOD_DIR
    ext = EXTENSION