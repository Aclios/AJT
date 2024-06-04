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