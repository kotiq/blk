meta:
  id: bbf_blk
  title: DagorEngine BBF datablock
  file-extension: blk
  endian: le

seq:
  - id: header
    type: header
  - id: data
    type: data

types:
  header:
    seq:
      - id: magic
        contents: "\x00BBF"
      - id: ver_hi
        type: u2
      - id: ver_lo
        type: u2
  data:
    seq:
      - id: data_size
        type: u4
      - id: data_content
        size: data_size
