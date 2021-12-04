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
        # TODO: read from header type
        return self.read_dib_header()[0]

    def get_height(self):
        # TODO: read from header type
        return self.read_dib_header()[1]

    def get_row(self, row):
        PIXEL_SIZE = 3

        height = self.get_height()
        assert row < height

        row_index = (height - row) - 1

        # Rows are padded out to 4 byte alignment
        row_size = int(math.ceil((PIXEL_SIZE * self.get_width()) / 4.0) * 4)

        row_start = (
            self.read_bmp_file_header().image_start_offset + row_size * row_index
        )

        self.file_handle.seek(row_start)

        row_bytes = list(bytearray(self.file_handle.read(row_size)))

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
    @staticmethod
    def from_positioned_file_handler(file_handler):
        header_size = int.from_bytes(file_handler.read(4), "little")

        header_bytes_list = list(bytearray(file_handler.read(header_size)))

        width = int.from_bytes(bytes(header_bytes_list[0:4]), "little")
        height = int.from_bytes(bytes(header_bytes_list[4:8]), "little")

        # TODO: actually parse the whole header and return a proper DIB header type
        return (width, height)


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
