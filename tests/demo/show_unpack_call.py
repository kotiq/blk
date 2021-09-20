"""Скрипт для запуска тестов продолжительности распаковки и построения гистограммы по результатам.
Используют numpy и matplotlib.
Предполагается, что версии интерпретаторов установлены в виртуальные окружения
cpython_venv и pypy_venv с общим корнем venv_home
"""

import os
from pathlib import Path
from functools import reduce
import itertools as itt
import subprocess
import shlex
import shutil
import json
import numpy as np
import matplotlib.pyplot as plt

project = reduce(lambda acc, _: acc.parent, '...', Path(__file__))
build = project / 'build'
tests = project / 'tests'
out = build / 'tests' / 'test_blk' / 'test_compare' / 'help_time'

log = out / 'time.log'
test = tests / 'test_blk' / 'test_compare' / 'help_time.py'


with open(log, 'w'):
    pass

venv_home = Path('~/.virtualenvs').expanduser()
cpython_venv = 'blk'
pypy_venv = 'blk_pypy3'
lang = 'en_US.UTF-8'

for venv in (cpython_venv, pypy_venv):
    path = venv_home / venv / 'bin'
    args = shlex.split(f'python -m pytest {test} --durations=0 -vs')
    subprocess.run(args, env={'PATH': str(path), 'LANG': lang})

with open(log) as istream:
    rs = [json.loads(line) for line in istream]

rs_new = tuple(r for r in rs if r['path'].endswith('.bin_u'))
rs_old = tuple(r for r in rs if r['path'].endswith('.bin_u_old'))

fig = plt.figure()
ax = fig.add_subplot(111)
n = 4
ind = np.arange(n)
width = 0.35

calls_new = tuple(r['call'] for r in rs_new)
calls_old = tuple(r['call'] for r in rs_old)
max_call = max(itt.chain(calls_new, calls_old))

rects1 = ax.bar(ind, calls_new, width, color='dimgray')
rects2 = ax.bar(ind+width, calls_old, width, color='lightgray')

ystep = 5
ax.set_xlim(-width, len(ind)+width)
ax.set_ylim(0, max_call+4*ystep)
ax.set_ylabel('Время, с')
ax.set_title('Время распаковки aces по форматам, интерпретаторам и распаковщикам', loc='center', wrap=True)

cpu_count = os.cpu_count()
marks = []
for r in rs_new:
    impl = r['impl']
    unpacker = r['unpacker']
    if unpacker == 'blk_unpack_demo.py':
        ps = '1 process'
    elif unpacker == 'blk_unpack_demo_mp.py':
        ps = f'{cpu_count} processes'
    marks.append('\n'.join([impl, ps]))

ax.set_xticks(ind+width/2)
names = ax.set_xticklabels(marks)
rects = ax.patches
labels = (format(t, '.1f') for t in itt.chain(calls_new, calls_old))

for rect, label in zip(rects, labels):
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width() / 2, height + ystep, label, ha="center", va="bottom")

ax.legend((rects1[0], rects2[0]), ('Новый формат', 'Старый формат'))
svg = out / 'time.svg'
plt.savefig(svg)
shutil.copy2(svg, tests / 'demo')
