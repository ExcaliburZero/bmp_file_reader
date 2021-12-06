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
    def __init__(self, file_handle):
        self.file_handle = file_handle
        self.__bmp_header = None
        self.__dib_header = None

    def read_bmp_file_header(self):
        if self.__bmp_header is not None:
            return self.__bmp_header

        self.file_handle.seek(0)

        header_bytes = self.file_handle.read(14)

        bmp_header = BMPHeader.from_bytes(header_bytes)
        self.__bmp_header = bmp_header

        return bmp_header

    def read_dib_header(self):
        if self.__dib_header is not None:
            return self.__dib_header

        self.file_handle.seek(14)

        dib_header = DIBHeader.from_positioned_file_handler(self.file_handle)
        self.__dib_header = dib_header

        return dib_header

    def get_width(self):
        return self.read_dib_header().width

    def get_height(self):
        return self.read_dib_header().height

    def get_row(self, row):
        PIXEL_SIZE_BYTES = 3

        # Check the file info to make sure we support it
        bits_per_pixel = self.read_dib_header().bits_per_pixel
        if bits_per_pixel != 24:
            raise ValueError(
                f"This parser does not currently support BMP files with {bits_per_pixel} bits per pixel. Currently only 24-bit color values are supported."
            )

        compression_type = self.read_dib_header().compression_type
        if compression_type != CompressionType.BI_RGB:
            raise ValueError(
                f"This parser does not currently support compressed BMP files."
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
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self):
        return f"Color(red={self.red}, green={self.green}, blue={self.blue})"

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
        return f"BMPHeader(bmp_type={self.bmp_type}, size={self.size}, value_1={self.value_1}, value_2={self.value_2}, image_start_offset={self.image_start_offset})"

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
    ):
        self.width = width
        self.height = height
        self.num_color_planes = num_color_planes
        self.bits_per_pixel = bits_per_pixel
        self.compression_type = compression_type
        self.raw_bitmap_size = raw_bitmap_size
        self.horizontal_resolution_ppm = horizontal_resolution_ppm

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
        )

    def __repr__(self):
        return f"""DIBHeader(
    width={self.width},
    height={self.height},
    num_color_planes={self.num_color_planes},
    bits_per_pixel={self.bits_per_pixel},
    compression_type={CompressionType.to_str(self.compression_type)},
    raw_bitmap_size={self.raw_bitmap_size},
    horizontal_resolution_ppm={self.horizontal_resolution_ppm},
)"""

    @staticmethod
    def from_positioned_file_handler(file_handler):
        header_size = int.from_bytes(file_handler.read(4), "little")

        header_bytes_list = list(bytearray(file_handler.read(header_size - 4)))

        width = int.from_bytes(bytes(header_bytes_list[0:4]), "little")
        height = int.from_bytes(bytes(header_bytes_list[4:8]), "little")

        # TODO: parse the rest of the header parts
        num_color_planes = None
        bits_per_pixel = None
        compression_type = None
        raw_bitmap_size = None
        horizontal_resolution_ppm = None

        if header_size >= 40:
            num_color_planes = int.from_bytes(bytes(header_bytes_list[8:10]), "little")
            bits_per_pixel = int.from_bytes(bytes(header_bytes_list[10:12]), "little")
            compression_type = int.from_bytes(bytes(header_bytes_list[12:16]), "little")
            raw_bitmap_size = int.from_bytes(bytes(header_bytes_list[16:20]), "little")
            horizontal_resolution_ppm = int.from_bytes(
                bytes(header_bytes_list[20:24]), "little"
            )

        return DIBHeader(
            width=width,
            height=height,
            num_color_planes=num_color_planes,
            bits_per_pixel=bits_per_pixel,
            compression_type=compression_type,
            raw_bitmap_size=raw_bitmap_size,
            horizontal_resolution_ppm=horizontal_resolution_ppm,
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