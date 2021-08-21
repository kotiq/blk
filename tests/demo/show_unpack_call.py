import os
from functools import reduce
import itertools as itt
import subprocess
import shlex
import json
import numpy as np
import matplotlib.pyplot as plt

project = reduce(lambda acc, _: os.path.dirname(acc), '...', __file__)
build = os.path.join(project, 'build')
tests = os.path.join(project, 'tests')
out = os.path.join(build, 'tests', 'test_blk', 'test_compare', 'test_time')

log = os.path.join(out, 'time.log')
test = os.path.join(tests, 'test_blk', 'test_compare', 'test_time.py')


with open(log, 'w'):
    pass

venv_home = os.path.expanduser('~/.virtualenvs')
venvs = (
    'blk',
    'blk_pypy3',
)
lang = 'en_US.UTF-8'

for venv in venvs:
    path = os.path.join(venv_home, venv, 'bin')
    args = shlex.split(f'python -m pytest {test} --durations=0 -vs')
    subprocess.run(args, env=dict(PATH=path, LANG=lang))

with open(log) as istream:
    rs = [json.loads(line) for line in istream]

rs_new = [r for r in rs if r['path'].endswith('.bin_u')]
rs_old = [r for r in rs if r['path'].endswith('.bin_u_old')]

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

marks = []
for r in rs_new:
    impl = r['impl']
    unpacker = r['unpacker']
    if unpacker == 'blk_unpack_demo.py':
        ps = '1 процесс'
    elif unpacker == 'blk_unpack_demo_mp.py':
        ps = '4 процесса'
    marks.append('\n'.join([impl, ps]))

ax.set_xticks(ind+width/2)
names = ax.set_xticklabels(marks)
rects = ax.patches
labels = (format(t, '.1f') for t in itt.chain(calls_new, calls_old))

for rect, label in zip(rects, labels):
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width() / 2, height + ystep, label, ha="center", va="bottom")

ax.legend((rects1[0], rects2[0]), ('Новый формат', 'Старый формат'))
plt.savefig(os.path.join(out, 'time.svg'))
