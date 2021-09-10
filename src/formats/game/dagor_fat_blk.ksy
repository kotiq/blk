meta:
  id: fat_blk
  title: DagorEngine fat datablock
  file-extension: blk
  endian: le
  imports:
    - /common/vlq_base128_le


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

  names_stream:
    seq:
      - id: array
        type: cstring
        repeat: expr
        repeat-expr: _parent.count.value

  names:
    seq:
      - id: count
        type: vlq_base128_le
      - id: size
        type: vlq_base128_le
      - id: names_stream
        type: names_stream
        size: size.value

  params_data:
    seq:
      - id: size
        type: vlq_base128_le
      - id: params_data_stream
        size: size.value

  param:
    seq:
      - id: name_id
        type: b24le
      - id: type_id
        type: u1
        enum: value_type
      - id: data
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
