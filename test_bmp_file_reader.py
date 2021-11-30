import unittest

import bmp_file_reader as bmpr


class BMPFileReaderTest(unittest.TestCase):
    def test_read_header(self):
        image_path = "images/single_white_pixel.bmp"

        with open(image_path, "rb") as file_handle:
            reader = bmpr.BMPFileReader(file_handle)

            actual = reader.read_file_header()

        expected = bmpr.BMPHeader(bmpr.BMPType.BM, 126, b"\x00\x00", b"\x00\x00", 122)

        self.assertEqual(expected, actual)