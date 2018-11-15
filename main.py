#!/usr/bin/env python3

import pygame
import os
from enum import Enum, auto

class ViewtextState(Enum):
    WAIT_PAGE_HEADER = auto()



class ViewtextRenderer:
    # Viewtext screen area in characters
    VTCOLS  = 40
    VTLINES = 25

    COLOURMAP = (
            (0,     0,      0),     # Black
            (255,   0,      0),     # Red
            (0,     255,    0),     # Green
            (255,   255,    0),     # Yellow
            (0,     0,      255),   # Blue
            (255,   0,      255),   # Magenta
            (0,     255,    255),   # Cyan
            (255,   255,    255)    # White
            )

    def __init__(self, font="MODE7GX3.TTF", fontsize=20, antialias=False):
        # Load the font
        self._font = pygame.font.Font(font, fontsize)
        self._antialias = antialias

        # Get the size of a screen full of Viewtext data
        # assumes monospaced font
        (linew, lineh) = self._font.size("A"*self.VTCOLS)
        self._surfw = linew
        self._surfh = lineh * self.VTLINES
        self._lineh = lineh
        self._charw = linew / self.VTCOLS

    def _charmap(self, cha):
        """
        Private: map character set
        """
        m = {
                0x23: '\u00A3',
                0x24: '\u00A4',
                # 0x40 is @ already
                0x5c: '\u00BD',
                0x5f: '\u0023',
                0x7b: '\u00BC',
                0x7d: '\u00BE',
                0x7e: '\u00F7',
                0x7f: '\u00B6'
            }
        if cha in m:
            return m[cha]
        else:
            return chr(cha)

    def render(self, data, flags=0):
        """
        Render Viewtext

        data: 40x25 2D array containing Viewtext character data.
              This is essentially the Viewtext/Teletext RAM buffer.

        flags: Page control bits
        """
        #assert(len(data) == self.VTLINES)
        #assert(len(data[0]) == self.VTCOLS)

        #state = ViewtextState.WAIT_PAGE_HEADER
        doublehigh = False

        # create two blank output surfaces -- Flash A and Flash B
        surface1 = pygame.Surface((self._surfw, self._surfh))
        surface2 = pygame.Surface((self._surfw, self._surfh))

        cx = 0
        cy = 0

        # Start rendering the data
        for row in data:
            holdgfx = ' '       # Hold Graphics character
            s = ''              # string buffer
            fg = self.COLOURMAP[7]  # reset fg colour to white
            bg = self.COLOURMAP[0]  # reset bg colour to black
            flash = False

            for col in row:
                # single character
                if col < 0x20:
                    # control character -- TODO
                    s = s + ' '

                    # Deal with Set-After codes, which take effect from the
                    # following character.
                    if col < 0x07 or \
                            (col >= 0x10 and col <= 0x17) or \
                            col in (0x08, 0x0A, 0x0B, 0x0D, 0x0E, 0x0F, 0x1B, 0x1F):
                        # Flush the text buffer
                        ts = self._font.render(s, self._antialias, fg, bg)
                        surface1.blit(ts, (cx, cy))
                        if not flash:
                            surface2.blit(ts, (cx, cy))
                        # Update X position and clear output buffer
                        cx += (self._charw * len(s))
                        s = ''

                    # Control code handling

                    if col < 0x07:      # 0x00 to 0x07: Alpha Colour (Set-After)
                        fg = self.COLOURMAP[col]

                    elif col == 0x1C:   # 0x1C: Black Background (Set-At)
                        bg = self.COLOURMAP[0]

                    elif col == 0x1D:   # 0x1D: New Background (Set-At)
                        bg = fg

                else:
                    # text character
                    s = s + self._charmap(col)

            if len(s) > 0:
                # There are characters left in the buffer -- render them
                ts = self._font.render(s, self._antialias, fg, bg)
                surface1.blit(ts, (cx, cy))
                if not flash:
                    surface2.blit(ts, (cx, cy))

            # Reset X/Y position to the start of the following line
            cy += self._lineh
            cx = 0

        return (surface1,surface2)

def DeTTX(s):
    a = bytearray()
    for i in [s[i:i+2] for i in range(0, len(s), 2)]:
        a.append(int(i,16) & 0x7f)

    b = [a[i:i+40] for i in range(0, len(a), 40)]

    return b


#os.putenv('SDL_FBDEV', '/dev/fb1')
#os.putenv('SDL_VIDEODRIVER', 'fbcon') # Force PyGame to PiTFT
pygame.init()
pygame.mouse.set_visible(False)

lcd = pygame.display.set_mode((896, 512))
lcd.fill((128,128,0))
pygame.display.update()

engtest = '8180818081808180818081808180818081808180818081808180818081808180818081808180b0b1979e8ff3939a969e9f98848d9d83c5cec7c9cec5c5d2c9cec7a0929c8c9ef3958e918f948f87b0b2979e8ff3939a969e9f98848d9d83c5cec7c9cec5c5d2c9cec7a0929c8c9ef3958e918f948f87b0b2fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb0b4949a9ef39199958095818da0859d82d4e5f3f4a0d0e1e7e5a0a09c8c9e92f396989380979881b0b5949a9ef39199958095818da0859d82d4e5f3f4a0d0e1e7e5a0a09c8c9e92f396989380979881b0b5818081a080a0819ea09ea097ac9393969692929295959191949494a0a0948081808180818081b0b7fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb0b88180818081808180818081808180818081808180818081808180818081808180818081808180b0b9fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb1b08180818081808180818081808180818081808180818081808180818081808180818081808180b1b1fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb1b28180818081808180818081808180818081808180818081808180818081808180818081808180b1b3fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb1b48180818081808180818081808180818081808180818081808180818081808180818081808180b1b5fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb1b6d7e8e9f4e583d9e5ececeff786c3f9e1ee82c7f2e5e5ee85cde1e7e5eef4e181d2e5e484c2ecf5e5979aa1a2a393a4a5a6a796a8a9aaab92acadaeaf99b0b1b2b395b4b5b6b791b8b9babb94bcbdbebfa0a0a1a2a3a0a4a5a6a7a0a8a9aaaba0acadaeafa0b0b1b2b3a0b4b5b6b7a0b8b9babba0bcbdbebfa0c0c1c2c3a0c4c5c6c7a0c8c9cacba0cccdcecfa0d0d1d2d3a0d4d5d6d7a0d8d9dadba0dcdddedfa0e0e1e2e3a0e4e5e6e7a0e8e9eaeba0ecedeeefa0f0f1f2f3a0f4f5f6f7a0f8f9fafba0fcfdfeff94e0e1e2e391e4e5e6e795e8e9eaeb92ecedeeef9af0f1f2f396f4f5f6f793f8f9fafb97fcfdfeff8398c3efeee3e5e1ec88c6ece1f3e883aa8b8bc2eff889d3f4e5e1e4f998c7efeee58a8abf96deff'

d = [[0x20]*40]
d.extend(DeTTX(engtest))
d.extend([[0x20]*40])

r = ViewtextRenderer()
main,flash = r.render(d)

# rescale if oversize
r = main.get_rect().fit(lcd.get_rect())
main = pygame.transform.smoothscale(main, (r.width, r.height))
flash = pygame.transform.smoothscale(flash, (r.width, r.height))

# blit to LCD

import time
for i in range(5):
    lcd.blit(main, (0,0))
    pygame.display.update()
    time.sleep(1.0)
    
    lcd.blit(flash, (0,0))
    pygame.display.update()
    time.sleep(0.5)
