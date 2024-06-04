import os
import json
from _obj.utils.utils import *

with open(os.path.join('_obj','script','AJT','aa4_codes_info.json')) as json_file:
    codes_dict = json.load(json_file)

reverse_codes_dict = {codes_dict[key].split(',')[0] : key for key in codes_dict}

def readAA4char(f):
    data = f.read(2)
    value = int.from_bytes(data,'little') - 0xe000
    if value >= 0 and value <= 0x200:
        code_name, args_count = codes_dict[str(value)].split(",")
        output = f"<{code_name}"
        for _ in range(int(args_count)):
            arg_value = int.from_bytes(f.read(2),'little')
            output += f",{arg_value}"
        if code_name in ["b","p"]:
            return output + ">\n", 1 + int(args_count)
        return output + ">", 1 + int(args_count)
    else:
        return data.decode('utf-16'), 1

def readnextcode(f):
    data = bytearray()
    byte = f.read(1)
    while byte != b'>':
        data += byte
        byte = f.read(1)
    output = bytearray()
    values = data.split(b',')
    code = reverse_codes_dict[values[0].decode()]
    output += (int(code) + 0xe000).to_bytes(2,'little')
    for idx in range(len(values) - 1):
        output += int(values[idx + 1]).to_bytes(2,'little')
    return output



class User2AA4Header:
    def __init__(self,data_size,offset_list):
        self.stuff = b'USR\x00' + bytes(12) + b'\x30' + bytes(7) + b'\x30' + bytes(7) + b'\x30' + bytes(15) + b'RSZ\x00' + b'\x10' + bytes(3) + b'\x01' + bytes(3) + b'\x02' + bytes(11) + b'\x34' +  bytes(7) + b'\x50' +  bytes(7) + b'\x50' +  bytes(7) + b'\x01' + bytes(11) + b'\x45\x84\xa4\xda\xa2\xda\x12\x52' + bytes(12)
        self.data_size = data_size
        self.offset_list = offset_list

    def write(self,f):
        f.write(self.stuff + self.data_size.to_bytes(4,'little') + len(self.offset_list).to_bytes(4,'little'))
        for offset in self.offset_list:
            f.write(offset.to_bytes(4,'little'))

class User2AA4Topic:
    def __init__(self,data):
        self.data = data
        self.data_size = len(data)

class User2AA4File:
    def __init__(self,filepath):
        self.filepath = filepath
        if filepath.endswith('.txt'):
            with open(filepath,mode='rb') as f:
                self.topic_list = []
                byte = f.read(1)
                first_topic = True
                topic_data = bytearray()
                while byte != b'':
                    if byte == b'[':
                        if not first_topic:
                            self.topic_list.append(User2AA4Topic(topic_data))
                            topic_data = bytearray()
                        else:
                            first_topic  = False
                        byte = f.read(1)
                        while byte != b']':
                            byte = f.read(1)
                        byte = f.read(1)
                    elif byte == b'<':
                        topic_data += readnextcode(f)
                        byte = f.read(1)
                    elif byte in [b'\x0d',b'\x0a']:
                        byte = f.read(1)
                    else:
                        data = bytearray()
                        while byte not in [b'\x0d',b'\x0a',b'[',b'<',b'']:
                            data += byte
                            byte = f.read(1)
                        topic_data += data.decode().encode('utf-16')[2:]
                self.topic_list.append(User2AA4Topic(topic_data))
                data_size = 4 + 4 * len(self.topic_list)
                base_offset = 4 + 4 * len(self.topic_list)
                offset_list = [base_offset]
                for topic in self.topic_list[:-1]:
                    offset_list.append(offset_list[-1] + topic.data_size)
                data_size = offset_list[-1] + self.topic_list[-1].data_size
                self.header = User2AA4Header(data_size,offset_list)


        else:
            with open(filepath,mode='rb') as f:
                f.seek(0x80)
                data_size = readint32(f)
                self.topic_count = readint32(f)
                self.offset_list = []
                for _ in range(self.topic_count):
                    self.offset_list.append(readint32(f))
                self.topic_list = []
                for idx in range(self.topic_count):
                    if idx < self.topic_count -1 :
                        topic_len = self.offset_list[idx+1] - self.offset_list[idx]
                    else:
                        topic_len = data_size - self.offset_list[-1]
                    char_count = 0
                    scriptdata = ""
                    new_box_flag = True
                    while char_count < topic_len // 2:
                        data, count = readAA4char(f)
                        if "rowe" in data:
                            new_box_flag = True
                        if len(data) == 1 and new_box_flag == True:
                            scriptdata += '\n'
                            new_box_flag = False
                        char_count += count
                        scriptdata += data
                    self.topic_list.append(User2AA4Topic(scriptdata))

    def write_txt(self,txt_filepath):
        with open(txt_filepath,mode='w',encoding='utf-8') as f:
            for idx,topic in enumerate(self.topic_list):
                f.write(f'[{idx}]\n\n')
                f.write(topic.data + '\n\n')

    def write_user2(self,filepath):
        with open(filepath,mode='wb') as f:
            self.header.write(f)
            for topic in self.topic_list:
                f.write(topic.data)


def batch_export_user2_AA4(PLATFORM):
    extracted_root_dir = PLATFORM.pak_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
    user2_dir = os.path.join(extracted_root_dir,'natives',plat_code,'gamedesign','gs4','scriptbinary')
    for file in os.listdir(user2_dir):
        if not file.endswith(f'.{ext}') and ext != 'all':
            continue
        truepath = os.path.join(user2_dir,file)
        try:
            os.makedirs(os.path.join('script','gs4'))
        except:
            pass
        output_path = os.path.join('script','gs4',file + '.txt')
        print(f"Converting {truepath}...")
        user2 = User2AA4File(truepath)
        user2.write_txt(output_path)

def batch_import_user2_AA4(PLATFORM):
    patch_root_dir = PLATFORM.patch_path
    platform = PLATFORM.name
    plat_code = PLATFORM.code
    ext = PLATFORM.ext
    user2_dir = os.path.join(patch_root_dir,'natives',plat_code,'gamedesign','gs4','scriptbinary')
    try:
        os.makedirs(user2_dir)
    except:
        pass
    txt_dir = os.path.join('script','gs4')
    for file in os.listdir(txt_dir):
        if not file.endswith('.txt'):
            continue
        print(f'Converting {file}...')
        usr = User2AA4File(os.path.join(txt_dir,file))
        usr.write_user2(os.path.join(user2_dir, file[:-4]))