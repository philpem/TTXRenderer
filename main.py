#!/usr/bin/env python3

import pygame

from ViewtextRenderer import *
from testpages import engtest


#os.putenv('SDL_FBDEV', '/dev/fb1')
#os.putenv('SDL_VIDEODRIVER', 'fbcon') # Force PyGame to PiTFT
print("displayInit")
pygame.display.init()
#pygame.mouse.set_visible(False)


print("Modelist:")
for mode in pygame.display.list_modes():
    print("   {0} x {1}".format(mode[0], mode[1]))


size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print("Framebuffer size: %d x %d" % (size[0], size[1]))
#size = (768,576)
lcd = pygame.display.set_mode(size, pygame.FULLSCREEN)

print("modeset done, init display")

#lcd = pygame.display.set_mode((896, 512))
#lcd.fill((128,128,0))
pygame.display.update()




print("fontInit")
pygame.font.init()

print("viewtextInit")
r = ViewtextRenderer()
main,flash = r.render(engtest)

# rescale if oversize
#r = main.get_rect().fit(lcd.get_rect())
#main = pygame.transform.smoothscale(main, (r.width, r.height))
#flash = pygame.transform.smoothscale(flash, (r.width, r.height))

# blit to LCD
lcd.blit(main, (0,0))
pygame.display.update()

import time
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()


"""
    lcd.blit(main, (0,0))
    pygame.display.update()
    #time.sleep(1.0)
    
    lcd.blit(flash, (0,0))
    pygame.display.update()
    #time.sleep(0.5)
"""
