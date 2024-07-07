import os
import soundfile as sf
import io
import shutil
from _obj.utils.utils import *
import traceback

sound_bit_dict = {"PCM_16":16,"PCM_U8":8,"PCM_24":24,"PCM_32":32,"VORBIS":16,"OPUS":16}
sound_format_dict = {"WAV":b"wav ","OGG":b"ogg "}
ext_dict={b"wav ":".wav",b"ogg ":".ogg",b"at9 ":".at9"}

class ASRCFile:
    def __init__(self,filepath):
        self.filepath = filepath
        with open(filepath,mode='rb') as f:
            self.magic = f.read(4)
            if self.magic != b'srcd':
                raise Exception('Invalid asrc file (bad magic)')
            self.unk1 = f.read(4) # 00 00 00 00 ??
            self.audio_filesize = readint32(f)
            self.audio_file_format = f.read(4) # = "wav " or "ogg " ?
            if self.audio_file_format not in [b"wav ",b"ogg ",b"at9 "]:
                raise Exception(f"Error: unimplemented audio format: {self.audio_file_format}")
            self.ext = ext_dict[self.audio_file_format]
            self.unk2 = f.read(4)
            if '.asrc.31' in self.filepath:
                self.filename_hash = f.read(8)
            else:
                self.filename_hash = f.read(4)
            self.channel_nbr = readint32(f) #mono = 1, stereo = 2
            self.unk3 = f.read(4) # seems to be approx. filesize // 2 for wav, but idk
            self.unk_rate = readint32(f) #sometimes it's different between files with the same exact wave header, so idk
            if '.asrc.31' in self.filepath:
                self.samplerate = readint32(f)
            else:
                self.samplerate = None
            self.bits_per_sample = readint16(f)
            self.unk4 = f.read(11) #looks like flags
            self.unk5 = f.read(4)  #seems to be approx. filesize // 4 for wav, but idk
            self.some_count = readint32(f)
            self.unknown_struct_list = []
            for _ in range(self.some_count):
                self.unknown_struct_list.append(f.read(8))
            self.unk6 = f.read(8) #padding ?
            self.header_flag = f.read(1)
            if self.header_flag == b'\x00':
                self.unk7 = f.read(12)
            elif self.header_flag == b'\x01':
                self.unk7 = f.read(0x20)
            self.data = f.read()

    def update(self):
        stream = self.magic + self.unk1 + self.audio_filesize.to_bytes(4,'little') + self.audio_file_format + self.unk2 + self.filename_hash + self.channel_nbr.to_bytes(4,'little') + self.unk3 + self.unk_rate.to_bytes(4,'little')
        if self.samplerate != None:
            stream += self.samplerate.to_bytes(4,'little')
        steam += self.bits_per_sample.to_bytes(2,'little') + self.unk4 + self.unk5 + self.some_count.to_bytes(4,'little')
        for stuff in self.unknown_struct_list:
            stream += stuff
        stream += self.unk6 + self.header_flag + self.unk7 + self.data
        with open(self.filepath,mode='wb') as f:
            f.write(stream)

    def import_audio(self,audio_filepath):
        format,channels,samplerate,subtype,data = get_audio_file_data(audio_filepath)
        bits_per_sample = sound_bit_dict[subtype]
        format_magic = sound_format_dict[format]
        self.audio_file_format,self.channel_nbr, self.samplerate,self.bits_per_sample,self.audio_filesize, self.data = format_magic,channels,samplerate,bits_per_sample,len(data), data

        if self.audio_file_format == b"at9 " and not audio_filepath.endswith('at9'):
            raise Exception("Error: at9 conversion is not supported.")

        elif self.audio_file_format == b"ogg " and audio_filepath.endswith('wav'):
            new_audio_file = io.BytesIO()
            data, samplerate = sf.read(audio_filepath)
            sf.write(new_audio_file,data,samplerate,format="ogg")
            self.data = new_audio_file.getvalue()
            self.audio_filesize = len(self.data)

        elif self.audio_file_format == b"wav " and audio_filepath.endswith("ogg"):
            new_audio_file = io.BytesIO()
            data, samplerate = sf.read(audio_filepath)
            sf.write(new_audio_file,data,samplerate,format="wav")
            self.data = new_audio_file.getvalue()
            self.audio_filesize = len(self.data)

    def export_audio(self,audio_filepath):
        with open(audio_filepath,mode='wb') as f:
            f.write(self.data)

def get_audio_file_data(audio_filepath):
        with open(audio_filepath,'rb') as f:
            data = f.read()
        with sf.SoundFile(audio_filepath,'r') as f:
            return f.format,f.channels,f.samplerate,f.subtype,data

def batch_export_asrc(PLATFORM):
    print('\n\n--- EXPORTING SOUND FILES ---\n\n')
    extracted_root_dir = PLATFORM.pak_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
    root = os.path.join(extracted_root_dir,'natives',plat_code,'streaming','sound')
    for path, subdirs,files in os.walk(root):
        for file in files:
            truepath = os.path.join(path,file)
            if islocalized(file,'.asrc',ext):
                try:
                    os.makedirs(path.replace(root,'sound'))
                except:
                    pass
                try:
                    print(f"Exporting {truepath}...")
                    snd = ASRCFile(truepath)
                    audio_filepath = truepath.replace(root,'sound') + snd.ext
                    snd.export_audio(audio_filepath)
                except:
                    traceback.print_exc()

def batch_import_asrc(PLATFORM):
    print('\n\n--- IMPORTING SOUND FILES ---\n\n')
    extracted_root_dir = PLATFORM.pak_path
    patch_root_dir = PLATFORM.patch_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
    for path, _, files in os.walk('sound'):
        for file in files:
            truepath = os.path.join(path,file)
            if file.endswith('.wav') or file.endswith('.ogg'):
                print(f'Importing {truepath}...')
                asrc_path = os.path.join(patch_root_dir,'natives',plat_code,'streaming',truepath.replace('.wav','').replace('.ogg',''))
                if not os.path.isfile(asrc_path):
                    if not os.path.isdir(os.path.dirname(asrc_path)):
                        os.makedirs(os.path.dirname(asrc_path))
                    shutil.copy(asrc_path.replace(patch_root_dir,extracted_root_dir),asrc_path)
                asrc = ASRCFile(asrc_path,platform)
                asrc.import_audio(truepath)
                asrc.update()