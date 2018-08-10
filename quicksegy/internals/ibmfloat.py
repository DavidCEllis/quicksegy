"""
Handle the IBM Floating point numeric format.

Convert 32 bit IBM floating point numbers to
native python floats.
"""
MAX_SIZE = (1 - 16**-6) * 16**63
MIN_SIZE = 16**-65


def ibm_to_float(ibm):
    """
    Convert IBM float to Python float

    Assumes input is an IBM float represented
    as an unsigned python integer. Does not perform
    bounds checking or type checking.

    :param ibm: IBM floating point value as uint
    :type ibm: int
    :return: Python Float
    :rtype: float
    """
    sign = 1 - 2 * ((ibm >> 31) & 0x01)
    exp = (ibm >> 24) & 0x7f
    fract = (ibm & 0xffffff) / 2**24
    value = sign * 16**(exp-64) * fract

    return value
