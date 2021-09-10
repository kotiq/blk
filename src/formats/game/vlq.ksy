meta:
  id: vlq
  title: Variable Length Quantity, unsigned integer, big-endian

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
