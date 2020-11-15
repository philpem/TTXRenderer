#!/usr/bin/env python3

from datetime import datetime
import os
import pygame

from ViewtextRenderer import *
from testpages import CeefaxEngtest, ETS300706Test, LoadEP1, LoadRaw


# Set to True to force rescaling of the image regardless of screen size
# TODO - allow scaling to be set to NONE, FIT or STRETCH
FORCE_SCALE=False

# Font size
FONT_SIZE = 30
# Antialiasing -- needs to be on or MODE7 will screw up
FONT_AA   = True

# Display timing -- flash on in seconds
T_FLASH_ON  = 1.0
# Display timing -- flash off in seconds
T_FLASH_OFF = 0.3

# Fullscreen
FULLSCREEN = False

# Hold pages up for this many seconds
PAGEDELAY = 10


# page list
pages = []
pages.append([196, CeefaxEngtest()])
pages.append([197, ETS300706Test()])
pages.append([198, LoadRaw('pages/P198-0001.bin')])
pages.append([366, LoadRaw('pages/trudge.bin')])
pages.append([535, LoadRaw('pages/SchedSat-001.bin')])
pages.append([535, LoadRaw('pages/SchedSat-002.bin')])
pages.append([535, LoadRaw('pages/SchedSat-003.bin')])
pages.append([367, LoadRaw('pages/conbook.bin')])
pages.append([536, LoadRaw('pages/SchedSun-001.bin')])
pages.append([536, LoadRaw('pages/SchedSun-002.bin')])
pages.append([536, LoadRaw('pages/SchedSun-003.bin')])
pages.append([621, LoadRaw('pages/contact.bin')])


# initialise the display
print("displayInit")
pygame.display.init()
pygame.display.set_caption('Viewtext renderer')

# hide the mouse cursor
pygame.mouse.set_visible(False)

# open the screen
if FULLSCREEN:
    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    print("Framebuffer size: %d x %d" % (size[0], size[1]))
    lcd = pygame.display.set_mode(size, pygame.FULLSCREEN)
else:
    #size = (720, 576)
    size = (1280,768)
    lcd = pygame.display.set_mode(size, 0)

print("modeset done")

# TODO background image
lcd.fill((0,0,0))

# initialise fonts
print("fontInit")
pygame.font.init()

# initialise Viewdata/Teletext renderer
print("viewtextInit")
#vtr = ViewtextRenderer(font="fonts/MODE7GX0.TTF", fontsize=FONT_SIZE, antialias=FONT_AA)
vtr = ViewtextRenderer(font="bedstead", fontsize=FONT_SIZE, antialias=FONT_AA)


# --- set up transform rectangle ---

# do an initial render
pagenumber, page = pages[0]
main,flash = vtr.render(page)

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
pageidx = 0
lasttick = 0
while not quit:
    lasttick = tick
    newpage = False

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
            tick += 1

    # if the tick hasn't incremented, don't bother doing anything
    if (tick <= lasttick):
        continue

    if (tick % (PAGEDELAY*TICKSPERSEC)) == 0:
        # pick the next page
        pagenumber, page = pages[pageidx]
        pageidx += 1
        if pageidx >= len(pages):
            pageidx = 0
        newpage = True

    if (tick % TICKSPERSEC) == 0 or newpage:
        # Top of second. Update the header row and force a display update.
        now = datetime.now()

        page[0]  = b'  P%03d  ' % pagenumber            # decoder reserved (8 chars) -- requested page number
        page[0] += b'\x04\x1d\x03Furcfax \x07\x1c '     # header bar
        page[0] += b'%03d ' % pagenumber                 # page number
        page[0] += bytes(now.strftime("%b%d"), 'ascii')     # date
        page[0] += b'\x03'      # yellow text for clock
        page[0] += bytes(now.strftime("%H:%M/%S"), 'ascii') # time

        main,flash = vtr.render(page)

    ## --- flash display loop ---

    if (tick % ((T_FLASH_OFF + T_FLASH_ON) * TICKSPERSEC)) == 0:
        # Start of flash time period -- blit the main image
        lcd.blit(main, r)
        pygame.display.update()
        #pygame.image.save(main, "teletext_new.png")
        #os.replace("teletext_new.png", "teletext.png")

    elif (tick % ((T_FLASH_OFF + T_FLASH_ON) * TICKSPERSEC)) == (T_FLASH_ON * TICKSPERSEC):
        # Change from Main (flashing text displayed) to Flash
        # (flashing text hidden)
        lcd.blit(flash, r)
        pygame.display.update()
        #pygame.image.save(flash, "teletext_new.png")
        #os.replace("teletext_new.png", "teletext.png")


# shut down pygame on exit
pygame.quit()
