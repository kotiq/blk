__all__ = [
    'ALG',
    'ANS',
    'DEC',
    'DGEN',
    'DQN',
    'DQS',
    'DefaultDialect',
    'EXP',
    'GEN',
    'HEX',
    'LOG',
    'SW',
    'StrictDialect',
    'VQN',
    'VQS',
    'bool_map',
    'float_map',
    'int_map'
]


EXP = 'exp'
"""Научный формат float, 7 значащих цифр."""

GEN = 'gen'
"""Общий формат float, 7 значащих цифр."""

DGEN = 'dgen'
"""Формат float для strict_blk."""

LOG = 'log'
"""Формат bool false|true."""

ANS = 'ans'
"""Формат bool no|yes."""

SW = 'sw'
"""Формат bool off|on."""

ALG = 'alg'
"""Формат bool 0|1."""

HEX = 'hex'
"""Шестнадцатеричный формат int."""

DEC = 'dec'
"""Десятичный формат int."""

DQS = 'dqs'
"""Формат строк в двойных кавычках."""

VQS = 'vqs'
"""Формат строк в кавычках или без."""

DQN = 'dqn'
"""Формат имен в двойных кавычках."""

VQN = 'vqn'
"""Формат имен в кавычках или без."""


float_map = {
    EXP: '.7e',
    GEN: '.7g',
    DGEN: DGEN,
}

bool_map = {
    LOG: ('false', 'true'),
    ANS: ('no', 'yes'),
    SW: ('off', 'on'),
    ALG: ('0', '1'),
}

int_map = {
    HEX: '#x',
    DEC: 'd',
}


class DefaultDialect:
    scale = 2
    name_format = DQN
    str_format = DQS
    float_format = GEN
    bool_format = LOG
    ubyte_format = HEX
    long_format = HEX
    int_format = DEC
    name_type_sep = ':'
    type_value_sep = ' = '
    name_opener_sep = ' '
    sec_opener = ''
    eof_newline = True


class StrictDialect(DefaultDialect):
    name_format = VQN
    str_format = VQS
    bool_format = ANS
    float_format = DGEN
    ubyte_format = DEC
    long_format = DEC
    type_value_sep = '='
    name_opener_sep = ''
    sec_opener = '\n'
    eof_newline = False
