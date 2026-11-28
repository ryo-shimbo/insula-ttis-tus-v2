# 段階0の 4(c): BabelBrain の 2 つの出力（例: 手元の Mac と学内の GPGPU サーバー 2 号機）の音場が同じかを比べる
# 実行: /opt/anaconda3/envs/simnibs_env/bin/python scripts/gpgpu/compare_bb_outputs.py <出力フォルダ A> <出力フォルダ B> [PPW（既定 6）]
#   比べるもの: LInsula_CTX_500_500kHz_<PPW>PPW_FullElasticSolution.nii.gz（圧力の振幅・Pa）
#   1) 全体: 形と位置（shape・affine）・最大の圧力とその場所・最大の差 / A の最大・相対 L2 の差・
#      A の最大の 0.1 % / 1 % を超える差のボクセルの数と、差が一番大きいボクセルの場所
#      （全体の最大は頭皮・頭蓋の近くに出るので、焦点の評価には使わない）
#   2) 標的の周り（標的 ±10 mm の立方体）: 窓の中の最大とその場所・最大の差 / 窓の中の A の最大・
#      焦点の -6 dB の領域（窓の中で、窓の中の最大の半分以上）の体積と、A と B の重なり（Dice）
#   標的は ernie の座標 (-33.53, 31.60, 18.41) mm（MNI (-38, 6, 2) を写したもの。check_babelbrain_ernie.py と同じ）
import sys
import os
import numpy as np
import nibabel as nib

TARGET_MM = np.array([-33.53, 31.60, 18.41])
HALF_MM = 10.0

a_dir, b_dir = sys.argv[1], sys.argv[2]
ppw = int(sys.argv[3]) if len(sys.argv) > 3 else 6
name = f'LInsula_CTX_500_500kHz_{ppw}PPW_FullElasticSolution.nii.gz'
ia, ib = nib.load(os.path.join(a_dir, name)), nib.load(os.path.join(b_dir, name))
print(f'== {name}')
if ia.shape != ib.shape or not np.allclose(ia.affine, ib.affine, atol=1e-4):
    sys.exit(f'shape/affine differ: A {ia.shape} B {ib.shape}\nA affine\n{ia.affine}\nB affine\n{ib.affine}')
a = np.asanyarray(ia.dataobj).astype(np.float64)
b = np.asanyarray(ib.dataobj).astype(np.float64)
aff = ia.affine
vox_vol = float(np.prod(ia.header.get_zooms()[:3]))


def where(d, offset=(0, 0, 0)):
    idx = np.unravel_index(np.argmax(d), d.shape)
    idx = tuple(int(i) + o for i, o in zip(idx, offset))
    mm = nib.affines.apply_affine(aff, idx)
    return idx, f'({mm[0]:.2f}, {mm[1]:.2f}, {mm[2]:.2f}) mm'


# 1) 全体
print('-- whole volume')
for label, d in [('A', a), ('B', b)]:
    print(f'  {label}: max {d.max():.1f} Pa at {where(d)[1]}')
diff = np.abs(a - b)
print(f'  max |A-B| / max A = {diff.max() / a.max():.3e} at {where(diff)[1]}'
      f' (A {a[where(diff)[0]]:.0f} Pa, B {b[where(diff)[0]]:.0f} Pa)')
print(f'  relative L2 |A-B| / |A| = {np.linalg.norm(a - b) / np.linalg.norm(a):.3e}')
for t in [1e-3, 1e-2]:
    print(f'  voxels with |A-B| > {t:g} x max A: {int((diff > t * a.max()).sum())} of {diff.size}')

# 2) 標的の周り
center = np.round(nib.affines.apply_affine(np.linalg.inv(aff), TARGET_MM)).astype(int)
half = np.ceil(HALF_MM / np.array(ia.header.get_zooms()[:3])).astype(int)
lo = np.maximum(center - half, 0)
hi = np.minimum(center + half + 1, a.shape)
win = tuple(slice(l, h) for l, h in zip(lo, hi))
aw, bw = a[win], b[win]
print(f'-- target window: target ({TARGET_MM[0]:.2f}, {TARGET_MM[1]:.2f}, {TARGET_MM[2]:.2f}) mm +-{HALF_MM:g} mm')
for label, d in [('A', aw), ('B', bw)]:
    print(f'  {label}: window max {d.max():.1f} Pa at {where(d, lo)[1]}, at target voxel {d[tuple(center - lo)]:.1f} Pa')
print(f'  max |A-B| / window max A = {np.abs(aw - bw).max() / aw.max():.3e}')
ma, mb = aw >= 0.5 * aw.max(), bw >= 0.5 * bw.max()
dice = 2 * np.logical_and(ma, mb).sum() / (ma.sum() + mb.sum())
print(f'  -6 dB focal region (>= 0.5 x own window max): A {ma.sum() * vox_vol:.1f} mm3, B {mb.sum() * vox_vol:.1f} mm3, Dice {dice:.4f}')
