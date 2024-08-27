# AJT-Tools

Extracting / importing tools for some RE Engine games, for Steam, Switch and PS4 versions.

The following files are supported:

Textures (.tex)

Apollo Justice Trilogy script files (.user.2)
 
Message data files (.msg)

Sound files (.asrc)

Full support for Apollo Justice Trilogy (Steam, Switch, PS4 (limited testing)) and Ghost Trick: Phantom Detective (Steam and Switch, PS4 have not been tested but should be supported)

Limited support for other RE Engine games.

# Setup

To use this project, you need to extract the .pak file(s) of the platform(s) you want to mod.  

Download retool: https://www.patreon.com/posts/retool-v0-225-to-100846608

Download the release list(s) of your game and platform(s) here: https://github.com/Ekey/REE.PAK.Tool

Put your pak file(s) in the same folder than retool and run 
<code> retool -h <.list file> -x <.pak file> </code>

Then, you need to fill the path_init.txt file:

"extracted_XXX_pak_path" must be filled with the path of your extracted .pak file(s). Those paths should link to a folder which contain the "natives" folder (the path should end with "re_chunk_000").

"XXX_patch_dir" must be filled with the folder(s) where you want your modded files to be written. These folders should be empty.

"extension" is the game language extension of the files you want to extract. You can find a full list of the extensions in _obj/platform.py.
You can also use the "all" extension to export all supported files of the game.

"XXX_mod_dir" must be filled with the folder(s) where you want your .pak patch file to be written. For Steam, it should be the Steam directory of the game and for Switch it can be the mod/{game id}/romfs folder of an emulator.

# Usage

After the setup, you can extract the files to common files format by running one of the EXTRACT .bat files. If you have the choice, it's always better to extract from the Steam version because it will be much faster since the textures are not swizzled.

.tex files will be extracted to png, .msg files to csv or txt, and asrc to wav (Steam), wav/ogg (Switch) or at9 (PS4).

From now, you can just replace the files with your modded files and run the IMPORT .bat files to create your patched files. Note that the textures (and especially Switch textures) are very long to import, so you have an option to only import text and sound files.

After the files are imported, a .pak patch file will be created and automatically moved to the mod directory given in the init file.

#  Requirements

You need Python 3.10 or above, Pillow (image processing), soundfile (sound files processing), pyswizzle and numpy (textures swizzle) modules. 

In a Command prompt, run the following commands to install those modules:

<code>python3 -m pip install --upgrade Pillow</code>

<code>python3 -m pip install --upgrade soundfile</code>

<code>python3 -m pip install --upgrade pyswizzle</code>

<code>python3 -m pip install --upgrade numpy</code>

# Limitations

For sound files, the project can automatically convert wav to ogg and vice versa but at9 conversion is not supported. You'll need to find a converter and do the conversion yourself.

# Credits

Kuriimu2 for some info about how Switch textures are swizzled (see https://github.com/FanTranslatorsInternational/Kuriimu2)

# See also

REEngine font cryptor/decryptor: https://github.com/Ekey/REE.PAK.Tool/tree/main

AJT .gui files conversion: https://github.com/Akrasr/AJT-RE-Engine-GUI-Investigator/tree/v1.0.0

.mesh (3D models) import/export: https://github.com/alphazolam/fmt_RE_MESH-Noesis-Plugin
