meta:
  id: fat_blk
  title: DagorEngine fat datablock
  file-extension: blk
  endian: le
  bit-endian: le
  imports:
    - /common/vlq_base128_le
    - names


seq:
  - id: type
    contents: [1]
  - id: names
    type: names
  - id: content
    type: content

enums:
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
  cstring:
    seq:
      - id: data
        type: strz
        encoding: UTF-8

  params_data:
    seq:
      - id: size
        type: vlq_base128_le
      - id: params_data_stream
        size: size.value

  tag_offset:
    seq:
      - id: offset
        type: b31
      - id: tag
        type: b1

  offset:
    seq:
      - id: value
        type: u4

  color:
    seq:
      - id: b
        type: u1
      - id: g
        type: u1
      - id: r
        type: u1
      - id: a
        type: u1

  param:
    seq:
      - id: name_id
        type: b24le
      - id: type_id
        type: u1
        enum: value_type
      - id: data
        type:
          switch-on: type_id
          cases:
            value_type::str: tag_offset
            value_type::float12: offset
            value_type::float4: offset
            value_type::float3: offset
            value_type::float2: offset
            value_type::int3: offset
            value_type::int2: offset
            value_type::long: offset
            value_type::color: color
            value_type::int: s4
            value_type::float: f4
            value_type::bool: u4
        size: 4

  name_index:
    seq:
      - id: raw
        type: vlq_base128_le
    instances:
      value:
        value: raw.value - 1


  block:
    seq:
      - id: name_id
        type: name_index
      - id: params_count
        type: vlq_base128_le
      - id: blocks_count
        type: vlq_base128_le
      - id: block_offsett
        type: vlq_base128_le
        if: 'blocks_count.value > 0'

  content:
    seq:
      - id: blocks_count
        type: vlq_base128_le
      - id: params_count
        type: vlq_base128_le
      - id: params_data
        type: params_data
      - id: params
        type: param
        repeat: expr
        repeat-expr: params_count.value
      - id: blocks
        type: block
        repeat: expr
        repeat-expr: blocks_count.value
