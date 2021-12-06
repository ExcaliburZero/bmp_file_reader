import unittest

import bmp_file_reader as bmpr


class BMPFileReaderTest(unittest.TestCase):
    def test_read_bmp_file_header(self):
        image_path = "images/single_white_pixel.bmp"

        with open(image_path, "rb") as file_handle:
            reader = bmpr.BMPFileReader(file_handle)

            actual = reader.read_bmp_file_header()

        expected = bmpr.BMPHeader(bmpr.BMPType.BM, 126, b"\x00\x00", b"\x00\x00", 122)

        self.assertEqual(expected, actual)

    def test_read_dib_header(self):
        image_path = "images/single_white_pixel.bmp"

        with open(image_path, "rb") as file_handle:
            reader = bmpr.BMPFileReader(file_handle)

            actual = reader.read_dib_header()

        expected = bmpr.DIBHeader(
            width=1,
            height=1,
            num_color_planes=1,
            bits_per_pixel=24,
            compression_type=bmpr.CompressionType.BI_RGB,
            raw_bitmap_size=4,
            horizontal_resolution_ppm=11811,
            vertical_resolution_ppm=11811,
            num_colors_in_palette=0,
        )

        self.assertEqual(expected, actual)

    def test_get_width_and_height(self):
        image_path = "images/single_white_pixel.bmp"

        with open(image_path, "rb") as file_handle:
            reader = bmpr.BMPFileReader(file_handle)

            actual_width = reader.get_width()
            actual_height = reader.get_height()

        expected_width = 1
        expected_height = 1

        self.assertEqual(expected_width, actual_width)
        self.assertEqual(expected_height, actual_height)

    def test_get_width_and_height_2(self):
        image_path = "images/single_green_pixel.bmp"

        with open(image_path, "rb") as file_handle:
            reader = bmpr.BMPFileReader(file_handle)

            actual_width = reader.get_width()
            actual_height = reader.get_height()

        expected_width = 1
        expected_height = 1

        self.assertEqual(expected_width, actual_width)
        self.assertEqual(expected_height, actual_height)

    def test_get_width_and_height_3(self):
        image_path = "images/small_image_with_colors.bmp"

        with open(image_path, "rb") as file_handle:
            reader = bmpr.BMPFileReader(file_handle)

            actual_width = reader.get_width()
            actual_height = reader.get_height()

        expected_width = 30
        expected_height = 20

        self.assertEqual(expected_width, actual_width)
        self.assertEqual(expected_height, actual_height)

    def test_get_row(self):
        image_path = "images/single_white_pixel.bmp"

        with open(image_path, "rb") as file_handle:
            reader = bmpr.BMPFileReader(file_handle)

            actual = reader.get_row(0)

        expected = [bmpr.Color(255, 255, 255)]

        self.assertEqual(expected, actual)

    def test_get_row_2(self):
        image_path = "images/single_green_pixel.bmp"

        with open(image_path, "rb") as file_handle:
            reader = bmpr.BMPFileReader(file_handle)

            actual = reader.get_row(0)

        expected = [bmpr.Color(red=0, green=255, blue=0)]

        self.assertEqual(expected, actual)

    def test_get_row_3(self):
        image_path = "images/small_image_with_colors.bmp"

        with open(image_path, "rb") as file_handle:
            reader = bmpr.BMPFileReader(file_handle)

            actual = reader.get_row(0)

        expected = [
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=20, green=145, blue=113),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
            bmpr.Color(red=255, green=255, blue=255),
        ]

        self.assertEqual(expected, actual)

    def test_get_row_16bit_colors(self):
        image_path = "images/16_bit_colors.bmp"

        with open(image_path, "rb") as file_handle:
            reader = bmpr.BMPFileReader(file_handle)

            with self.assertRaises(ValueError) as context:
                reader.get_row(0)

            expected_msg = "This parser does not currently support BMP files with 16 bits per pixel. Currently only 24-bit color values are supported."
            self.assertEquals(expected_msg, str(context.exception))

    def test_get_row_16bit_colors(self):
        image_path = "images/32_bit_colors.bmp"

        with open(image_path, "rb") as file_handle:
            reader = bmpr.BMPFileReader(file_handle)

            with self.assertRaises(ValueError) as context:
                reader.get_row(0)

            expected_msg = "This parser does not currently support BMP files with 32 bits per pixel. Currently only 24-bit color values are supported."
            self.assertEquals(expected_msg, str(context.exception))


class DIBHeaderTest(unittest.TestCase):
    def test_repr_simple(self):
        header = bmpr.DIBHeader(
            width=1,
            height=1,
            num_color_planes=1,
            bits_per_pixel=24,
            compression_type=bmpr.CompressionType.BI_RGB,
            raw_bitmap_size=4,
            horizontal_resolution_ppm=11811,
            vertical_resolution_ppm=11811,
            num_colors_in_palette=0,
        )

        actual = repr(header)

        expected = """DIBHeader(
    width=1,
    height=1,
    num_color_planes=1,
    bits_per_pixel=24,
    compression_type=BI_RGB,
    raw_bitmap_size=4,
    horizontal_resolution_ppm=11811,
    vertical_resolution_ppm=11811,
    num_colors_in_palette=0,
)"""

        self.assertEquals(expected, actual)