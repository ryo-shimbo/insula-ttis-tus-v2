# 段階0の 6(b): PySONIC の点神経（RS）に超音波を当てる計算が手元で通るかを確かめる
# 実行: ~/envs/insula-sonic/bin/python scripts/archive/check_pysonic_point.py
import time

import numpy as np
from PySONIC.core import AcousticDrive, NeuronalBilayerSonophore, PulsedProtocol
from PySONIC.neurons import getPointNeuron
from PySONIC.postpro import detectSpikes

# 皮質の錐体細胞の点神経モデル（regular spiking）と、膜内キャビテーションの半径 32 nm
pneuron = getPointNeuron('RS')
nbls = NeuronalBilayerSonophore(32e-9, pneuron)

# 500 kHz・100 kPa の連続波を 100 ms 当て、その後 50 ms 見る
drive = AcousticDrive(500e3, 100e3)
pp = PulsedProtocol(100e-3, 50e-3)

t0 = time.time()
data, meta = nbls.simulate(drive, pp)
elapsed = time.time() - t0

# 発火の数（電荷密度 Qm のピークで数える）
ispikes, _ = detectSpikes(data)
print(f'neuron: {pneuron.name}, drive: {drive}, protocol: {pp}')
print(f'samples: {len(data)}, Qm range: {data["Qm"].min()*1e5:.1f} .. {data["Qm"].max()*1e5:.1f} nC/cm2')
print(f'spikes: {len(ispikes)}')
if len(ispikes) > 1:
    t = data['t'].values[ispikes]
    print(f'first spike: {t[0]*1e3:.1f} ms, mean rate: {(len(t)-1)/(t[-1]-t[0]):.1f} Hz')
print(f'elapsed: {elapsed:.1f} s')
