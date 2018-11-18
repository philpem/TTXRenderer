#!/usr/bin/env python3

import pygame

pygame.display.init()

print("Available display modes:")
for mode in pygame.display.list_modes():
    print("   {0} x {1}".format(mode[0], mode[1]))

size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print("Framebuffer size: %d x %d" % (size[0], size[1]))
