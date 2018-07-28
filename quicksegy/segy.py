import array
from pathlib import Path

from .struct_utils import (
    UCHAR,  # CHAR,
    UINT16, INT16,
    UINT32, INT32,
    UINT64,  # INT64,
    DOUBLE,  # FLOAT
    StructPair, MultiStruct
)

from .header_enums import SampleFormat
from .ibmfloat import ibm_to_float


class TextHeader:
    LINE_LENGTH = 80
    LINE_COUNT = 40
    CHARACTERS = LINE_LENGTH * LINE_COUNT

    def __init__(self, data, encoding='EBCDIC-CP-BE'):
        self._raw = data
        self.text = [
            data[i*self.LINE_LENGTH:(i + 1) * self.LINE_LENGTH].decode(encoding)
            for i in range(self.LINE_COUNT)
        ]

    def __str__(self):
        return '\n'.join(self.text)

    def __getitem__(self, key):
        return self.text[key]

    @classmethod
    def from_file(cls, handle, encoding='EBCDIC-CP-BE'):
        data = handle.read(cls.CHARACTERS)
        return cls(data, encoding)


class BinaryHeader:
    """
    SEG-Y Binary Header handler

    Dict-like access to all header keys.
    """
    SIZE = 400
    ENDIAN = '>'
    STRUCT_DICT = {
        'JOB_ID': StructPair(0, INT32),
        'LINE_NO': StructPair(4, UINT32),
        'REEL_NO': StructPair(8, UINT32),
        'DATA_TRACES_PER_ENSEMBLE': StructPair(12, UINT16),
        'AUX_TRACES_PER_ENSEMBLE': StructPair(14, UINT16),
        'SAMPLE_INTERVAL': StructPair(16, UINT16),
        'ORIGINAL_SAMPLE_INTERVAL': StructPair(18, UINT16),
        'SAMPLES_PER_TRACE': StructPair(20, UINT16),
        'ORIGINAL_SAMPLES_PER_TRACE': StructPair(22, UINT16),
        'SAMPLE_FORMAT_CODE': StructPair(24, UINT16),
        'ENSEMBLE_FOLD': StructPair(26, UINT16),
        'TRACE_SORT_CODE': StructPair(28, INT16),
        'VERTICAL_SUM_CODE': StructPair(30, UINT16),
        'SWEEP_FREQ_START': StructPair(32, UINT16),
        'SWEEP_FREQ_END': StructPair(34, UINT16),
        'SWEEP_LENTGH': StructPair(36, UINT16),
        'SWEEP_TYPE': StructPair(38, UINT16),
        'TRACE_NO_SWEEP_CHANNEL': StructPair(40, UINT16),
        'SWEEP_TRACE_TAPER_START': StructPair(42, UINT16),
        'SWEEP_TRACE_TAPER_END': StructPair(44, UINT16),
        'TAPER_TYPE': StructPair(46, UINT16),
        'CORRELATED_DATA_TRACES': StructPair(48, UINT16),
        'BINARY_GAIN_RECOVERED': StructPair(50, UINT16),
        'AMPLITUDE_RECOVERY_METHOD': StructPair(52, UINT16),
        'MEASUREMENT_SYSTEM': StructPair(54, UINT16),
        'IMPULSE_SIGNAL_POLARITY': StructPair(56, UINT16),
        'VIBRATORY_POLARITY_CODE': StructPair(58, UINT16),
        'EXTENDED_DATA_TRACES_PER_ENSEMBLE': StructPair(60, UINT32),
        'EXTENDED_AUX_TRACES_PER_ENSEMBLE': StructPair(64, UINT32),
        'EXTENDED_SAMPLES_PER_TRACE': StructPair(68, UINT32),
        'EXTENDED_SAMPLE_INTERVAL': StructPair(72, DOUBLE),
        'EXTENDED_ORIGINAL_SAMPLE_INTERVAL': StructPair(80, DOUBLE),
        'EXTENDED_ORIGINAL_SAMPLES_PER_TRACE': StructPair(88, UINT32),
        'EXTENDED_ENSEMBLE_FOLD': StructPair(92, UINT32),
        'ENDIAN_CONSTANT': StructPair(96, UINT32),
        'MAJOR_SEGY_REV_NO': StructPair(300, UCHAR),
        'MINOR_SEGY_REV_NO': StructPair(301, UCHAR),
        'FIXED_LENGTH_TRACE_FLAG': StructPair(302, UINT16),
        'EXTENDED_TEXT_HEADER_COUNT': StructPair(304, INT16),
        'MAX_EXTENDED_TRACE_HEADERS': StructPair(306, UINT32),
        'TIME_BASIS_CODE': StructPair(310, UINT16),
        'TRACES_IN_STREAM': StructPair(312, UINT64),
        'FIRST_TRACE_OFFSET': StructPair(320, UINT64),
        'TRAILER_RECORDS': StructPair(328, INT32),
    }
    DEFAULT_STRUCT = MultiStruct(STRUCT_DICT)

    def __init__(self, data, edits=None, overrides=None, endian=ENDIAN):
        """
        Parse the binary header

        :param data: binary header data as a bytestring
        :param edits: edits to the structure of the binary header
        :param overrides: overrides of values in the binary header
        :param endian: Endianness of data '>' big, '<' little
        """
        self.endian = endian

        if edits:
            self.struct_dict = {**self.STRUCT_DICT}
            self.struct_dict.update(edits)
            self.multistruct = MultiStruct(self.struct_dict, self.endian)
        elif self.endian != self.ENDIAN:
            self.multistruct = MultiStruct(self.STRUCT_DICT, self.endian)
        else:
            self.multistruct = self.DEFAULT_STRUCT

        self.data = self.multistruct.unpack(data)

        if overrides:
            self.data.update(overrides)

    def __str__(self):
        return str(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise AttributeError(f'BinaryHeader object has no attribute \'{key}\'')

    @classmethod
    def from_file(cls, handle, edits=None, overrides=None, endian=ENDIAN):
        handle.seek(TextHeader.CHARACTERS)
        data = handle.read(cls.SIZE)
        return cls(data, edits, overrides, endian)


class TraceHeader:
    SIZE = 240
    ENDIAN = '>'
    STRUCT_DICT = {
        'TRACE_NO_LINE': StructPair(0, INT32),
        'TRACE_NO_FILE': StructPair(4, INT32),
        'ORIGINAL_FIELD_RECORD_NO': StructPair(8, INT32),
        'TRACE_NO_FIELD_RECORD': StructPair(12, INT32),
        'SP': StructPair(16, INT32),
        'CDP': StructPair(20, INT32),
        'TRACE_NO_ENSEMBLE': StructPair(24, INT32),
        'TRACE_ID_CODE': StructPair(28, INT16),
        'VERTICALLY_SUMMED_TRACES': StructPair(30, INT16),
        'HORIZONTALLY_STACKED_TRACES': StructPair(32, INT16),
        'DATA_USE': StructPair(34, INT16),
        'DISTANCE_FROM_SOURCE_TO_RECEIVER': StructPair(36, INT32),
        'RECEIVER_ELEVATION': StructPair(40, INT32),
        'SURFACE_ELEVATION_AT_SOURCE': StructPair(44, INT32),
        'SOURCE_DEPTH_BELOW_SURFACE': StructPair(48, INT32),
        'SEISMIC_DATUM_AT_RECEIVER': StructPair(52, INT32),
        'SEISMIC_DATUM_AT_SOURCE': StructPair(56, INT32),
        'WATER_COLUMN_HEIGHT_AT_SOURCE': StructPair(60, INT32),
        'WATER_COLUMN_HEIGHT_AT_RECEIVER': StructPair(64, INT32),
        'ELEVATION_SCALAR': StructPair(68, INT16),
        'COORDINATE_SCALAR': StructPair(70, INT16),
        'SOURCE_X': StructPair(72, INT32),
        'SOURCE_Y': StructPair(76, INT32),
        'GROUP_X': StructPair(80, INT32),
        'GROUP_Y': StructPair(84, INT32),
        'COORDINATE_UNIT': StructPair(88, INT16),
        'WEATHERING_VELOCITY': StructPair(90, INT16),
        'SUBWEATHERING_VELOCITY': StructPair(92, INT16),
        'UPHOLE_TIME_SOURCE': StructPair(94, INT16),
        'UPHOLE_TIME_GROUP': StructPair(96, INT16),
        'SOURCE_STATIC_CORRECTION': StructPair(98, INT16),
        'GROUP_STATIC_CORRECTION': StructPair(100, INT16),
        'TOAL_STATIC_CORRECTION': StructPair(102, INT16),
        'LAG_TIME_A': StructPair(104, INT16),
        'LAG_TIME_B': StructPair(106, INT16),
        'DELAY_RECORDING_TIME': StructPair(108, INT16),
        'MUTE_START': StructPair(110, INT16),
        'MUTE_END': StructPair(112, INT16),
        'SAMPLE_COUNT': StructPair(114, INT16),
        'SAMPLE_INTERVAL': StructPair(116, INT16),
        'GAIN_TYPE': StructPair(118, INT16),
        'INSTRUMENT_GAIN_CONSTANT': StructPair(120, INT16),
        'INSTRUMENT_INITIAL_GAIN': StructPair(122, INT16),
        'CORRELATED': StructPair(124, INT16),
        'SWEEP_FREQUENCY_START': StructPair(126, INT16),
        'SWEEP_FREQUENCY_END': StructPair(128, INT16),
        'SWEEP_LENGTH': StructPair(130, INT16),
        'SWEEP_TYPE': StructPair(132, INT16),
        'SWEEP_TRACE_TAPER_LENGTH_START': StructPair(134, INT32),
        'SWEEP_TRACE_TAPER_LENGTH_END': StructPair(136, INT32),
        'TAPER_TYPE': StructPair(138, INT16),
        'ALIAS_FILTER_FREQ': StructPair(140, INT16),
        'ALIAS_FILTER_SLOPE': StructPair(142, INT16),
        'NOTCH_FILTER_FREQ': StructPair(144, INT16),
        'NOTCH_FILTER_SLOPE': StructPair(146, INT16),
        'LCF_FREQ': StructPair(148, INT16),
        'HCF_FREQ': StructPair(150, INT16),
        'LCF_SLOPE': StructPair(152, INT16),
        'HCF_SLOPE': StructPair(154, INT16),
        'YEAR_RECORDED': StructPair(156, INT16),
        'DAY_RECORDED': StructPair(158, INT16),
        'HOUR_RECORDED': StructPair(160, INT16),
        'MINUTE_RECORDED': StructPair(162, INT16),
        'SECOND_RECORDED': StructPair(164, INT16),
        'TIME_BASIS_CODE': StructPair(166, INT16),
        'TRACE_WEIGHTING_FACTOR': StructPair(168, INT16),
        'GEOPHONE_GROUP_NO_RSP1': StructPair(170, INT16),
        'GEOPHONE_GROUP_NO_FIRST_TRACE': StructPair(172, INT16),
        'GEOPHONE_GROUP_NO_LAST_TRACE': StructPair(174, INT16),
        'GAP_SIZE': StructPair(176, INT16),
        'TAPER_OVER_TRAVEL': StructPair(178, INT16),
        'CDP_X': StructPair(180, INT32),
        'CDP_Y': StructPair(184, INT32),
        'INLINE': StructPair(188, INT32),
        'CROSSLINE': StructPair(192, INT32),
        'SP_NO': StructPair(196, INT32),
        'SP_SCALAR': StructPair(200, INT16),
        'TRACE_VALUE_MEASUREMENT_UNIT': StructPair(202, INT16),
        'TRANSDUCTION_CONSTANT': StructPair(204, INT32),
        'TRANSDUCTION_CONSTANT_EXPONENT': StructPair(208, INT16),
        'TRANSDUCTION_UNITS': StructPair(210, INT16),
        'DEVICE_IDENTIFIER': StructPair(212, INT16),
        'TIME_SCALAR': StructPair(214, INT16),
        'SOURCE_TYPE': StructPair(216, INT16),
        'SOURCE_DIRECTION_VERTICAL': StructPair(218, INT16),
        'SOURCE_DIRECTION_CROSSLINE': StructPair(220, INT16),
        'SOURCE_DIRECTION_INLINE': StructPair(222, INT16),
        'SOURCE_MEASUREMENT': StructPair(224, INT32),
        'SOURCE_MEASUREMENT_EXPONENT': StructPair(228, INT16),
        'SOURCE_MEASUREMENT_UNIT': StructPair(230, INT16),
        'HEADER_NAME': StructPair(233, '8c'),  # 8 chars
    }
    DEFAULT_STRUCT = MultiStruct(STRUCT_DICT, ENDIAN)

    def __init__(self, data, header_edits=None, endian=ENDIAN):
        """
        Parse the binary header

        :param data: binary header data as a bytestring
        :param header_edits:
        """
        self.endian = endian

        if header_edits:
            self.struct_dict = {**self.STRUCT_DICT}
            self.struct_dict.update(header_edits)
            self.multistruct = MultiStruct(self.struct_dict, self.endian)
        elif self.endian != self.ENDIAN:
            self.multistruct = MultiStruct(self.struct_dict, self.endian)
        else:
            self.multistruct = self.DEFAULT_STRUCT

        self.data = self.multistruct.unpack(data)
        self._transform_ibm()

    def _transform_ibm(self):
        for key in self.data.keys():
            if self.struct_dict[key].ibm_float:
                self.data[key] = ibm_to_float(self.data[key])

    @classmethod
    def from_file(cls, handle, header_edits=None, endian=ENDIAN):
        # Assumes seeked to correct location
        data = handle.read(cls.SIZE)
        return cls(data, header_edits, endian)


class ExtendedTraceHeader1:
    # NOT YET DEFINED
    SIZE = 240
    ENDIAN = '>'
    STRUCT_DICT = {}

    def __init__(self, data, header_edits=None, endian=ENDIAN):
        self._data = data


class TraceData:
    def __init__(self, data, format_code=1, endian='>'):
        self._data = None
        self._raw_data = data
        self.format_code = SampleFormat(format_code)
        self.endian = endian

    @property
    def base_format(self):
        # Format for initial array parsing
        # Not necessarily the final data format
        return self.format_code.as_struct

    @property
    def data(self):
        if self._data is None:
            arr = array.array(self.base_format, self._raw_data)
            if self.endian == '>':
                arr.byteswap()
            if self.format_code == SampleFormat.IBM_FLOAT:
                self._data = [ibm_to_float(val) for val in arr]
            else:
                self._data = list(arr)
        return self._data


class TraceHeaderIndexer:
    def __init__(self, path, trace_size, header_edits, endian):
        self.start_offset = TextHeader.CHARACTERS + BinaryHeader.SIZE
        self.path = Path(path)
        self.trace_size = trace_size + TraceHeader.SIZE
        self.header_edits = header_edits
        self.endian = endian

    def read_header(self, handle, idx):
        # not the fastest method but will do for now
        handle.seek(self.start_offset + self.trace_size * idx)
        return TraceHeader.from_file(handle,
                                     header_edits=self.header_edits,
                                     endian=self.endian)

    def __getitem__(self, trace_no):
        with self.path.open('rb') as sgy:
            if isinstance(trace_no, slice):
                start, stop, step = trace_no.start, trace_no.stop, trace_no.step
                data = [self.read_header(sgy, i) for i in range(start, stop, step)]
            else:
                data = self.read_header(sgy, trace_no)

        return data


class SegY:
    ENDIAN = '>'

    def __init__(
            self,
            filepath,
            *,
            text_encoding='ebcdic-cp-be',
            binheader_edits=None,
            trheader_edits=None,
            binheader_overrides=None,
            # trheader_overrides=None,
            endian=ENDIAN
    ):
        self.filepath = Path(filepath)

        self.text_encoding = text_encoding
        self.binheader_edits = binheader_edits if binheader_edits else {}
        self.binheader_overrides = binheader_overrides if binheader_overrides else {}
        self.trheader_edits = trheader_edits if trheader_edits else {}
        # self.trheader_overrides = trheader_overrides if trheader_overrides else {}
        self.endian = endian

        with self.filepath.open('rb') as segy_data:
            self.textheader = TextHeader.from_file(segy_data, self.text_encoding)
            self.binary_header = BinaryHeader.from_file(segy_data,
                                                        self.binheader_edits,
                                                        self.binheader_overrides,
                                                        self.endian)

        self.samples_per_trace = self.binary_header['SAMPLES_PER_TRACE']
        self.sample_format = SampleFormat(self.binary_header['SAMPLE_FORMAT'])
        self.sample_size = self.sample_format.size
        self.trace_size = self.sample_size * self.samples_per_trace

        self._loaded = False
        self.headerindexer = TraceHeaderIndexer(self.filepath,
                                                self.trace_size,
                                                self.trheader_edits,
                                                self.endian)

    @property
    def trace_header(self):
        if self._loaded:
            raise NotImplementedError('Loading headers not yet implemented')
        else:
            return self.headerindexer


class SegY2D(SegY):
    pass


class SegY3D(SegY):
    pass
