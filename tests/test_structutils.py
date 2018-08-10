import struct

import pytest

from quicksegy.internals.struct_utils import StructPair, MultiStruct


@pytest.fixture
def demo_data():
    testvalsp1 = [2, -4, 0.5, 2**40]
    testvalsp2 = [-2**20, 16, 10.25]

    test_struct = struct.pack('>BhfQ', *testvalsp1)
    test_struct += struct.pack('>bbbb', 0, 0, 0, 0)
    test_struct += struct.pack('>lHd', *testvalsp2)

    return test_struct


@pytest.fixture
def demo_multi():
    struct_dict = {
        'v1': StructPair(0, 'B'),
        'v2': StructPair(1, 'h'),
        'v3': StructPair(3, 'f'),
        'v4': StructPair(7, 'Q'),
        'v5': StructPair(19, 'l'),
        'v6': StructPair(23, 'H'),
        'v7': StructPair(25, 'd'),
    }

    ms = MultiStruct(struct_dict)
    return ms


def test_multistruct_build(demo_multi):

    ms = demo_multi

    assert len(ms.structs) == 2
    assert ms.structs[0].offset == 0
    assert ms.structs[1].offset == 19
    assert ms.structs[0].struct_.format == '>BhfQ'
    assert ms.structs[1].struct_.format == '>lHd'
    assert ms.structs[0].names == ['v1', 'v2', 'v3', 'v4']
    assert ms.structs[1].names == ['v5', 'v6', 'v7']


def test_multistruct_unpack(demo_multi, demo_data):
    expected = {
        'v1': 2,
        'v2': -4,
        'v3': 0.5,
        'v4': 2**40,
        'v5': -2**20,
        'v6': 16,
        'v7': 10.25,
    }

    assert demo_multi.unpack(demo_data) == expected
