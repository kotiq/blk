meta:
  id: names
  endian: le
  imports:
    - /common/vlq_base128_le

seq:
  - id: count
    type: vlq_base128_le
  - id: names_data
    type: names_data
    if: count.value != 0

types:
  cstring:
    seq:
      - id: data
        type: strz
        encoding: UTF-8

  names_data:
    seq:
      - id: size
        type: vlq_base128_le
      - id: names_stream
        type: names_stream
        size: size.value

  names_stream:
    seq:
      - id: array
        type: cstring
        repeat: expr
        repeat-expr: _root.count.value
