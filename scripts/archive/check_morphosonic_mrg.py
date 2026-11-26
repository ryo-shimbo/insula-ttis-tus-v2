# 段階0の 6(c): MorphoSONIC の髄鞘のある軸索（MRG）に超音波を当てる計算が手元で通るかを確かめる
# 実行: ~/envs/insula-sonic/bin/python scripts/archive/check_morphosonic_mrg.py
import logging
import time

from MorphoSONIC.models import MRGFiber
from MorphoSONIC.sources import GaussianAcousticSource
from PySONIC.core import PulsedProtocol
from PySONIC.utils import logger

logger.setLevel(logging.WARNING)

# コンテストの TUS と同じ軸索: MRG 16 µm・7 節・ソノフォア半径 32 nm・被覆率 1
fiber = MRGFiber(16e-6, nnodes=7, a=32e-9, fs=1.)

# 軸索の真ん中（x = 0）を中心に、幅 1 mm のガウス分布で 250 kHz・500 kPa（表の上限 600 kPa の内側）
# 幅 2 mm だと半値全幅 4.7 mm が軸索の長さ 9 mm に対して広すぎるという警告が出たので 1 mm にした
source = GaussianAcousticSource(0., 1e-3, 250e3, A=500e3)

# 100 ms 当て、その後 50 ms 見る
pp = PulsedProtocol(100e-3, 50e-3)

t0 = time.time()
# simulate は（区画ごとのデータ, 付帯情報）の組を返す
data, meta = fiber.simulate(source, pp)
elapsed = time.time() - t0

# 節ごとの発火の時刻（端の節まで発火が伝わったかを見る）
tspikes = fiber.getSpikesTimings({k: data[k] for k in fiber.nodeIDs})
print(f'fiber: {fiber}')
print(f'source: {source}, protocol: {pp}')
for k in fiber.nodeIDs:
    t = tspikes.get(k)
    n = 0 if t is None else len(t)
    first = '' if n == 0 else f'  first {t[0]*1e3:.2f} ms'
    print(f'{k}: {n} spikes{first}')
print(f'elapsed: {elapsed:.1f} s')
