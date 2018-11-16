#!/usr/bin/env python3

import pygame
import os
from enum import Enum, auto

class ViewtextRenderer:
    # Viewtext screen area in characters
    VTCOLS  = 40
    VTLINES = 25

    FEAT_FG_BLACK = False

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
        lineh = lineh - 1
        self._surfw = linew
        self._surfh = lineh * self.VTLINES
        self._lineh = lineh
        self._charw = linew / self.VTCOLS

    def _charmap(self, cha, dhrow, mosaic, separated):
        """
        Private: map character set

        dhrow: 0 = normal height, 1=doubleheight row 1, 2=doubleheight row 2
        mosaic: True for mosaic mode
        contiguous: True for contiguous mosaic, False for separated
        """

        if mosaic and not separated:
            # mosaic, contiguous
            if dhrow != 0:
                if dhrow == 1:
                    ofs = 0
                elif dhrow == 2:
                    ofs = 0x40

                if cha >= 0x20 and cha <= 0x3F:
                    return chr(0xE240 + ofs + (cha - 0x20))
                elif cha >= 0x60 and cha <= 0x7F:
                    return chr(0xE260 + ofs + (cha - 0x60))
            else:
                if cha >= 0x20 and cha <= 0x3F:
                    return chr(0xE200 + (cha - 0x20))
                elif cha >= 0x60 and cha <= 0x7F:
                    return chr(0xE220 + (cha - 0x60))
            # 0x40 <= cha <= 0x5F: Fall through to G0 character set

        elif mosaic and separated:
            # mosaic, separated
            if dhrow != 0:
                if dhrow == 1:
                    ofs = 0
                elif dhrow == 2:
                    ofs = 0x40

                if cha >= 0x20 and cha <= 0x3F:
                    return chr(0xE300 + ofs + (cha - 0x20))
                elif cha >= 0x60 and cha <= 0x7F:
                    return chr(0xE320 + ofs + (cha - 0x60))
            else:
                if cha >= 0x20 and cha <= 0x3F:
                    return chr(0xE2C0 + (cha - 0x20))
                elif cha >= 0x60 and cha <= 0x7F:
                    return chr(0xE2E0 + (cha - 0x60))
            # 0x40 <= cha <= 0x5F: Fall through to G0 character set

        # character mode
        if dhrow == 0:      # no double height
            ofs = 0
        elif dhrow == 1:    # top half, double height
            ofs = 0xE000
        elif dhrow == 2:    # bottom half, double height
            ofs = 0xE100

        # character mapping table
        m = {
                0x23: 0xA3,
                0x24: 0xA4,
                0x5c: 0xBD,
                0x5f: 0x23,
                0x7b: 0xBC,
                0x7d: 0xBE,
                0x7e: 0xF7,
                0x7f: 0xB6
            }

        if cha in m:
            return chr(ofs + m[cha])
        else:
            return chr(ofs + cha)


    def render(self, data, flags=0):
        """
        Render Viewtext

        data: 40x25 2D array containing Viewtext character data.
              This is essentially the Viewtext/Teletext RAM buffer.

        flags: Page control bits
        """

        dhrow = 0

        # create two blank output surfaces -- Flash A and Flash B
        surface1 = pygame.Surface((self._surfw, self._surfh))
        surface2 = pygame.Surface((self._surfw, self._surfh))

        cx = 0
        cy = 0

        dhPrevRow = False

        # Start rendering the data
        for row in data:
            s = ''              # string buffer

            # Set start of line condition
            # White text, black background
            fg              = self.COLOURMAP[7]
            bg              = self.COLOURMAP[0]
            # Flash off
            flash           = False
            # Double Height off
            doubleheight    = False
            # Box off -- TODO add page flag
            box             = False
            # Conceal off -- TODO add input flag
            conceal         = False
            # Mosaic characters off, contiguous mode, Hold Mosaic off
            mosaic          = False
            sepMosaic       = False
            holdMosaic      = False
            holdMosaicCh    = ord(' ')
            holdMosaicSep   = False

            # If we had double-height on the last row, this row is the second
            # double-height row.
            # If this is the second double-height row, reset double-height.
            if dhrow == 1:
                dhrow = 2
            elif dhrow == 2:
                dhrow = 0

            for col in row:
                if dhrow == 2:
                    # ETS 300 706 s12.3 "0/D: Double Height"
                    # When double height (or double size) characters are used on a given row, the row
                    # below normal height characters on that row is displayed with the same local
                    # background colour and no foreground data.
                    continue

                # single character
                if col < 0x20:
                    # It's a control character

                    # Deal with Set-After codes, which take effect from the
                    # following character.
                    if col <= 0x07 or \
                            (col >= 0x10 and col <= 0x17) or \
                            col in (0x08, 0x0A, 0x0B, 0x0D, 0x0E, 0x0F, 0x1B, 0x1F):
                        # this is a set-after code, preload a blank
                        if holdMosaic:
                            if conceal: # TODO: 'and not Flags.REVEAL'
                                s = s + ' '
                            elif doubleheight:
                                s = s + self._charmap(holdMosaicCh, dhrow, True, holdMosaicSep)
                            else:
                                s = s + self._charmap(holdMosaicCh, 0, True, holdMosaicSep)
                        else:
                            s = s + ' '
                        setAfter = True
                    else:
                        setAfter = False

                    # Flush the text buffer
                    ts = self._font.render(s, self._antialias, fg, bg)
                    surface1.blit(ts, (cx, cy))
                    if not flash:
                        surface2.blit(ts, (cx, cy))
                    # Update X position and clear output buffer
                    cx += (self._charw * len(s))
                    s = ''

                    # Control code handling

                    if (col <= 0x07) or (col >= 0x10 and col <= 0x17):
                                        # 0x00 to 0x07: Alpha Colour (Set-After)
                                        # 0x10 to 0x17: Mosaic Colour (Set-After)
                        # TODO: Alpha Black only takes effect on some decoders (see ETSI ETS 300 706)
                        #       What does Teletext Level 1 spec say we should do here?
                        mosaic = (col >= 0x10)
                        c = col & 0x07
                        if (c == 0 and self.FEAT_FG_BLACK) or (c != 0x00):
                            fg = self.COLOURMAP[c]
                        conceal = False

                    elif col == 0x08:   # 0x08: Flash (Set-After)
                        flash = True

                    elif col == 0x09:   # 0x09: Flash (Set-At)
                        flash = False

                    elif col == 0x0A:   # 0x0A: End Box (Set-After)
                        box = False     # TODO

                    elif col == 0x0B:   # 0x0B: Start Box (Set-After)
                        box = True      # TODO

                    elif col == 0x0C:   # 0x0C: Normal size (Set-At)
                        if doubleheight:
                            holdMosaicCh = ord(' ')
                        doubleheight = False

                    elif col == 0x0D:   # 0x0D: Double Height (Set-After)
                        if not doubleheight:
                            holdMosaicCh = ord(' ')
                        # If the doubleheight character code offset is set to
                        # "top half", set it to "bottom half". Otherwise set
                        # it to "top half".
                        if dhrow == 0:
                            dhrow = 1
                        doubleheight = True
                        dhPrevRow = True

                    # 0x0E: Level 2.5 and 3.5: Double Width (Set-After) -- TODO
                    # 0x0F: Level 2.5 and 3.5: Double Size  (Set-After) -- TODO

                    # 0x10-0x17 are handled above (Mosaic Colour)

                    elif col == 0x18:   # 0x18: Conceal (Set-At)
                        conceal = True

                    elif col == 0x19:   # 0x19: Contiguous Mosaic characters (Set-At)
                        sepMosaic = False

                    elif col == 0x1A:   # 0x1A: Separated Mosaic characters (Set-At)
                        sepMosaic = True

                    # TODO: 0x1B / Escape

                    elif col == 0x1C:   # 0x1C: Black Background (Set-At)
                        bg = self.COLOURMAP[0]

                    elif col == 0x1D:   # 0x1D: New Background (Set-At)
                        bg = fg

                    elif col == 0x1E:   # 0x1E: Hold Mosaic on (Set-At)
                        holdMosaic = True

                    elif col == 0x1F:   # 0x1F: Hold Mosaic off (Set-At)
                        holdMosaic = False

                    # If this was a Set-At code, load a space with the new
                    # attributes into the buffer
                    if not setAfter:
                        if holdMosaic:
                            if conceal: # TODO: 'and not Flags.REVEAL'
                                s = s + ' '
                            elif doubleheight:
                                s = s + self._charmap(holdMosaicCh, dhrow, True, holdMosaicSep)
                            else:
                                s = s + self._charmap(holdMosaicCh, 0, True, holdMosaicSep)
                        else:
                            s = s + ' '

                else:
                    if holdMosaic and (col & 0x20) and mosaic:
                        holdMosaicCh = col
                        holdMosaicSep = sepMosaic

                    # text character
                    if conceal: # TODO: 'and not Flags.REVEAL'
                        s = s + ' '
                    elif doubleheight:
                        s = s + self._charmap(col, dhrow, mosaic, sepMosaic)
                    else:
                        s = s + self._charmap(col, 0, mosaic, sepMosaic)

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
#main = pygame.transform.smoothscale(main, (r.width, r.height))
#flash = pygame.transform.smoothscale(flash, (r.width, r.height))

# blit to LCD

import time
for i in range(5):
    lcd.blit(main, (0,0))
    pygame.display.update()
    time.sleep(1.0)
    
    lcd.blit(flash, (0,0))
    pygame.display.update()
    time.sleep(0.5)
