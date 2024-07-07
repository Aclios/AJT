import os
import zlib
import zstd
import mmh3

def readint32(f):
    return int.from_bytes(f.read(4),'little')

def readint64(f):
    return int.from_bytes(f.read(8),'little')

class REPak:
    def __init__(self,filepath):
        with open(filepath,mode='rb') as f:
            self.filepath = filepath
            magic = f.read(4)
            if magic != b'KPKA':
                raise Exception('Error: bad magic')
            version = readint32(f)
            self.entry_count = readint32(f)
            unknown = f.read(4)
            self.entry_list = []
            for _ in range(self.entry_count):
                self.entry_list.append(PAKEntry(f))

    def unpack(self,output_dir):
        with open(self.filepath,mode='rb') as f:
            for entry in self.entry_list:
                f.seek(entry.offset)
                compressed_data = f.read(entry.compressed_size)
                if entry.compression_flag & 1: #deflate
                    data = zlib.decompress(compressed_data,-15)
                    compression = 'deflate'
                elif entry.compression_flag & 2:
                    data = zstd.decompress(compressed_data)
                    compression = 'zstd'
                else:
                    data = compressed_data
                    compression = 'none'
                print(f'Unpacking {entry.lowercase_path_hash}-{entry.uppercase_path_hash}.bin... (compression={compression})')
                with open(os.path.join(output_dir,f'{entry.lowercase_path_hash}-{entry.uppercase_path_hash}.bin'),mode='wb') as fw:
                    fw.write(data)


class PAKEntry:
    def __init__(self,f):
        if f != None:
            self.lowercase_path_hash = readint32(f)
            self.uppercase_path_hash = readint32(f)
            self.offset = readint64(f)
            self.compressed_size = readint64(f)
            self.decompressed_size = readint64(f)
            self.compression_flag = readint64(f)
            self.checksum = readint64(f)

pak = REPak(r'C:\Program Files (x86)\Steam\steamapps\common\Apollo Justice Ace Attorney Trilogy\re_chunk_000.pak')
pak.unpack(r'C:\Users\Clément\OneDrive\Documents\AJT\GT\rechunk_000')
