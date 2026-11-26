# 段階0の 2(c) 後半②: 例の頭 ernie で、左の島皮質向けの電極（Montage I）で TI を計算する
# 電極: 1 組目 T7-P7（0.891 mA）・2 組目 Fp1-Fp2（1.109 mA）。島皮質の群レベルの最適な配置で、コンテスト版と同じ
#   形は公式の例と同じ直径 40 mm の円・厚さ 2 mm
# 標的: MNI (-38, 6, 2) を ernie に写した (-33.53, 31.60, 18.41) mm（BabelBrain の試しと同じ）。半径 5 mm の灰白質で読む
# 実行: cd data/ti_ernie_test && /opt/anaconda3/envs/simnibs_env/bin/python ../../scripts/archive/check_ti_ernie_insula.py
#   出力: data/ti_ernie_test/TI_insula/
from copy import deepcopy
import os
import numpy as np

from simnibs import sim_struct, run_simnibs, mesh_io, ElementTags
from simnibs.utils import TI_utils as TI

TARGET = np.array([-33.53, 31.60, 18.41])
R = 5.0

S = sim_struct.SESSION()
S.subpath = os.path.abspath('../m2m_ernie')
S.pathfem = 'TI_insula'
S.open_in_gmsh = False


def add_pair(c1, c2, current):
    tdcs = S.add_tdcslist()
    tdcs.currents = [current, -current]
    for ch, c in ((1, c1), (2, c2)):
        e = tdcs.add_electrode()
        e.channelnr = ch
        e.centre = c
        e.shape = 'ellipse'
        e.dimensions = [40, 40]
        e.thickness = 2


add_pair('T7', 'P7', 0.891e-3)
add_pair('Fp1', 'Fp2', 1.109e-3)
run_simnibs(S)

m1 = mesh_io.read_msh(os.path.join(S.pathfem, 'ernie_TDCS_1_scalar.msh'))
m2 = mesh_io.read_msh(os.path.join(S.pathfem, 'ernie_TDCS_2_scalar.msh'))
tags_keep = np.hstack((
    np.arange(ElementTags.TH_START, ElementTags.SALINE_START - 1),
    np.arange(ElementTags.TH_SURFACE_START, ElementTags.SALINE_TH_SURFACE_START - 1),
))
m1 = m1.crop_mesh(tags=tags_keep)
m2 = m2.crop_mesh(tags=tags_keep)
TImax = TI.get_maxTI(m1.field['E'].value, m2.field['E'].value)

mout = deepcopy(m1)
mout.elmdata = []
mout.add_element_field(m1.field['E'].norm(), 'magnE - pair 1')
mout.add_element_field(m2.field['E'].norm(), 'magnE - pair 2')
mout.add_element_field(TImax, 'TImax')
mesh_io.write_msh(mout, os.path.join(S.pathfem, 'TI.msh'))

gm = mout.elm.tag1 == ElementTags.GM
centers = mout.elements_baricenters().value
roi = gm & (np.linalg.norm(centers - TARGET, axis=1) <= R)
vol = mout.elements_volumes_and_areas().value
print('elements', mout.elm.nr, 'GM', int(gm.sum()), 'ROI', int(roi.sum()))
print('TImax GM V/m: max %.4f p99 %.4f median %.4f' % (
    TImax[gm].max(), np.percentile(TImax[gm], 99), np.median(TImax[gm])))
roi_mean = np.average(TImax[roi], weights=vol[roi])
gm_mean = np.average(TImax[gm], weights=vol[gm])
print('TImax ROI V/m: mean %.4f max %.4f' % (roi_mean, TImax[roi].max()))
print('ROI mean / GM mean %.3f' % (roi_mean / gm_mean))
print('GM fraction with TImax >= ROI mean %.4f' % (vol[gm & (TImax >= roi_mean)].sum() / vol[gm].sum()))
print('TI insula OK')
