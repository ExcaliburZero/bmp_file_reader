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

        # TODO: use a proper DIB header type
        expected = (1, 1)

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