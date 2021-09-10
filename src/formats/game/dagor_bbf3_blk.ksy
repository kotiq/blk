meta:
  id: bbf_blk
  title: DagorEngine BBF datablock
  file-extension: blk
  endian: le
  bit-endian: le
  imports:
    - vlq

seq:
  - id: header
    type: header
  - id: data
    type: data

enums:
  count_type:
    0: zero
    1: single_byte
    2: two_bytes
    3: four_bytes

  value_type:
    0: section
    1: str
    2: int
    3: float
    4: float2
    5: float3
    6: float4
    7: int2
    8: int3
    9: bool
    10: color
    11: float12
    12: long

types:
  version:
    seq:
      - id: hi
        type: u2
      - id: lo
        type: u2

  header:
    seq:
      - id: magic
        contents: "\x00BBF"
      - id: version
        type: version

  tag_module:
    seq:
      - id: module
        type: b14
      - id: tag
        type: b2
        enum: count_type

  tag_size:
    seq:
      - id: size
        type: b30
      - id: tag
        type: b2
        enum: count_type

  pascal_string:
    seq:
      - id: size
        type: vlq
      - id: data
        type: str
        # todo: вариации кодирования: utf8, cp1251
        encoding: UTF-8
        size: size.value

  pad4:
    seq:
      - id: padding
        size: (4 - _io.pos) % 4

  names_content:
    seq:
      - id: count
        type:
          switch-on: _parent.tag_module.tag
          cases:
            count_type::single_byte: u1
            count_type::two_bytes: u2
            count_type::three_bytes: u4
      - id: data
        type: pascal_string
        repeat: expr
        repeat-expr: count

  names:
    seq:
      - id: tag_module
        type: tag_module
      - id: content
        type: names_content
        if: tag_module.tag != count_type::zero
      - id: padding
        type: pad4

  strings_content:
    seq:
      - id: count
        type:
          switch-on: _parent.tag_size.tag
          cases:
            count_type::single_byte: u1
            count_type::two_bytes: u2
            count_type::three_bytes: u4
      - id: data
        type: pascal_string
        repeat: expr
        repeat-expr: count

  strings:
    seq:
      - id: tag_size
        type: tag_size
      - id: content
        type: strings_content
        if: tag_size.tag != count_type::zero
      - id: padding
        type: pad4

  block:
    seq:
      - id: data
        size-eos: true

  data_content:
    seq:
      - id: names
        type: names
      - id: strings
        type: strings
      - id: block
        type: block

  data:
    seq:
      - id: size
        type: u4
      - id: content
        type: data_content
