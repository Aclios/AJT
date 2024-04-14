# AJT-Tools

Tools for modding Apollo Justice Trilogy, Switch and Steam versions. Support most of tex.719230324 files (textures), user.2 files (script, only for AA5 and AA6), msg.22 files (all text data that isn't script), asrc.31 files (sound). Can import/export from/to one language of the game according to the provided language file extension.

# Setup

First, you need to download the following tools as exe and add them to the same folder as main.py:

retool: https://www.patreon.com/posts/retool-modding-36746173?l=en
texconv: https://github.com/Microsoft/DirectXTex/wiki/Texconv
remsg_converter: https://github.com/dtlnor/REMSG_Converter

Second, fill the path_init.txt file:

"extracted_steam_pak_path" and "extracted_switch_pak_path" are the path of your extracted pak files, should end with "re_chunk_000"
"steam_patch_dir" and "switch_patch_dir" are the folders where you want your modded files to be written, they can be empty
"extension" is the game extension of the files you want to extract, must be one of the following: "fr","en","de","ko","zhcn","zhtw". "ja" wont' work for now because Japanese texture files don't have langage extension.
"steam_mod_dir" and "switch_mod_dir" are the folders where you want your patch pak files to be written. 

# Requirements

Python 3.x, Pillow (image processing) and soundfile (sound files processing) modules. 
(python3 -m pip install --upgrade Pillow; python3 -m pip install --upgrade soundfile)
