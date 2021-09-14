meta:
  id: bbf3_zlib_blk
  title: DagorEngine BBF Zlib compressed datablock
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
        contents: "\x00BBz"
      - id: size
        type: u4

  data:
    seq:
      - id: size
        type: u4
      - id: zlib_data_stream
        size: size
