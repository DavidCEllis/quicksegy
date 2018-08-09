import math
import struct

from hypothesis import given
from hypothesis.strategies import booleans, data, floats, integers, lists, sampled_from

from quicksegy.struct_utils import StructPair, SingleStruct, MultiStruct


hypothesis_types = {
    'b': integers(min_value=-2**7, max_value=2**7-1),
    'B': integers(min_value=0, max_value=2**8-1),
    'h': integers(min_value=-2**15, max_value=2**15-1),
    'H': integers(min_value=0, max_value=2**16-1),
    'l': integers(min_value=-2**31, max_value=2**31-1),
    'L': integers(min_value=0, max_value=2**32-1),
    'q': integers(min_value=-2**63, max_value=2**63-1),
    'Q': integers(min_value=0, max_value=2**64-1),
    'f': floats(min_value=-10**38, max_value=10**38,
                allow_infinity=False, allow_nan=False),
    'd': floats(min_value=-10**300, max_value=10**300,
                allow_infinity=False, allow_nan=False),
}


@given(integers(min_value=0), sampled_from('bBhHlLqQfd'), booleans())
def test_structpair(offset, ctype, ibm_float):
    sp = StructPair(offset, ctype, ibm_float)
    assert sp.offset == offset
    assert sp.ctype == ctype
    assert sp.ibm_float == ibm_float

    rsp = eval(repr(sp))

    assert isinstance(rsp, StructPair)
    assert sp.offset == rsp.offset
    assert sp.ctype == rsp.ctype
    assert sp.ibm_float == rsp.ibm_float


@given(data())
def test_singlestruct(data):
    # Generate a random fmt string
    structfmtlist = data.draw(lists(sampled_from('bBhHlLqQfd'), min_size=1, max_size=40))
    endian = '>' if data.draw(booleans()) else '<'
    structfmt = endian + ''.join(structfmtlist)

    keys = [str(i) for i, _ in enumerate(structfmtlist)]
    values = [data.draw(hypothesis_types[key]) for key in structfmtlist]

    expected = {key: value for key, value in zip(keys, values)}

    teststruct = struct.Struct(structfmt)
    testpacked = teststruct.pack(*values)

    unpacker = SingleStruct(teststruct, keys, offset=0)

    actual = unpacker.unpack(testpacked)

    for key in actual.keys():
        if isinstance(actual[key], float):
            assert math.isclose(expected[key], actual[key], rel_tol=0.001)
        else:
            assert expected[key] == actual[key]


@given(data())
def test_singlestruct_repr(data):
    structfmtlist = data.draw(lists(sampled_from('bBhHlLqQfd'), min_size=1, max_size=40))
    endian = '>' if data.draw(booleans()) else '<'
    structfmt = endian + ''.join(structfmtlist)
    teststruct = struct.Struct(structfmt)
    keys = [str(i) for i, _ in enumerate(structfmtlist)]
    offset = data.draw(integers(min_value=0, max_value=1000))

    expected = SingleStruct(teststruct, keys, offset=offset)

    result = eval(repr(expected))

    assert expected.struct_.format == result.struct_.format
    assert expected.names == result.names
    assert expected.offset == result.offset
