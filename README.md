# AJT-Tools

Tools for modding Apollo Justice Trilogy, Switch and Steam versions. 

The following files are supported:

tex.719230324 (textures) 

user.2 files (script)

msg.22 files (message data) 

asrc.31 files (sound) 

# Setup

First, you need to download the following tools as exe and add them to the same folder as main.py:

retool (pak extraction/repacking): https://www.patreon.com/posts/retool-modding-36746173?l=en

texconv (png/dds conversion): https://github.com/Microsoft/DirectXTex/wiki/Texconv

remsg_converter (msg.22 files conversion): https://github.com/dtlnor/REMSG_Converter

Then, you have to extract the .pak files of the platform(s) you want to mod. Download the release list(s) here: https://github.com/Ekey/REE.PAK.Tool, put your pak file(s) in the same folder than retool and run 
<code> retool -h <.list file> -x <.pak file> </code>

Finally, fill the path_init.txt file:

"extracted_steam_pak_path" and "extracted_switch_pak_path" are the path of the folders of your extracted .pak files. Those paths should link to a folder which contain the "natives" folder. If you only want to mod one of the two platforms, you can just fill one of the paths.

"steam_patch_dir" and "switch_patch_dir" are the folders where you want your modded files to be written, they should be empty.

"extension" is the game extension of the files you want to extract, so one of the following: "ja","fr","en","de","ko","zhcn","zhtw". The tools will only extract the files that are exclusive to this language, and the patch will replace the files of this language. It is heavily advised to chose the langage you want to translate from, since the extracted scripts will be of this language.

You can also use the "all" extension to export all the supported files of the game.

"steam_mod_dir" and "switch_mod_dir" are the folders where you want your patch pak files to be written. For Steam, it's by default the Steam directory of the game and there is no real reason to change it, for Switch you can put the mod/{game id}/romfs of an emulator.

# How does it work ?

After the setup, you can extract the files to common files format by running one of the EXTRACT .bat files. If you can chose between Switch and Steam, please use the Steam one, since the Switch textures have to be deswizzled, so they are much longer to extract.

tex.719230324 will be extracted to png files, msg.22 and user.2 to txt files, and asrc.31 to wav (Steam) or ogg (Switch) files.

From now, you can just replace the files with your modded files and run the IMPORT .bat files to create your patched files. Note that the textures (and especially Switch textures) are very long to import, so you have an option to only import text and sound files.

After importing the files, a patched .pak file will be created and automatically moved to the mod directory given in the init file.

#  Requirements

You need Python 3.x, Pillow (image processing) and soundfile (sound files processing) modules. 

<code>python3 -m pip install --upgrade Pillow</code>

<code>python3 -m pip install --upgrade soundfile</code>

# Limitations

The texture files can't be resized for now.

# Credits

retool for tex format

Kuriimu2 for some info about how Switch textures are swizzled (see https://github.com/FanTranslatorsInternational/Kuriimu2)

REE.PAK.Tool for file hash lists

# See also

REEngine font cryptor/decryptor: https://github.com/Ekey/REE.PAK.Tool/tree/main

AJT .gui files conversion: https://github.com/Akrasr/AJT-RE-Engine-GUI-Investigator/tree/v1.0.0
