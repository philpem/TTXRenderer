import pygame
import pygame.freetype
import pygame.ftfont
import os

class ViewtextRenderer:
    # Viewtext screen area in characters
    VTCOLS  = 40
    VTLINES = 25

    # Feature code -- enable black foreground.
    # Not compatible with Teletext level 1.0 or 1.5
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

    def __init__(self, font="bedstead", fontsize=20, antialias=True):
        pygame.freetype.init()

        # Load the font
        if font == "bedstead":
            self._font = pygame.ftfont.Font("fonts/bedstead.otf", fontsize)
            self._font2 = pygame.ftfont.Font("fonts/bedstead-ultracondensed.otf", fontsize*2)
            self.mapper = self._charmap_bedstead
        else:
            self._font = pygame.ftfont.Font(font, fontsize)
            self._font2 = None
            self.mapper = self._charmap_mode7
        self._antialias = antialias

        # Get the size of a screen full of Viewtext data
        # assumes monospaced font
        (linew, lineh) = self._font.size("A"*self.VTCOLS)
        lineh = lineh - 1   # fudge factor
        self._surfw = linew
        self._surfh = lineh * self.VTLINES
        self._lineh = lineh
        self._charw = linew / self.VTCOLS

    def _charmap_bedstead(self, cha, dhrow, mosaic, separated):
        """
        Private: map character set -- for Bedstead font

        dhrow:
            0 = normal height
            1 = double-height row 1
            2 = double-height row 2
        mosaic:
            True for mosaic graphics mode
        separated:
            False for contiguous mosaic
            True for separated mosaic
        """

        if mosaic and not separated:
            # mosaic, contiguous
            if cha >= 0x20 and cha <= 0x3F:
                return chr(0xEE00 + (cha - 0x20))
            elif cha >= 0x60 and cha <= 0x7F:
                return chr(0xEE40 + (cha - 0x60))
            # 0x40 <= cha <= 0x5F: Fall through to G0 character set

        elif mosaic and separated:
            # mosaic, separated
            if cha >= 0x20 and cha <= 0x3F:
                return chr(0xEE20 + (cha - 0x20))
            elif cha >= 0x60 and cha <= 0x7F:
                return chr(0xEE60 + (cha - 0x60))
        # 0x40 <= cha <= 0x5F: Fall through to G0 character set

        # character mapping table
        m = {
                0x23: 0xA3,     # 2/3: ASCII # => £
                0x24: 0x24,     # 2/4: ASCII $ => $
                0x40: 0x40,     # 4/0: ASCII @ => @
                0x5b: 0x2190,   # 5/B: ASCII [ => left arrow
                0x5c: 0xBD,     # 5/C: ASCII \ => 1/2 fraction
                0x5d: 0x2192,   # 5/D: ASCII ] => right arrow
                0x5e: 0x2191,   # 5/E: ASCII ^ => up arrow
                0x5f: 0x23,     # 5/F: ASCII _ => #
                0x60: 0x2014,   # 6/0: ASCII ` => emdash
                0x7b: 0xBC,     # 7/B: ASCII { => 1/4 fraction
                0x7c: 0x2016,   # 7/C: ASCII | => ||
                0x7d: 0xBE,     # 7/D: ASCII } => 3/4 fraction
                0x7e: 0xF7,     # 7/E: ASCII ~ => divide
                0x7f: 0x25a0    # 7/F: ASCII DEL => square block
            }

        if cha in m:
            return chr(m[cha])
        else:
            return chr(cha)



    def _charmap_mode7(self, cha, dhrow, mosaic, separated):
        """
        Private: map character set -- for MODE7 font

        dhrow:
            0 = normal height
            1 = double-height row 1
            2 = double-height row 2
        mosaic:
            True for mosaic graphics mode
        separated:
            False for contiguous mosaic
            True for separated mosaic
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


    def render(self, data, reveal=True):
        """
        Render Viewtext

        data:    40x25 2D array containing Viewtext character data.
                 This is essentially the Viewtext/Teletext RAM buffer.
        reveal:  True if the REVEAL button has been pressed.
                 Makes CONCEALed screen elements visible.

        Returns a tuple:
            (solid, blink)
            solid:  pygame Surface with flashing elements drawn
            blink:  pygame Surface with flashing elements blanked

        To draw the Viewtext page correctly, the two frames should be drawn
        on screen alternately with a delay of around 1.7 seconds between
        page 'switches'. This will make flashing text flash.

        TODO: Page control bits
        """

        def flushTextBuf():
            # Flush the text buffer
            # This saves us repeating ourselves in the enclosing function
            if doubleheight and self._font2 is not None:
                ts = self._font2.render(s, self._antialias, fg, bg)
            else:
                ts = self._font.render(s, self._antialias, fg, bg)

            surface1.blit(ts, (cx, cy))
            if not flash:
                surface2.blit(ts, (cx, cy))

        # create two blank output surfaces -- Flash A and Flash B
        surface1 = pygame.Surface((self._surfw, self._surfh))
        surface2 = pygame.Surface((self._surfw, self._surfh))

        # Set start of page conditions
        #   Reset X/Y position to (0,0)
        #   Disable double-height
        cx = 0
        cy = 0
        dhrow = 0

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
            # Conceal off
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
                row = prevRow       # ETS 300 706: Double height row 2 uses data from the previous row
            elif dhrow == 2:
                dhrow = 0

            # Save the previous row (see above re. ETS 300 706 handling of double-height)
            prevRow = row

            for col in row:
                # Mask off the MSB (sometimes set in image files)
                col &= 0x7F

                # process control characters
                if col < 0x20:
                    # It's a control character

                    # Deal with Set-After codes, which take effect from the
                    # following character.
                    if col <= 0x07 or \
                            (col >= 0x10 and col <= 0x17) or \
                            col in (0x08, 0x0A, 0x0B, 0x0D, 0x0E, 0x0F, 0x1B, 0x1F):
                        # this is a set-after code, preload a blank
                        if holdMosaic:
                            if conceal and not reveal:
                                s = s + ' '
                            elif doubleheight:
                                s = s + self.mapper(holdMosaicCh, dhrow, True, holdMosaicSep)
                            else:
                                s = s + self.mapper(holdMosaicCh, 0, True, holdMosaicSep)
                        else:
                            s = s + ' '
                        setAfter = True
                    else:
                        setAfter = False

                    # Flush the text buffer
                    flushTextBuf()

                    # Update X position and clear output buffer
                    cx += (self._charw * len(s))
                    s = ''

                    # Control code handling

                    if (col <= 0x07) or (col >= 0x10 and col <= 0x17):
                                        # 0x00 to 0x07: Alpha Colour (Set-After)
                                        # 0x10 to 0x17: Mosaic Colour (Set-After)
                        # TODO: Alpha Black only takes effect on some decoders (see ETSI ETS 300 706)
                        #       What does Teletext Level 1 spec say we should do here?
                        if (col != 0 and col != 0x10) or self.FEAT_FG_BLACK:
                            fg = self.COLOURMAP[col & 0x07]

                            if (mosaic != (col >= 0x10)):
                                # The "Held-Mosaic" character is reset to "SPACE" at the start of each
                                # row, on a change of alphanumeric/mosaics mode or on a change of size
                                holdMosaicCh = ord(' ')

                            mosaic = (col >= 0x10)
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
                        # The "Held-Mosaic" character is reset to "SPACE" at the start of each
                        # row, on a change of alphanumeric/mosaics mode or on a change of size
                        if not doubleheight:
                            holdMosaicCh = ord(' ')

                        # If doubleheight isn't enabled, enable it
                        if dhrow == 0:
                            dhrow = 1
                        doubleheight = True

                        # If we're using the Bedstead font and this is line 2, we need to stop rendering at the first
                        # instance of the Double Height code.
                        if self._font2 is not None and dhrow == 2:
                            break

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
                            if conceal and not reveal:
                                s = s + ' '
                            elif doubleheight:
                                s = s + self.mapper(holdMosaicCh, dhrow, True, holdMosaicSep)
                            else:
                                s = s + self.mapper(holdMosaicCh, 0, True, holdMosaicSep)
                        else:
                            s = s + ' '

                else:   # not col < 0x20
                    if (not doubleheight) and dhrow == 2:
                        col = 32

                    if (col & 0x20) and mosaic:
                        holdMosaicCh = col
                        holdMosaicSep = sepMosaic

                    # text character
                    if conceal and not reveal:
                        s = s + ' '
                    elif doubleheight:
                        s = s + self.mapper(col, dhrow, mosaic, sepMosaic)
                    else:
                        s = s + self.mapper(col, 0, mosaic, sepMosaic)

            if len(s) > 0:
                # There are characters left in the buffer -- render them
                flushTextBuf()


            # Reset X/Y position to the start of the following line
            cy += self._lineh
            cx = 0

        return (surface1,surface2)

