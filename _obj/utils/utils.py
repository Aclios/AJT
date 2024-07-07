import os

def readint32(file):
    return int.from_bytes(file.read(4),'little')

def readint24(file):
    return int.from_bytes(file.read(3),'little')

def readint16(file):
    return int.from_bytes(file.read(2),'little')

def readint8(file):
    return int.from_bytes(file.read(1),'little')

def writeint32(file,value):
    file.write(value.to_bytes(4,'little'))

def writeint24(file,value):
    file.write(value.to_bytes(3,'little'))

def writeint16(file,value):
    file.write(value.to_bytes(2,'little'))

def writeint8(file,value):
    file.write(value.to_bytes(1,'little'))

def readutf16(f):
    return f.read(2).decode('utf-16')

def islocalized(path,file_ext,lang_ext):
    file, dir = os.path.basename(path), os.path.dirname(path)
    if lang_ext == 'all' and file_ext in path:
        return True
    if lang_ext in ['en','fr','de']: #useful for one AJT file
        region = 'europe'
    else:
        region = 'asia'
    if (file_ext in file and file.endswith(lang_ext)) or (f'_{lang_ext}_' in file and file_ext in file) or ((region in file) and file_ext in file):
        return True
    elif file_ext in file:
        if not os.path.isfile(path + f'.{lang_ext}'):
            for lang_ext in ['ja','en','de','fr','ko','it','es','zhcn','zhtw','ru','pl','nl','pt','ptbr','fi','sv','da','no','cs','hu','sk','ar','tr','bg','el','ro','th','ua','vi','id','cc','hi','es419']:
                if os.path.isfile(path + f'.{lang_ext}'):
                    return True
            return False
    else:
        return False