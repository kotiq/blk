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
    9: true
    10: color
    11: float12
    12: long
    0x89: false

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
        encoding: UTF-8
        size: size.value

  pad4:
    seq:
      - id: padding
        size: (4 - _io.pos) % 4

  names_data:
    seq:
      - id: count
        type:
          switch-on: _parent.tag_module.tag
          cases:
            count_type::single_byte: u1
            count_type::two_bytes: u2
            count_type::four_bytes: u4
      - id: array
        type: pascal_string
        repeat: expr
        repeat-expr: count

  names:
    seq:
      - id: tag_module
        type: tag_module
      - id: names_data
        type: names_data
        if: tag_module.tag != count_type::zero
      - id: padding
        type: pad4

  strings_stream:
    seq:
      - id: array
        type: pascal_string
        repeat: expr
        repeat-expr: _parent.count

  strings_data:
    seq:
      - id: count
        type:
          switch-on: _parent.tag_size.tag
          cases:
            count_type::single_byte: u1
            count_type::two_bytes: u2
            count_type::four_bytes: u4
      - id: strings_stream
        type: strings_stream
        size: _parent.tag_size.size

  strings:
    seq:
      - id: tag_size
        type: tag_size
      - id: strings_data
        type: strings_data
        if: tag_size.tag != count_type::zero
      - id: padding
        type: pad4

  value_info:
    seq:
      - id: name_id
        type: b24le
      - id: type_id
        type: u1
        enum: value_type

  dummy: {}

  floats:
    params:
      - id: len
        type: u1
    seq:
      - id: array
        type: f4
        repeat: expr
        repeat-expr: len

  ints:
    params:
      - id: len
        type: u1
    seq:
      - id: array
        type: s4
        repeat: expr
        repeat-expr: len

  color:
    seq:
      - id: array
        type: u1
        repeat: expr
        repeat-expr: 4

  true:
    instances:
      value:
        value: True

  false:
    instances:
      value:
        value: False

  param_value:
    params:
      - id: i
        type: u2
    seq:
      - id: value
        type:
          switch-on: _parent.values_info[i].type_id
          cases:
            value_type::str: u4
            value_type::int: s4
            value_type::float: f4
            value_type::float2: floats(2)
            value_type::float3: floats(3)
            value_type::float4: floats(4)
            value_type::int2: ints(2)
            value_type::int3: ints(3)
            value_type::true: true
            value_type::false: false
            value_type::color: color
            value_type::float12: floats(12)
            value_type::long: s8


  block_value:
    seq:
      - id: value_info
        type: value_info
      - id: value
        type: block  # @r

  block:
    seq:
      - id: params_count
        type: u2
      - id: blocks_count
        type: u2
      - id: values_info
        type: value_info
        repeat: expr
        repeat-expr: params_count
      - id: params_values
        type: param_value(_index)
        repeat: expr
        repeat-expr: params_count
      - id: blocks_values
        type: block_value
        repeat: expr
        repeat-expr: blocks_count

  data_stream:
    seq:
      - id: names
        type: names
      - id: strings
        type: strings
      - id: root
        type: block

  data:
    seq:
      - id: size
        type: u4
      - id: data_stream
        type: data_stream
        size: size
