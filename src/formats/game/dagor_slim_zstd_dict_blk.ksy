meta:
  id: slim_zstd_dict
  title: DagorEngine Zstd compressed with a dict slim datablock
  file-extension: blk
  endian: le


seq:
  - id: type
    contents: [5]
  - id: zstd_with_dict_data_stream
    size-eos: True
