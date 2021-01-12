

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation
import numpy as np
from PIL import Image
import random
from datetime import datetime
from datetime import timedelta
from threading import Thread

def sp_album_art_screensaver(update_display = True, display_result = True):
    global sp_saved_album_arts, display
    if datetime.now() - timedelta(days=1) > sp_saved_album_arts["last updated"]:
        print("fetching album art:")
        sp_saved_album_arts["art"] = [album_info["art"]["64x64"] for album_info in sp_api.get_saved_albums(album_art_size = "small")]
        sp_saved_album_arts["last updated"] = datetime.now()
    # imgplot = plt.imshow(random.choice(album_arts)["64x64"])
    # plt.show()
    
    # likelihood that tile will be square rather than rectangular
   
    rect_tile_horizontal_orientation_pref = .5
    
    shape_prefs = {"square": .8, "rectangle": .2}
    size_prefs = {64: .3, 32: .6, 16: .1}
    orient_prefs = {"horizontal": .8, "vertical": .2}
    
    # last_cycle = datetime.now()
    
    # if datetime.now() > last_cycle + timedelta(seconds = cycle_time):
    art_pool = sp_saved_album_arts["art"] 
    
    pixels = np.array([[[-1,-1,-1] for x in range(ledm_width)] for y in range(ledm_height)])
    
    tries = 0
    tiles_placed = 0
    finished = False
    x, y = 0, 0
    while not finished:

        print("("+str(x)+", "+str(y)+")")
        tries+=1
        tile_size = np.random.choice(list(size_prefs.keys()), p = list(size_prefs.values()))
        # 16x16 only squares; no rectangles
        if tile_size == 16:
            tile_shape = "square"
            tile_orient = ""
        else:
            tile_shape = np.random.choice(list(shape_prefs.keys()), p = list(shape_prefs.values()))
            tile_orient = np.random.choice(list(orient_prefs.keys()), p = list(orient_prefs.values()))
        print(tile_size)
        print(tile_shape)
        print(tile_orient)
        xspan = tile_size + tile_size * (tile_shape=="rectangle") * (- ((tile_orient == "vertical")) / 2)
        yspan = tile_size + tile_size * (tile_shape=="rectangle") *  (- ((tile_orient == "horizontal")) / 2)
        print("xspan: " + str(xspan) +", yspan: "+ str(yspan))
        
        # tile fits
        if y + yspan <= ledm_height and x + xspan <= ledm_width and (pixels[int(y)][int(x + xspan - 1)] == [-1,-1,-1]).all() and (pixels[int(y + yspan - 1)][int(x)] == [-1,-1,-1]).all():
            try:
                pixels[int(y):int(y+yspan), int(x):int(x+xspan)] = crop_image(art_pool[(selected_art_index:= random.randint(0,len(art_pool)-1))], xspan, yspan)
            except Exception as e:
                print(selected_art_index)
                print(art_pool[selected_art_index])
                
            del art_pool[selected_art_index]
            tiles_placed += 1
            x += xspan
            
            # imgplot = plt.imshow(pixels)
            # plt.show()
            # edge of display has been reached: wrap around to next available spot
            if int(x) == int(ledm_width) or not ((pixels[int(y)][int(x)] == [-1,-1,-1]).all()):
                print("looping around:")
                finished = True
                for xi in range(ledm_width):
                    if not finished:
                        break
                    for yi in range(ledm_height):
                        if (pixels[yi][xi] == [-1,-1,-1]).all():
                            x = xi
                            y = yi
                            print("new x and y: ("+str(x)+", "+str(y)+")")
                            finished = False
                            break
    
    # if instructed to update the global display state
    if update_display:
        display = pixels
    
    # if instructed to display the screensaver that was just created
    if display_result:
        imgplot = plt.imshow(pixels)
        plt.show()
    
    return pixels

def crop_image(image, xdim, ydim, xalign = "center", yalign = "center"):
    xdim = int(xdim)
    ydim = int(ydim) 
    image = np.array(image)
    smallest_dim = min([xdim, ydim])
    largest_dim = max([xdim, ydim])
    print(smallest_dim)
    print(largest_dim)
    # resizing needed
    if largest_dim < len(image): 
        PIL_image = Image.fromarray(image)
        image = np.array(PIL_image.resize((largest_dim, largest_dim)))
    
    
    # needs cropped
    if xdim != ydim:
        # x dimension needs cropped
        if xdim == smallest_dim:
            if xalign == "center":
                image = image[:, int(len(image)/2 - xdim / 2): int(len(image)/2 + xdim / 2)]
            elif xalign == "left":
                image = image[:, 0:xdim]
            elif xalign == "right":
                image = image[:, xdim:]
        # y dimension needs cropped
        if ydim == smallest_dim:
            if yalign == "center":
                image = image[int(len(image)/2 - ydim / 2) : int(len(image)/2 + ydim / 2),:]
            elif yalign == "top":
                image = image[0:ydim, :]
            elif yalign == "bottom":
                image = image[ydim:, :]
    return image
    
# try:
    # show desired album art 
    # imgplot = plt.imshow(sp_api.get_currently_playing_info()["album arts"].get("64x64"))
    # plt.show()
# except:
    # print("album art not found!")
    
# sp_album_art_screensaver()

# test 
# imgplot = plt.imshow(crop_image(sp_api.get_currently_playing_info()["album arts"].get("64x64"), 64, 32, "center", "center"))
# plt.show()
# fig = plt.figure()
# im = plt.imshow(display)
# def update_display(tick):
    # global display
    # if tick % (ledm_fps * 10) == 0:
        # Thread(target = sp_album_art_screensaver, args=(True,)).start()
    # im.set_array(display)
    # return [im]
    
    

# ani = animation.FuncAnimation(fig,update_display,frames=range(864000000),interval=(1.0/ledm_fps), blit=True)
# plt.show()
sp_album_art_screensaver(display_result = True)