import unittest


class RomReader(object):
    def __init__(self, path):
        self.rom_path = path

        self._header = None
        self.PRG_ROM = None
        self.CHR_ROM = None
        self._prg_count = None
        self._chr_count = None
        self._flag6 = None
        self._flag7 = None

    def parse_header(self, data):
        # Header: 'NES\x1a'
        self._header = data[:4]

        # Number of 16384 byte program ROM pages
        self._prg_count = ord(data[4])

        # Number of 8192 byte character ROM pages (0 indicates CHR RAM)
        self._chr_count = ord(data[5])


        """
        Flag 6

        7       0
        ---------
        NNNN FTBM

        N: Lower 4 bits of the mapper number
        F: Four screen mode. 0 = no, 1 = yes. (When set, the M bit has no effect)
        T: Trainer.  0 = no trainer present, 1 = 512 byte trainer at 7000-71FFh
        B: SRAM at 6000-7FFFh battery backed.  0= no, 1 = yes
        M: Mirroring.  0 = horizontal, 1 = vertical.
        """
        self._flag6 = ord(data[6])


        """
        Flag 7
        7       0
        ---------
        NNNN xxPV

        N: Upper 4 bits of the mapper number
        P: Playchoice 10.  When set, this is a PC-10 game
        V: Vs. Unisystem.  When set, this is a Vs. game
        x: these bits are not used in iNES.
        """
        self._flag7 = ord(data[7])

        self.mapper_id = (self._flag7 & 0xf0) | ((self._flag6 & 0xf0) >> 4)
        print(self.mapper_id)
        # import pdb; pdb.set_trace()

    def read(self):

        with open(self.rom_path, 'rb') as rom_file:

            self.parse_header(rom_file.read(16))

            # Read trainer if it exists
            if self._flag6 & 0b100:
                self._trainer = rom_file.read(512)

            # Read PRG ROM (16384 sized banks)
            self.PRG_ROM = rom_file.read(self._prg_count * 0x4000)

            # Read CHR ROM (8192 sized banks)
            self.CHR_ROM = rom_file.read(self._chr_count * 0x2000)


class RomReaderTestCase(unittest.TestCase):
    def test_read_header(self):
        rom_reader = RomReader('mario.nes')
        rom_reader.read()

        self.assertEqual('NES\x1a', rom_reader._header)
        self.assertEqual(4, rom_reader._prg_count)
        self.assertEqual(2, rom_reader._chr_count)

        self.assertEqual(65536, len(rom_reader.PRG_ROM))
        self.assertEqual(16384, len(rom_reader.CHR_ROM))

        self.assertEqual(66, rom_reader.mapper_id)


if __name__ == '__main__':
    unittest.main()
