# 段階0の 2(c): Fp1-Fp2 の校正の誤差（7.6 %）の原因を探る（3 つ目の仮説）
# 仮説: Fp1 と Fp2 が近い（ふちの間 約 19 mm）ので、向かい合うふちに電流が集まり、境目で電流を数える計算が外れる
# 確かめ方: Fp1 の電極（直径 40 mm・厚さ 2 mm）はそのまま、相手だけを遠い P8 に替えて 1 組（1 mA）回す
#   誤差が 1 % 前後に下がれば近さが原因・7 % 前後のままなら Fp1 の場所（額）が原因
# 実行: cd data/ti_ernie_test && /opt/anaconda3/envs/simnibs_env/bin/python ../../scripts/archive/check_ti_fp1_far.py
#   誤差は SimNIBS のログ（標準エラー）の "Estimated current calibration error" の行に出る。出力: data/ti_ernie_test/Fp1_P8/
#   6 つ目の確かめ: 環境変数 TI_DIAM（電極の直径 mm・既定 40）で電極を小さくする。40 以外は出力を Fp1_P8_d<直径>/ に分ける
import os
from simnibs import sim_struct, run_simnibs

DIAM = int(os.environ.get('TI_DIAM', '40'))

S = sim_struct.SESSION()
S.subpath = os.path.abspath('../m2m_ernie')
S.pathfem = 'Fp1_P8' if DIAM == 40 else f'Fp1_P8_d{DIAM}'
S.open_in_gmsh = False
S.fields = 'eE'  # E（向き付き）も残す。電極ごとの電流を check_ti_electrode_flux.py で数えるため

tdcs = S.add_tdcslist()
tdcs.currents = [0.001, -0.001]
for ch, c in ((1, 'Fp1'), (2, 'P8')):
    e = tdcs.add_electrode()
    e.channelnr = ch
    e.centre = c
    e.shape = 'ellipse'
    e.dimensions = [DIAM, DIAM]
    e.thickness = 2

run_simnibs(S)
print(f'Fp1-P8 d={DIAM} OK')
