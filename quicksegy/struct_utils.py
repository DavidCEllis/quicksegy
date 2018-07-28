import struct

from typing import Dict, List, Union


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


class StructPair:
    def __init__(self, offset, ctype=UINT32, ibm_float=False):
        # type: (int, str, bool) -> None
        self.offset = offset
        self.ctype = ctype  # UINT32 by default for IBM floats
        self.ibm_float = ibm_float

    def __repr__(self):
        classname = self.__class__.__name__
        r = f'{classname}({self.offset}, ' \
            f'{self.ctype}, ibm_float={self.ibm_float})'
        return r


class SingleStruct:
    def __init__(self, offset, struct_, names):
        # type: (int, struct.Struct, List[str]) -> None
        self.offset = offset
        self.struct_ = struct_
        self.names = names

    def __repr__(self):
        classname = self.__class__.__name__
        return f'{classname}({self.offset}, {self.struct_}, {self.names})'

    def unpack(self, data):
        result = self.struct_.unpack_from(data, offset=self.offset)
        return dict(zip(self.names, result))


class MultiStruct:
    def __init__(self, struct_dict, endian=BIG_ENDIAN):
        # type: (Dict[str, StructPair], str) -> None
        """
        Create a class that acts like a python struct but allows gaps and overlaps
        and unpacks to a dictionary. Assumes one endianness for the whole set.

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
            if value.offset == last_index:
                current_struct.append(value.ctype)
                last_index += struct.calcsize(value.ctype)
                names.append(key)
            else:
                # Add previous struct
                struct_str = self.endian + ''.join(current_struct)
                last_struct = SingleStruct(index_val, struct.Struct(struct_str), names)
                structs.append(last_struct)

                # Clear and create next struct
                index_val = value.offset
                current_struct = [value.ctype]
                last_index = index_val + struct.calcsize(value.ctype)
                names = [key]

        # Finally add the last struct before it cleared
        struct_str = self.endian + ''.join(current_struct)
        last_struct = SingleStruct(index_val, struct.Struct(struct_str), names)
        structs.append(last_struct)
        return structs

    def unpack(self, data):
        # type: (bytes) -> Dict[str, Union[int, float]]
        result = {}
        for section in self.structs:
            result.update(section.unpack(data))
        return result
