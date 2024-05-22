#very unefficient way to swizzle/unswizzle textures, but it was easier to do since it's a more visual approch, and at least it works

from PIL import Image

#it should be totally possible to deduct these list from format data (BC or not?; number of bits per pixel, etc.)

unswizzle_dict = {
"BC7_UNORM":[(4,4),[[8,8,True],[16,32,True],[16,512,True]]],
"BC1_UNORM":[(4,4),[[8,8,False],[16,32,False],[32,512,False]]],
"RGBA8888_UNORM":[(1,1),[[4,2,False],[8,2,False],[8,8,False],[16,8,False],[16,128,False]]]
}

swizzle_dict = {
"BC7_UNORM":[[16,512,False],[16,32,True],[8,8,True],[4,4,True]],
"BC1_UNORM":[[32,512,False],[16,32,False],[8,8,False],[4,4,False]],
"RGBA8888_UNORM":[[16,128,False],[16,8,False],[8,8,False],[8,2,False],[4,2,False],[1,1,False]]
}


class ImageDeswizzle:
    def __init__(self,im,format):
        self.im = im
        self.width = self.im.size[0]
        self.height = self.im.size[1]
        self.x = 0
        self.y = 0
        self.format = format
        self.block, self.coord_L = unswizzle_dict[format].copy()
        if self.format in ["BC7_UNORM","BC1_UNORM"]:
            if self.height <= 256:
                self.coord_L[-1][1] = 256
                self.height = 256
            else:
                self.coord_L[-1][1] = 512


    def get_next_block(self):
        block = self.im.crop((self.x,self.y,self.x + self.block[0],self.y + self.block[1]))
        self.x += self.block[0]
        if self.x >= self.width:
            self.x = 0
            self.y += self.block[1]
        return block

    def get_tile(self,L):
        tile_size = L[-1][0] * L[-1][1]
        block_count = tile_size // (self.block[0] * self.block[1])
        tile_list = []
        current_size = (self.block[0],self.block[1])
        for _ in range(block_count):
            tile_list.append(self.get_next_block())
        for tiling_data in L:
            new_tile_list = []
            width, height, isver = tiling_data
            idx = 0
            while idx < len(tile_list):
                newtile = Image.new('RGBA',(width,height))
                if isver:
                    for i in range(width//current_size[0]):
                        for j in range(height//current_size[1]):
                            smalltile = tile_list[idx]
                            idx += 1
                            newtile.paste(smalltile,(i*current_size[0],j*current_size[1]))
                else:
                    for j in range(height//current_size[1]):
                        for i in range(width//current_size[0]):
                            smalltile = tile_list[idx]
                            idx += 1
                            newtile.paste(smalltile,(i*current_size[0],j*current_size[1]))
                new_tile_list.append(newtile)
            tile_list = new_tile_list
            current_size = (width,height)
        if len(tile_list) != 1:
            print(len(tile_list))
        return tile_list[0]

    def deswizzle(self,final_width,final_height):
        new_im = Image.new('RGBA',(self.width,self.height))
        max_tile_width = self.coord_L[-1][0]
        max_tile_height = self.coord_L[-1][1]
        for j in range(self.height // max_tile_height):
            for i in range(self.width // max_tile_width):
                tile = self.get_tile(self.coord_L)
                new_im.paste(tile,(i*max_tile_width,j*max_tile_height))
        new_im = new_im.crop((0,0,final_width,final_height))
        return new_im


class ImageSwizzle:
    def __init__(self,im,format):
        self.coord_L = swizzle_dict[format].copy()
        self.im = im
        self.format = format
        self.width = self.im.size[0]
        self.height = self.im.size[1]
        max_width_tile = self.coord_L[0][0]
        max_height_tile = self.coord_L[0][1]
        if self.format in ["BC7_UNORM","BC1_UNORM"]: #swizzling is different if the file is too small in height. The max tile height can be reduce to 256, 128, 64, etc.
            for pow in range(9):
                if self.height <= 2**(pow + 1) and self.height > 2**pow:
                    self.coord_L[0][1] = 2**(pow+1)
                    self.height = 2**(pow+1)
                    break
        if self.height % max_height_tile != 0 and self.height >= max_height_tile:
            self.height = ((self.height // max_height_tile) + 1) * max_height_tile
        if self.width % max_width_tile != 0:
            self.width = ((self.width // max_width_tile) + 1) * max_width_tile

        if self.format in ["BC7_UNORM","RGBA8888_UNORM"]: #rewriting an image with the right dimensions so it can be swizzled (for BC1, width must be a multiple of 32 and height a multiple of 512 or equal to 256, 128, ..., for example)
            expanded_im = Image.new('RGBA',(self.width,self.height))
        elif self.format in ["BC1_UNORM"]:
            expanded_im = Image.new('RGB',(self.width,self.height))
        expanded_im.paste(self.im,(0,0))
        self.im = expanded_im
        self.x = 0
        self.y = 0

    def swizzle_tile(self,L):
        tile_list = [self.im]
        width, height = self.width,self.height
        for tiling_data in L:
            new_tile_list = []
            tile_width, tile_height, isver = tiling_data
            for tile in tile_list:
                if isver:
                    for i in range(width//tile_width):
                        for j in range(height//tile_height):
                            smalltile = tile.crop((i*tile_width,j*tile_height,(i+1)*tile_width,(j+1)*tile_height))
                            new_tile_list.append(smalltile)
                else:
                    for j in range(height//tile_height):
                        for i in range(width//tile_width):
                            smalltile = tile.crop((i*tile_width,j*tile_height,(i+1)*tile_width,(j+1)*tile_height))
                            new_tile_list.append(smalltile)
            tile_list = new_tile_list
            width,height = tile_width,tile_height
        return tile_list


    def swizzle(self):
        if self.format in ["BC7_UNORM","RGBA8888_UNORM"]:
            new_im = Image.new('RGBA',(self.width,self.height))
        elif self.format in ["BC1_UNORM"]:
            new_im = Image.new('RGB',(self.width,self.height))
        idx = 0
        tile_list = self.swizzle_tile(self.coord_L)
        block_width,block_height = self.coord_L[-1][0], self.coord_L[-1][1]
        for j in range(self.height // block_height):
            for i in range(self.width // block_width):
                new_im.paste(tile_list[idx],(i*block_width,j*block_height))
                idx += 1
        if self.format in ["BC7_UNORM","BC1_UNORM"]:
            swizzle_dict[self.format][0][1] = 512
        return new_im
