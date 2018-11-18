#!/usr/bin/env python3

import pygame

from ViewtextRenderer import *
from testpages import engtest, LoadEP1


# Set to True to force rescaling of the image regardless of screen size
# TODO - allow scaling to be set to NONE, FIT or STRETCH
FORCE_SCALE=False

# Font size
FONT_SIZE = 20
# Antialiasing -- needs to be on or MODE7 will screw up
FONT_AA   = True

# Display timing -- flash on in seconds
T_FLASH_ON  = 1.0
# Display timing -- flash off in seconds
T_FLASH_OFF = 0.3


# initialise the display
print("displayInit")
pygame.display.init()

# hide the mouse cursor
pygame.mouse.set_visible(False)

# open the screen
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print("Framebuffer size: %d x %d" % (size[0], size[1]))
lcd = pygame.display.set_mode(size, pygame.FULLSCREEN)

print("modeset done")

# TODO background image
lcd.fill((63,63,63))

# initialise fonts
print("fontInit")
pygame.font.init()

# initialise Viewdata/Teletext renderer
print("viewtextInit")
r = ViewtextRenderer(font="fonts/MODE7GX0.TTF", fontsize=FONT_SIZE, antialias=FONT_AA)

#page = engtest
page = LoadEP1("snep.ep1")
#page = LoadEP1("1024.ep1")
main,flash = r.render(page)

# rescale the Teletext image if it's too large for the screen
r = main.get_rect()
lr = lcd.get_rect()
if (lr[0] < r[0]) or (lr[1] < r[1]) or FORCE_SCALE:
    # resize (scale down) to fit the screen
    r = main.get_rect().fit(lcd.get_rect())
    main = pygame.transform.smoothscale(main, (r.width, r.height))
    flash = pygame.transform.smoothscale(flash, (r.width, r.height))
else:
    # no resize required
    r = main.get_rect()

# centre the Teletext image on the screen
r.center=(size[0]/2, size[1]/2)

# set up 100ms tick
EVT_TICK=pygame.USEREVENT+1
TICKSPERSEC = 10
pygame.time.set_timer(EVT_TICK, (1000//TICKSPERSEC))

# main display loop
quit = False
tick = 0
while not quit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # quit (usually X11 only)
            quit = True

        elif event.type == pygame.KEYDOWN:
            # keypress
            if event.key == pygame.K_ESCAPE:
                quit = True

        elif event.type == EVT_TICK:
            # user defined event: timer tick
            if tick >= ((T_FLASH_ON + T_FLASH_OFF) * TICKSPERSEC):
                tick = 0
            else:
                tick += 1

       
    if tick == 0:
        # Start of time period -- 
        lcd.blit(main, r)
        pygame.display.update()

    elif tick >= (T_FLASH_ON * TICKSPERSEC):
        # Change from Main (flashing text displayed) to Flash
        # (flashing text hidden)
        lcd.blit(flash, r)
        pygame.display.update()


# shut down pygame on exit
pygame.quit()

