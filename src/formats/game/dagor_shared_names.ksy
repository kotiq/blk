meta:
  id: shared_names
  title: DagorEngine shared names
  endian: le


seq:
  - id: hash
    type: u8
  - id: dict_stem
    size: 32
  - id: names_zstd
    size-eos: True
