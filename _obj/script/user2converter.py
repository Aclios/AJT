import os
import shutil
from _obj.script.user2aa4converter import *


def readint32(f):
    return int.from_bytes(f.read(4),'little')

def readutf16(f):
    return f.read(2).decode('utf-16')


class User2Header:
    def __init__(self,first_header,unk1,topic_count,unk2,rsz_header_size,unk3,unk4,unk5):
        self.first_header = first_header
        self.magic = b'RSZ\x00'
        self.unk1 = unk1
        self.topic_count_1 = topic_count + 2
        self.unk2 = unk2
        self.rsz_header_size1 = rsz_header_size
        self.unk3 = unk3
        self.rsz_header_size2 = rsz_header_size
        self.unk4 = unk4
        self.topic_count_2 = topic_count + 1
        self.unk5 = unk5
        self.stuff = bytearray()
        for _ in range(topic_count):
            self.stuff += b'\x42\xf0\xf3\x83\x56\x31\x26\x0b'
        self.stuff += b'\xa7\x3a\x93\xee\xac\xa4\xa1\x1a'
        self.padding = rsz_header_size - 0x3c - 8*(topic_count+1)

    def write_to_file(self,f):
        f.write(self.first_header + self.magic + self.unk1 + self.topic_count_1.to_bytes(4,'little') + self.unk2 + self.rsz_header_size1.to_bytes(4,'little') + self.unk3 + self.rsz_header_size2.to_bytes(4,'little') + self.unk4 + self.topic_count_2.to_bytes(4,'little') + self.unk5 + self.stuff + self.padding * b'\x00')

class User2Topic:
    def __init__(self,topic_name_size,topic_name,topic_data_size,topic_data):
        self.name_size = topic_name_size
        self.name = topic_name
        self.data_size = topic_data_size
        self.data = topic_data

    def write_to_file(self,f):
        f.write(self.name_size.to_bytes(4,'little'))
        f.write(self.name.encode("utf-16")[2:] + 2 * b'\x00')
        if f.tell() % 4 != 0: # 4 bytes block padding
            f.write(2*b'\x00')
        f.write(self.data_size.to_bytes(4,'little'))
        f.write(self.data.encode("utf-16")[2:] + 2 * b'\x00')
        if f.tell() % 4 != 0: # 4 bytes block padding
            f.write(2*b'\x00')

class User2File:
    def __init__(self,filepath):
        if filepath.endswith('txt'): #import from txt
            with open(filepath,mode='rb') as f:
                self.filename = f.readline()[1:-2].decode()
                self.topic_list = []
                byte = f.read(1)
                first_topic = True
                topic_name = bytearray()
                topic_data = bytearray()
                while byte != b'':
                    if byte == b'{':
                        if not first_topic:
                            new_topic_data = topic_data.replace(b'<b>',b'\x0d\x0a').decode()
                            self.topic_list.append(User2Topic(len(topic_name.decode())+1,topic_name.decode(),len(new_topic_data)+1,new_topic_data))
                            topic_name = bytearray()
                            topic_data = bytearray()
                        else:
                            first_topic  = False
                        byte = f.read(1)
                        while byte != b'}':
                            topic_name += byte
                            byte = f.read(1)
                        byte = f.read(1)
                    elif byte in [b'\x0d',b'\x0a']:
                        byte = f.read(1)
                    else:
                        topic_data += byte
                        byte = f.read(1)
                topic_data = topic_data.replace(b'<b>',b'\x0d\x0a').decode()
                self.topic_list.append(User2Topic(len(topic_name.decode())+1,topic_name.decode(),len(topic_data)+1,topic_data))
                self.header = User2Header(b'USR' + bytes(13) + b'\x30' + bytes(7) + b'\x30' + bytes(7) + b'\x30' + bytes(15),b'\x10' + bytes(3) + b'\x01'+bytes(3),len(self.topic_list),bytes(8) + b'\x34'+bytes(7),0x40 + 0x10 * (len(self.topic_list)//2 + 1),bytes(4),bytes(4),bytes(8))



        else: #import from user2
            with open(filepath,mode='rb') as f:
                first_header = f.read(0x30)
                magic = f.read(4)
                if magic != b'RSZ\x00':
                    raise Exception("Error: invalid input file (bad magic)")
                unk1 = f.read(8)
                topic_count = readint32(f) - 2
                unk2 = f.read(16)
                rsz_header_size = readint32(f)
                unk3 = f.read(4)
                f.read(4)
                unk4 = f.read(4)
                f.read(4)
                unk5 = f.read(8)
                f.read(rsz_header_size -  60)
                self.header = User2Header(first_header,unk1,topic_count,unk2,rsz_header_size,unk3,unk4,unk5)
                self.topic_list = []
                for _ in range(topic_count):
                    topic_name_size = readint32(f)
                    topic_name = ''
                    for _ in range(topic_name_size - 1):
                        topic_name += readutf16(f)
                    f.read(2)
                    if f.tell() % 4 != 0: # 4 bytes block padding
                        f.read(2)
                    topic_data_size = readint32(f)
                    topic_data = ''
                    for _ in range(topic_data_size - 1):
                        topic_data += readutf16(f)
                    f.read(2)
                    if f.tell() % 4 != 0: # 4 bytes block padding
                        f.read(2)
                    self.topic_list.append(User2Topic(topic_name_size,topic_name,topic_data_size,topic_data))
                filename_lenght = readint32(f) - 1
                self.filename = ''
                for _ in range(filename_lenght):
                    self.filename += readutf16(f)


    def write_user2(self,filename):  #write user2
        with open(filename,mode="wb") as f:
            self.header.write_to_file(f)
            for topic in self.topic_list:
                topic.write_to_file(f)
            f.write((len(self.filename) + 1).to_bytes(4,'little'))
            f.write(self.filename.encode('utf-16')[2:] + 2 * b'\x00')
            if f.tell() % 4 != 0: # 4 bytes block padding
                f.write(2*b'\x00')
            f.write(len(self.topic_list).to_bytes(4,'little'))
            for i in range(len(self.topic_list)):
                f.write((i+1).to_bytes(4,'little'))

    def write_txt(self,txt_filename): #write txt
        with open(txt_filename,mode='wb') as f:
            f.write(b'{' + self.filename.encode() + b'}')
            f.write(b'\n\n')
            for topic in self.topic_list:
                f.write(b'{' + topic.name.encode() + b'}')
                f.write(b'\n\n')
                string = topic.data.replace('\x0d\x0a','<b>\n')
                newstring = ''
                func_flag = False
                func = ''
                bn_flag = False
                for char in string:
                    if char == '<':
                        func_flag = True
                    elif char == '>':
                        if 'XXXX MSG,' in func:
                            bn_flag = True
                        newstring += f'<{func}>'
                        func = ''
                        func_flag = False
                    elif func_flag:
                        func += char
                    else:
                        if bn_flag:
                            newstring += '\n'
                            bn_flag = False
                        newstring += char
                f.write(newstring.encode())
                f.write(b'\n\n')




def batch_export_user2_AA56(PLATFORM):
    extracted_root_dir = PLATFORM.pak_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
    #print('\n\n--- EXPORTING SCRIPT FILES ---\n\n')
    for dir in ['gs5','gs6']:
        user2_dir = os.path.join(extracted_root_dir,'natives',plat_code,'gamedesign',dir,'scriptdata')
        for file in os.listdir(user2_dir):
            if not file.endswith(f'.{ext}') and ext != 'all':
                continue
            truepath = os.path.join(user2_dir,file)
            try:
                os.makedirs(os.path.join('script',dir))
            except:
                pass
            output_path = os.path.join('script',dir,file + '.txt')
            print(f"Converting {truepath}...")
            user2 = User2File(truepath)
            user2.write_txt(output_path)

def batch_import_user2_AA56(PLATFORM):
    patch_root_dir = PLATFORM.patch_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
    for dir in ['gs5','gs6']:
        user2_dir = os.path.join(patch_root_dir,'natives',plat_code,'gamedesign',dir,'scriptdata')
        try:
            os.makedirs(user2_dir)
        except:
            pass
        txt_dir = os.path.join('script',dir)
        for file in os.listdir(txt_dir):
            if not file.endswith('.txt'):
                continue
            print(f'Converting {file}...')
            usr = User2File(os.path.join(txt_dir,file))
            usr.write_user2(os.path.join(user2_dir, file[:-4]))


def batch_export_user2(PLATFORM):
    batch_export_user2_AA4(PLATFORM)
    batch_export_user2_AA56(PLATFORM)


def batch_import_user2(PLATFORM):
    batch_import_user2_AA4(PLATFORM)
    batch_import_user2_AA56(PLATFORM)


