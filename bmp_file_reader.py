# MIT License
#
# Copyright (c) 2021 Christopher Wells
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math


class BMPFileReader:
    """
    An object for reading a BMP image file.
    """

    def __init__(self, file_handle):
        """
        Creates a BMPFileReader from the given file handle.

        The file handle must have been opened in read binary mode ("rb").

        :param file_handle: The file handle of the BMP image to read.
        :type file_handle: io.TextIOWrapper
        """
        self.file_handle = file_handle
        self.__bmp_header = None
        self.__dib_header = None

    def read_bmp_file_header(self):
        """
        Returns the BMP file header of the image.

        :return: BMP file header of the image.
        :rtype: BMPHeader
        """
        if self.__bmp_header is not None:
            return self.__bmp_header

        self.file_handle.seek(0)

        header_bytes = self.file_handle.read(14)

        bmp_header = BMPHeader.from_bytes(header_bytes)
        self.__bmp_header = bmp_header

        return bmp_header

    def read_dib_header(self):
        """
        Returns the DIB header of the BMP file.

        :return: DIB header of the image.
        :rtype: DIBHeader
        """
        if self.__dib_header is not None:
            return self.__dib_header

        self.file_handle.seek(14)

        dib_header = DIBHeader.from_positioned_file_handler(self.file_handle)
        self.__dib_header = dib_header

        return dib_header

    def get_width(self):
        """
        Returns the width of the image (in pixels).

        :return: Width of the image in pixels.
        :rtype: int
        """
        return self.read_dib_header().width

    def get_height(self):
        """
        Returns the height of the image (in pixels).

        :return: Height of the image in pixels.
        :rtype: int
        """
        return self.read_dib_header().height

    def get_row(self, row):
        """
        Reads in the pixels of the specified row (zero-indexed).

        :param row: The index of the row to read.
        :type row: int
        :return: The colors of the pixels in the specified row.
        :rtype: List[Color]
        """
        PIXEL_SIZE_BYTES = 3

        # Check the file info to make sure we support it
        bits_per_pixel = self.read_dib_header().bits_per_pixel
        if bits_per_pixel != 24:
            raise ValueError(
                "This parser does not currently support BMP files with {} bits per pixel. Currently only 24-bit color values are supported.".format(bits_per_pixel)
            )

        compression_type = self.read_dib_header().compression_type
        if compression_type != CompressionType.BI_RGB:
            raise ValueError(
                "This parser does not currently support compressed BMP files."
            )

        # Prepare to start parsing the row
        height = self.get_height()
        assert row < height

        row_index = (height - row) - 1

        # Rows are padded out to 4 byte alignment
        row_size = int(math.ceil((PIXEL_SIZE_BYTES * self.get_width()) / 4.0) * 4)

        row_start = (
            self.read_bmp_file_header().image_start_offset + row_size * row_index
        )

        # Read in the row information from the file
        self.file_handle.seek(row_start)

        row_bytes = list(bytearray(self.file_handle.read(row_size)))

        # Parse the pixel color information for the row
        pixels = []
        i = 0
        while i < self.get_width():
            start = i * 3
            end = (i + 1) * 3

            pixels.append(Color.from_bytes(row_bytes[start:end]))

            i += 1

        return pixels


class Color:
    """
    A 24bit RGB color value.
    """

    red = 0
    green = 0
    blue = 0

    def __init__(self, red, green, blue):
        """
        Creates a Color from the given 1 byte red, green, and blue color values.

        :param red: The 1 byte red value.
        :type red: int
        :param green: The 1 byte green value.
        :type green: int
        :param blue: The 1 byte blue value.
        :type blue: int
        """
        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self):
        return "Color(red={}, green={}, blue={})".format(self.red, self.green, self.blue)

    def __eq__(self, other):
        if not isinstance(other, Color):
            return False

        return (
            self.red == other.red
            and self.green == other.green
            and self.blue == other.blue
        )

    @staticmethod
    def from_bytes(color_bytes):
        blue = color_bytes[0]
        green = color_bytes[1]
        red = color_bytes[2]

        return Color(red, green, blue)


class BMPHeader:
    def __init__(self, bmp_type, size, value_1, value_2, image_start_offset):
        self.bmp_type = bmp_type
        self.size = size
        self.value_1 = value_1
        self.value_2 = value_2
        self.image_start_offset = image_start_offset

    def __repr__(self):
        return "BMPHeader(bmp_type={}, size={}, value_1={}, value_2={}, image_start_offset={})".format(
            self.bmp_type, self.size, self.value_1, self.value_2, self.image_start_offset
        )

    def __eq__(self, other):
        if not isinstance(other, BMPHeader):
            return False

        return (
            self.bmp_type == other.bmp_type
            and self.size == other.size
            and self.value_1 == other.value_1
            and self.value_2 == other.value_2
            and self.image_start_offset == other.image_start_offset
        )

    @staticmethod
    def from_bytes(header_bytes):
        header_bytes_list = list(bytearray(header_bytes))

        bmp_type = BMPType.from_bytes(header_bytes_list[0:2])
        size = int.from_bytes(bytes(header_bytes_list[2:6]), "little")
        value_1 = bytes(header_bytes_list[6:8])
        value_2 = bytes(header_bytes_list[8:10])
        image_start_offset = int.from_bytes(bytes(header_bytes_list[10:14]), "little")

        return BMPHeader(bmp_type, size, value_1, value_2, image_start_offset)


class DIBHeader:
    def __init__(
        self,
        width,
        height,
        num_color_planes,
        bits_per_pixel,
        compression_type,
        raw_bitmap_size,
        horizontal_resolution_ppm,
        vertical_resolution_ppm,
        num_colors_in_palette,
        num_important_colors_used,
    ):
        self.width = width
        self.height = height
        self.num_color_planes = num_color_planes
        self.bits_per_pixel = bits_per_pixel
        self.compression_type = compression_type
        self.raw_bitmap_size = raw_bitmap_size
        self.horizontal_resolution_ppm = horizontal_resolution_ppm
        self.vertical_resolution_ppm = vertical_resolution_ppm
        self.num_colors_in_palette = num_colors_in_palette
        self.num_important_colors_used = num_important_colors_used

    def __eq__(self, other):
        if not isinstance(other, DIBHeader):
            return False

        return (
            self.width == other.width
            and self.height == other.height
            and self.num_color_planes == other.num_color_planes
            and self.bits_per_pixel == other.bits_per_pixel
            and self.compression_type == other.compression_type
            and self.raw_bitmap_size == other.raw_bitmap_size
            and self.horizontal_resolution_ppm == other.horizontal_resolution_ppm
            and self.vertical_resolution_ppm == other.vertical_resolution_ppm
            and self.num_colors_in_palette == other.num_colors_in_palette
            and self.num_important_colors_used == other.num_important_colors_used
        )

    def __repr__(self):
        return """DIBHeader(
    width={},
    height={},
    num_color_planes={},
    bits_per_pixel={},
    compression_type={},
    raw_bitmap_size={},
    horizontal_resolution_ppm={},
    vertical_resolution_ppm={},
    num_colors_in_palette={},
    num_important_colors_used={},
)""".format(
            self.width,
            self.height,
            self.num_color_planes,
            self.bits_per_pixel,
            CompressionType.to_str(self.compression_type),
            self.raw_bitmap_size,
            self.horizontal_resolution_ppm,
            self.vertical_resolution_ppm,
            self.num_colors_in_palette,
            self.num_important_colors_used,
        )

    @staticmethod
    def from_positioned_file_handler(file_handler):
        # Based on info from:
        # https://en.wikipedia.org/wiki/BMP_file_format#DIB_header_(bitmap_information_header)

        header_size = int.from_bytes(file_handler.read(4), "little")

        if header_size <= 0:
            raise ValueError("BMP header has invalid header size: " + str(header_size))
        elif header_size > 100000:
            raise ValueError("BMP header looks like it may be too big (header_size=" + str(header_size) + ").")

        try:
            header_bytes_list = list(bytearray(file_handler.read(header_size - 4)))
        except MemoryError:
            raise MemoryError("MemoryError when trying to read BMP file header. header_size=" + str(header_size))

        width = None
        height = None
        num_color_planes = None
        bits_per_pixel = None
        compression_type = None
        raw_bitmap_size = None
        horizontal_resolution_ppm = None
        vertical_resolution_ppm = None
        num_colors_in_palette = None
        num_important_colors_used = None

        # BITMAPINFOHEADER or higher version
        if header_size in [40, 52, 56, 108, 124] or header_size > 124:
            width = int.from_bytes(bytes(header_bytes_list[0:4]), "little")
            height = int.from_bytes(bytes(header_bytes_list[4:8]), "little")
            num_color_planes = int.from_bytes(bytes(header_bytes_list[8:10]), "little")
            bits_per_pixel = int.from_bytes(bytes(header_bytes_list[10:12]), "little")
            compression_type = int.from_bytes(bytes(header_bytes_list[12:16]), "little")
            raw_bitmap_size = int.from_bytes(bytes(header_bytes_list[16:20]), "little")
            horizontal_resolution_ppm = int.from_bytes(
                bytes(header_bytes_list[20:24]), "little"
            )
            vertical_resolution_ppm = int.from_bytes(
                bytes(header_bytes_list[24:28]), "little"
            )
            num_colors_in_palette = int.from_bytes(
                bytes(header_bytes_list[28:32]), "little"
            )
            num_important_colors_used = int.from_bytes(
                bytes(header_bytes_list[32:36]), "little"
            )
        else:
            # Note: Might add some support for older headers in the future, but I don't know how to
            # generate BMP files with them, so maybe not.
            raise ValueError(
                "BMP file looks like it might be using an old BMP DIB header that we do not support."
            )

        return DIBHeader(
            width=width,
            height=height,
            num_color_planes=num_color_planes,
            bits_per_pixel=bits_per_pixel,
            compression_type=compression_type,
            raw_bitmap_size=raw_bitmap_size,
            horizontal_resolution_ppm=horizontal_resolution_ppm,
            vertical_resolution_ppm=vertical_resolution_ppm,
            num_colors_in_palette=num_colors_in_palette,
            num_important_colors_used=num_important_colors_used,
        )


# Note: Can't use enum here, since MicroPython doesn't currently have an enum standard library
class BMPType:
    BM = 0
    BA = 1
    CI = 2
    CP = 3
    IC = 4
    PT = 5

    @staticmethod
    def from_bytes(bmp_type_bytes):
        type_str = bytes(bmp_type_bytes).decode()

        if type_str == "BM":
            return BMPType.BM
        elif type_str == "BA":
            return BMPType.BA
        elif type_str == "CI":
            return BMPType.CI
        elif type_str == "CP":
            return BMPType.CP
        elif type_str == "IC":
            return BMPType.IC
        elif type_str == "PT":
            return BMPType.PT
        else:
            raise ValueError(f'Invalid BMP type: "{type_str}"')


class CompressionType:
    BI_RGB = 0
    BI_RLE8 = 1
    BI_REL4 = 2
    BI_BITFIELDS = 3
    BI_JPEG = 4
    BI_PNG = 5
    BI_ALPHABITFIELDS = 6
    BI_CMYK = 11
    BI_CMYKRLE8 = 12
    BI_CMYKRLE4 = 13

    STRINGS_DICT = {
        0: "BI_RGB",
        1: "BI_RLE8",
        2: "BI_REL4",
        3: "BI_BITFIELDS",
        4: "BI_JPEG",
        5: "BI_PNG",
        6: "BI_ALPHABITFIELDS",
        11: "BI_CMYK",
        12: "BI_CMYKRLE8",
        13: "BI_CMYKRLE4",
    }

    @staticmethod
    def to_str(compression_type):
        return CompressionType.STRINGS_DICT.get(compression_type, str(compression_type))

    @staticmethod
    def is_compressed(compression_type):
        return compression_type not in [CompressionType.BI_RGB, CompressionType.BI_CMYK]
