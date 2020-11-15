def DeTTX(s):
    """
    Convert Hexadecimal Teletext code (from the Galax TTX editor) into a bytearray
    """
    a = bytearray()
    for i in [s[i:i+2] for i in range(0, len(s), 2)]:
        a.append(int(i,16) & 0x7f)

    b = [a[i:i+40] for i in range(0, len(a), 40)]

    return b

def LoadEP1(filename):
    """
    Load an EP1 file into an array

    Note that EP1 files do not include the reserved 25th line, which edit.tf
    allows the user to edit.
    """
    with open(filename, "rb") as f:
        header = f.read(6)
        # EP1 header is FE:01:09:00:00:00
        if header[0] != 0xFE and header[1] != 0x01 and header[2] != 0x09:
            raise IOError("Header mismatch")

        # Now 24 lines of 40 characters follow (the header is omitted)
        data = bytearray(f.read(24*40))

        # Finally there are two null bytes we can safely ignore

    data_lines = [data[i:i+40] for i in range(0, len(data), 40)]
    return data_lines

def LoadRaw(filename):
    """
    Load raw files from edit.tf (Raw 0x00-0x7f)
    ZXNet calls this "Binary dump of Level 1 Page Data"
    """

    with open(filename, "rb") as f:
        # Now 24 lines of 40 characters follow (the header is omitted)
        data = bytearray(f.read())

    # Identify whether this file has LF or CRLF line endings, or none at all
    if len(data) == (24*40) or len(data) == (25*40):
        # raw data, no CRLF
        data_lines = [data[i:i+40] for i in range(0, len(data), 40)]
    elif len(data) == (24*41) or len(data) == (25*41):
        # raw data with LF line endings
        data_lines = [data[i:i+40] for i in range(0, len(data), 41)]
    elif len(data) == (24*42) or len(data) == (25*42):
        # raw data with CRLF line endings
        data_lines = [data[i:i+40] for i in range(0, len(data), 42)]
    else:
        raise IOError("Invalid Teletext-Raw file")

    return data_lines


def CeefaxEngtest():
    # Ceefax Engineering Test Page
    engtest = '8180818081808180818081808180818081808180818081808180818081808180818081808180b0b1979e8ff3939a969e9f98848d9d83c5cec7c9cec5c5d2c9cec7a0929c8c9ef3958e918f948f87b0b2979e8ff3939a969e9f98848d9d83c5cec7c9cec5c5d2c9cec7a0929c8c9ef3958e918f948f87b0b2fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb0b4949a9ef39199958095818da0859d82d4e5f3f4a0d0e1e7e5a0a09c8c9e92f396989380979881b0b5949a9ef39199958095818da0859d82d4e5f3f4a0d0e1e7e5a0a09c8c9e92f396989380979881b0b5818081a080a0819ea09ea097ac9393969692929295959191949494a0a0948081808180818081b0b7fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb0b88180818081808180818081808180818081808180818081808180818081808180818081808180b0b9fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb1b08180818081808180818081808180818081808180818081808180818081808180818081808180b1b1fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb1b28180818081808180818081808180818081808180818081808180818081808180818081808180b1b3fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb1b48180818081808180818081808180818081808180818081808180818081808180818081808180b1b5fefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffefffeffb1b6d7e8e9f4e583d9e5ececeff786c3f9e1ee82c7f2e5e5ee85cde1e7e5eef4e181d2e5e484c2ecf5e5979aa1a2a393a4a5a6a796a8a9aaab92acadaeaf99b0b1b2b395b4b5b6b791b8b9babb94bcbdbebfa0a0a1a2a3a0a4a5a6a7a0a8a9aaaba0acadaeafa0b0b1b2b3a0b4b5b6b7a0b8b9babba0bcbdbebfa0c0c1c2c3a0c4c5c6c7a0c8c9cacba0cccdcecfa0d0d1d2d3a0d4d5d6d7a0d8d9dadba0dcdddedfa0e0e1e2e3a0e4e5e6e7a0e8e9eaeba0ecedeeefa0f0f1f2f3a0f4f5f6f7a0f8f9fafba0fcfdfeff94e0e1e2e391e4e5e6e795e8e9eaeb92ecedeeef9af0f1f2f396f4f5f6f793f8f9fafb97fcfdfeff8398c3efeee3e5e1ec88c6ece1f3e883aa8b8bc2eff889d3f4e5e1e4f998c7efeee58a8abf96deff'

    d = [[0x20]*40]
    d.extend(DeTTX(engtest))
    d.extend([[0x20]*40])
    return d


def ETS300706Test():
    def ovr(a, s, ofs=0):
        a[ofs:ofs+len(s)] = [ord(x) for x in s]

    # Create a page of spaces to start from
    d = []
    for i in range(25):
        d.append([0x20]*40)

    ovr(d[0], '      ETS 300 706 (May 1997) Test Page')

    ovr(d[1],  'G.3.1 - Start Box and End Box')
    ovr(d[2],  '  X\x0B\x0B\x61\x0A\x0A')
    ovr(d[4],  '  X\x0B\x0B\x61\x0A\x0A')

    ovr(d[6],  'G.3.2 - Separated Mosaic Graphics')
    ovr(d[7],  '  -->\x17\x39\x1A\x39')
    ovr(d[9],  '  -->\x17\x39\x1A\x39')

    ovr(d[10], 'G.3.3 - Hold, Release & Separated Mosaic')
    ovr(d[11],  '  -->\x17\x66\x1E\x39\x1A\x1F\x66')
    ovr(d[13],  '  -->\x17\x66\x1E\x39\x1A\x1F\x66')

    return d
