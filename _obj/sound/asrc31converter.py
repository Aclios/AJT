import os
import soundfile as sf
import io
import shutil


sound_bit_dict = {"PCM_16":16,"PCM_U8":8,"PCM_24":24,"PCM_32":32,"VORBIS":16,"OPUS":16}
sound_format_dict = {"WAV":b"wav ","OGG":b"ogg "}

class SRCDFile:
    def __init__(self,filepath,platform):
        self.filepath = filepath
        with open(filepath,mode='rb') as f:
            self.magic = f.read(4)
            if self.magic != b'srcd':
                raise Exception('Invalid asrc.31 file (bad magic)')
            self.platform = platform
            self.unk1 = f.read(4) # 00 00 00 00 ??
            self.audio_filesize = int.from_bytes(f.read(4),'little')
            self.audio_file_format = f.read(4) # = "wav " or "ogg " ?
            self.unk2 = f.read(4)
            self.filename_hash = f.read(8)
            self.channel_nbr = int.from_bytes(f.read(4),'little') #mono = 1, stereo = 2
            self.unk3 = f.read(4) # seems to be approx. filesize // 2 for wav, but idk
            self.unk_rate = int.from_bytes(f.read(4),'little') #sometimes it's different between files with the same exact wave header, so idk
            self.sample_rate = int.from_bytes(f.read(4),'little')
            self.bits_per_sample = int.from_bytes(f.read(2),'little')
            self.unk4 = f.read(11) #looks like flags
            self.unk5 = f.read(4)  #seems to be approx. filesize // 4 for wav, but idk
            self.flag = f.read(1)
            if self.flag == b'\x00':
                self.unk6 = f.read(24) #looks like flags
            elif self.flag == b'\x01': #bgm headers are longer
                self.unk6 = f.read(32) #looks like flags
            else:
                raise Exception('Unknown header size flag')
            self.data = f.read()

    def update(self):
        with open(self.filepath,mode='wb') as f:
            f.write(self.magic + self.unk1 + self.audio_filesize.to_bytes(4,'little') + self.audio_file_format + self.unk2 + self.filename_hash + self.channel_nbr.to_bytes(4,'little') + self.unk3 + self.unk_rate.to_bytes(4,'little') + self.samplerate.to_bytes(4,'little')+self.bits_per_sample.to_bytes(2,'little') + self.unk4 + self.unk5 + self.flag + self.unk6 + self.data)

    def import_audio(self,audio_filepath):
        format,channels,samplerate,subtype,data = get_audio_file_data(audio_filepath)
        bits_per_sample = sound_bit_dict[subtype]
        format_magic = sound_format_dict[format]
        self.audio_file_format,self.channel_nbr, self.samplerate,self.bits_per_sample,self.audio_filesize, self.data = format_magic,channels,samplerate,bits_per_sample,len(data), data

        if self.platform == 'Switch' and audio_filepath.endswith('wav'):
            new_audio_file = io.BytesIO()
            data, samplerate = sf.read(audio_filepath)
            sf.write(new_audio_file,data,samplerate,format="ogg")
            self.data = new_audio_file.getvalue()
            self.audio_file_format = b"ogg "
            self.audio_filesize = len(self.data)

        elif self.platform == "Steam" and audio_filepath.endswith("ogg"):
            new_audio_file = io.BytesIO()
            data, samplerate = sf.read(audio_filepath)
            sf.write(new_audio_file,data,samplerate,format="wav")
            self.data = new_audio_file.getvalue()
            self.audio_file_format = b"wav "
            self.audio_filesize = len(self.data)


def get_audio_file_data(audio_filepath):
        with open(audio_filepath,'rb') as f:
            data = f.read()
        with sf.SoundFile(audio_filepath,'r') as f:
            return f.format,f.channels,f.samplerate,f.subtype,data

def batch_export_srcd(extracted_root_dir,platform,ext):
    print('\n\n--- EXPORTING SOUND FILES ---\n\n')
    if platform == 'Steam':
        plat_code = 'stm'
    elif platform == 'Switch':
        plat_code = 'nsw'
    root = os.path.join(extracted_root_dir,'natives',plat_code,'streaming','sound')
    for path, subdirs,files in os.walk(root):
        for file in files:
            truepath = os.path.join(path,file)
            if (ext in ['zhcn','zhtw'] and os.path.isfile(f'{truepath}.ja')) or (f'.asrc.31.{ext}' in file): #chinese sounds don't have any extension, since they are the same for zhcn and zhtw
                try:
                    os.makedirs(path.replace(root,'sound'))
                except:
                    pass
                try:
                    print(f"Exporting {truepath}...")
                    snd = SRCDFile(truepath,platform)
                    if platform == 'Steam':
                        with open(os.path.join(truepath.replace(root,'sound') + '.wav'),'wb') as f:
                            f.write(snd.data)
                    elif platform == 'Switch':
                        with open(os.path.join(truepath.replace(root,'sound') + '.ogg'),'wb') as f:
                            f.write(snd.data)
                except:
                    pass

def batch_import_srcd(extracted_root_dir,patch_root_dir,platform,ext):
    if platform == 'Steam':
        plat_code = 'stm'
    elif platform == 'Switch':
        plat_code = 'nsw'
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
                asrc = SRCDFile(asrc_path,platform)
                asrc.import_audio(truepath)
                asrc.update()