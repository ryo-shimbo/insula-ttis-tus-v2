# 段階0の 5(c): Aberra の錐体細胞の細胞体に電流を入れて、発火するかを確かめる
# 実行: ~/envs/insula-sonic/bin/python scripts/archive/check_aberra_iclamp.py ~/src/AberraEtAl2018 [cell_id] [amps_nA...]
#   cell_id: 1〜25（6 = L2/3 PC・16 = L5 TTPC2・21 = L6 TPC）。電流の既定は 0.5 1 2 nA
#   モデルの読み込みは check_aberra_load.py と同じ（画面の部分を除き、成人のヒトの設定）
import os
import sys
import time

model_dir = os.path.expanduser(sys.argv[1])
cell_id = int(sys.argv[2]) if len(sys.argv) > 2 else 6
amps = [float(a) for a in sys.argv[3:]] or [0.5, 1.0, 2.0]

# 髄鞘のある長い軸索を再帰で作るので、スタックを大きくする（neuron を import する前に設定する）
os.environ['NEURON_MODULE_OPTIONS'] = '-NSTACK 100000 -NFRAME 20000'
os.chdir(model_dir)

from neuron import h  # noqa: E402

h.load_file('stdrun.hoc')
for f in ['interpCoordinates.hoc', 'setPointers.hoc', 'calcVe.hoc', 'stimWaveform.hoc',
          'cellChooser.hoc', 'setParams.hoc', 'editMorphology.hoc']:
    if not h.load_file(f):
        sys.exit(f'failed to load {f}')
# cell_chooser は最後に形の描画（color_plotmax・init.hoc にある）を呼ぶ。画面は使わないので何もしない同名の手続きを置く
h('proc color_plotmax() { }')
h.celsius = 37
h.setParamsAdultHuman()
h.cell_chooser(cell_id)
soma = h.cell.soma[0]

# 細胞体の真ん中に電流を入れる: 50 ms から 200 ms 間、全体で 300 ms 計算する
stim = h.IClamp(soma(0.5))
stim.delay, stim.dur = 50, 200
h.tstop = 300
h.dt = 0.025

# 細胞体の膜電位が 0 mV を上向きに越えた回数を発火として数える
apc = h.APCount(soma(0.5))
apc.thresh = 0
vsoma = h.Vector().record(soma(0.5)._ref_v)

print(f'cell {cell_id}: {h.cell_names.o(cell_id - 1).s}')
for amp in amps:
    stim.amp = amp
    t0 = time.time()
    h.finitialize(-70)  # 初期の膜電位（モデルの静止電位の近くから始める）
    h.continuerun(h.tstop)
    elapsed = time.time() - t0
    rest = vsoma.x[int(40 / h.dt)]  # 電流を入れる前（40 ms）の膜電位
    rate = apc.n / (stim.dur / 1000)
    print(f'  {amp:4.1f} nA: {int(apc.n):3d} spikes ({rate:5.1f} Hz), V before stim = {rest:6.1f} mV, max V = {vsoma.max():5.1f} mV, {elapsed:.1f} s')
