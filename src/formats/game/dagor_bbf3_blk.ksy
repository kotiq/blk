meta:
  id: bbf_blk
  title: DagorEngine BBF datablock
  file-extension: blk
  endian: le
  bit-endian: le

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

  vql:
    seq:
      - id: head
        type: u1
      - id: tail
        type: u1
        repeat: expr
        repeat-expr: len - 1
    instances:
      len:
        value: >
          (head & 0x80) == 0 ? 1 :
          (head & 0xC0) == 0x80 ? 2 :
          3
      value:
        value: >
          len == 1 ? head :
          len == 2 ? (head & 0x3f | tail[0]) :
          ((head & 0x3f) << 16) | (tail[0] << 8) | tail[1]

  pascal_string:
    seq:
      - id: size
        type: vql
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
