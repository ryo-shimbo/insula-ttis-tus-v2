# 段階0の 5(b): Aberra の錐体細胞（ModelDB 241165）を、手元の NEURON 9.0.2 で Python から読み込めるかを確かめる
# 実行: ~/envs/insula-sonic/bin/python scripts/archive/check_aberra_load.py ~/src/AberraEtAl2018 [cell_id]
#   cell_id: 1〜25（6 = L2/3 PC の 1 つ目・既定）。モデルの hoc は相対パスで読むので、モデルのフォルダに移ってから読み込む
#   モデル（CC BY-NC-SA 4.0）はこのリポジトリに入れず、手元の別のフォルダに置く
import os
import sys
import time

model_dir = os.path.expanduser(sys.argv[1])
cell_id = int(sys.argv[2]) if len(sys.argv) > 2 else 6

# 髄鞘のある長い軸索を再帰で作るので、mosinit.command と同じくスタックを大きくする（neuron を import する前に設定する）
os.environ['NEURON_MODULE_OPTIONS'] = '-NSTACK 100000 -NFRAME 20000'
os.chdir(model_dir)

from neuron import h  # noqa: E402  モデルのフォルダの arm64/ にあるコンパイル済みの mod が読み込まれる

# init.hoc から、画面（nrngui.hoc・rig.ses・createPanels）を除いたものを読み込む
h.load_file('stdrun.hoc')
for f in ['interpCoordinates.hoc', 'setPointers.hoc', 'calcVe.hoc', 'stimWaveform.hoc',
          'cellChooser.hoc', 'setParams.hoc', 'editMorphology.hoc']:
    if not h.load_file(f):
        sys.exit(f'failed to load {f}')

# cell_chooser は最後に、init.hoc にある形の描画（color_plotmax）を呼ぶ。画面は使わないので何もしない同名の手続きを置く
h('proc color_plotmax() { }')

h.celsius = 37
h.setParamsAdultHuman()  # 成人のヒトの性質（軸索・樹状突起の太さなど）

t0 = time.time()
h.cell_chooser(cell_id)
elapsed = time.time() - t0

secs = list(h.allsec())
print(f'cell {cell_id}: {h.cell_names.o(cell_id - 1).s}')
print(f'sections: {len(secs)}, segments: {sum(s.nseg for s in secs)}')
# SectionList には count が無いので、中身を並べて数える
print(f'myelinated axon: {int(h.myelinate_ax)}, nodes of Ranvier: {len(list(h.Node_secList))}')
print(f'soma: L = {h.cell.soma[0].L:.1f} um, diam = {h.cell.soma[0].diam:.1f} um')
print(f'elapsed: {elapsed:.1f} s')
