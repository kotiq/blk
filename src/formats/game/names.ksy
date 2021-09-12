meta:
  id: names
  file-extension: names
  endian: le
  imports:
    - /common/vlq_base128_le


seq:
  - id: count
    type: vlq_base128_le
  - id: size
    type: vlq_base128_le
  - id: names_stream
    type: names_stream
    size: size.value

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
