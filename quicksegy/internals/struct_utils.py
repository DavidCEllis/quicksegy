import struct

from typing import Any, Dict, List, Union


# Unit aliases for format strings
BIG_ENDIAN = '>'
LITTLE_ENDIAN = '<'
CHAR = 'b'
UCHAR = 'B'
INT16 = 'h'
UINT16 = 'H'
INT32 = 'i'
UINT32 = 'I'
INT64 = 'q'
UINT64 = 'Q'
FLOAT = 'f'
DOUBLE = 'd'
VALID_TYPES = ''.join(
    [CHAR, UCHAR, INT16, UINT16, INT32, UINT32, INT64, UINT64, FLOAT, DOUBLE]
)


class StructPair:
    def __init__(self, offset, ctype=UINT32, ibm_float=False):
        # type: (int, str, bool) -> None
        self.offset = offset
        self.ctype = ctype  # UINT32 by default for IBM floats
        self.ibm_float = ibm_float

    def __repr__(self):
        classname = self.__class__.__name__
        r = f'{classname}({self.offset}, ' \
            f'"{self.ctype}", ibm_float={self.ibm_float})'
        return r


class SingleStruct:
    """
    A utility to unpack a struct into a dictionary.

    Provide an initial offset, struct object and a list of names to unpack into.
    Mainly used as part of a multistruct.

    :param struct_: Python Struct
    :param names: List of names to unpack the struct into
    :param offset: offset to start reading from given data
    """
    def __init__(self, struct_, names, offset=0):
        # type: (struct.Struct, List[str], int) -> None
        self.offset = offset
        self.struct_ = struct_
        self.names = names

    def __repr__(self):
        classname = self.__class__.__name__
        return (f'{classname}(struct.Struct(\'{self.struct_.format}\'), '
                f'{self.names}, offset={self.offset})')

    def unpack(self, data):
        # type: (bytes) -> Dict[str, Any]
        result = self.struct_.unpack_from(data, offset=self.offset)
        return dict(zip(self.names, result))


class MultiStruct:
    def __init__(self, struct_dict, endian=BIG_ENDIAN):
        # type: (Dict[str, StructPair], str) -> None
        """
        Create a class that acts like a python struct but allows gaps and overlaps
        and unpacks to a dictionary. Assumes one endianness for the whole set.

        Only for unpacking

        :param struct_dict: Dictionary of key names and structpairs
        :param endian: Endianness of structs
        """
        self.endian = endian
        self.source = struct_dict
        self.structs = self._generate_structs()

    def _generate_structs(self):
        # type: () -> List[SingleStruct]
        """
        Generate the SingleStructs to be used to unpack data

        :return: list of SingleStruct objects
        """
        current_struct = []
        index_val = 0
        names = []

        last_index = index_val

        structs = []  # type: List[SingleStruct]
        for key, value in self.source.items():
            # Check if we are still part of a single struct
            if value.offset == last_index:
                current_struct.append(value.ctype)
                last_index += struct.calcsize(self.endian + value.ctype)
                names.append(key)
            else:
                # Add previous struct
                struct_str = self.endian + ''.join(current_struct)
                last_struct = SingleStruct(struct.Struct(struct_str), names, offset=index_val)
                structs.append(last_struct)

                # Clear and create next struct
                index_val = value.offset
                current_struct = [value.ctype]
                last_index = index_val + struct.calcsize(self.endian + value.ctype)
                names = [key]

        # Finally add the last struct before it cleared
        struct_str = self.endian + ''.join(current_struct)
        last_struct = SingleStruct(struct.Struct(struct_str), names, offset=index_val)
        structs.append(last_struct)
        return structs

    def unpack(self, data):
        # type: (bytes) -> Dict[str, Union[int, float]]
        result = {}
        for section in self.structs:
            result.update(section.unpack(data))
        return result
