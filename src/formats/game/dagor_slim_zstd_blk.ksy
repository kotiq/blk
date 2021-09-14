meta:
  id: slim_zstd
  title: DagorEngine Zstd compressed slim datablock
  file-extension: blk
  endian: le


seq:
  - id: type
    contents: [4]
  - id: zstd_data_stream
    size-eos: True
