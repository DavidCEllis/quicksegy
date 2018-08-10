import struct
from enum import IntEnum

from quicksegy.internals import struct_utils


class SampleFormat(IntEnum):
    IBM_FLOAT = 1
    INT32 = 2
    INT16 = 3
    FIXED_POINT = 4
    IEEE_FLOAT = 5
    IEEE_DOUBLE = 6
    INT24 = 7  # UNSUPPORTED
    CHAR = 8
    INT64 = 9
    UINT32 = 10
    UINT16 = 11
    UINT64 = 12
    UINT24 = 13  # UNSUPPORTED
    UCHAR = 14

    def get_self(self):
        return self

    @property
    def as_struct(self):
        try:
            return format_to_struct[self]
        except KeyError:
            raise NotImplementedError(f'{self.name} not currently supported.') from None

    @property
    def size(self):
        return struct.calcsize('>' + self.as_struct)


format_to_struct = {
    SampleFormat.IBM_FLOAT: struct_utils.UINT32,
    SampleFormat.INT32: struct_utils.INT32,
    SampleFormat.INT16: struct_utils.INT16,
    SampleFormat.IEEE_FLOAT: struct_utils.FLOAT,
    SampleFormat.IEEE_DOUBLE: struct_utils.DOUBLE,
    SampleFormat.CHAR: struct_utils.CHAR,
    SampleFormat.INT64: struct_utils.INT64,
    SampleFormat.UINT32: struct_utils.UINT32,
    SampleFormat.UINT16: struct_utils.UINT16,
    SampleFormat.UINT64: struct_utils.UINT64,
    SampleFormat.UCHAR: struct_utils.UCHAR
}
