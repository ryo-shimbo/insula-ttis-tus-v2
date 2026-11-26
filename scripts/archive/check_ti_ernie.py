# 段階0の 2(c) 後半: SimNIBS の公式の TI の例（examples/simulations/TI.py）を、例の頭 ernie で手元で回す
# 目的: 手元の Mac で TI の計算が最後まで通るか、時間とメモリを測る（電極は例のまま F5-P5 と F6-P6・1 mA）
# 実行: cd data/ti_ernie_test && /opt/anaconda3/envs/simnibs_env/bin/python ../../scripts/archive/check_ti_ernie.py
#   入力: data/m2m_ernie（.gitignore 済み）・出力: data/ti_ernie_test/TI/
from copy import deepcopy
import os
import numpy as np

from simnibs import sim_struct, run_simnibs, mesh_io, ElementTags
from simnibs.utils import TI_utils as TI

S = sim_struct.SESSION()
S.subpath = os.path.abspath('../m2m_ernie')
S.pathfem = 'TI'
S.open_in_gmsh = False

tdcs = S.add_tdcslist()
tdcs.currents = [0.001, -0.001]
electrode = tdcs.add_electrode()
electrode.channelnr = 1
electrode.centre = 'F5'
electrode.shape = 'ellipse'
electrode.dimensions = [40, 40]
electrode.thickness = 2
electrode = tdcs.add_electrode()
electrode.channelnr = 2
electrode.centre = 'P5'
electrode.shape = 'ellipse'
electrode.dimensions = [40, 40]
electrode.thickness = 2

tdcs = S.add_tdcslist(deepcopy(tdcs))
tdcs.electrode[0].centre = 'F6'
tdcs.electrode[1].centre = 'P6'

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

# 灰白質（GM）での TImax の分布（V/m）
gm = mout.elm.tag1 == ElementTags.GM
print('elements', mout.elm.nr, 'GM', int(gm.sum()))
print('TImax GM V/m: max %.4f p99 %.4f median %.4f' % (
    TImax[gm].max(), np.percentile(TImax[gm], 99), np.median(TImax[gm])))
print('TI OK')
