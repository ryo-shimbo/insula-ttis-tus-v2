# 段階0の 2(c): 額の電極（Fp1・Fp2）で境目の電流の数えが 2〜3 割少なく出る理由を探る（5 つ目の仮説）
# 仮説: 額は頭皮が薄く、すぐ下に電気を通しにくい骨があるので、電極の下で電場が急に変わり、数える計算が外れる
# 電極ごとに: 境目の三角形の中心から骨の外側の面（緻密骨の面・1007）までの距離（＝頭皮の厚さ）と、
#   境目から深さ 15 mm までにある要素の組織の割合
# 比べる相手（境目の電流 / 上面の電流）: Fp1 0.72・Fp2 0.80・P7 0.92・P8 0.94・T7 1.01
# 実行: /opt/anaconda3/envs/simnibs_env/bin/python scripts/archive/check_ti_electrode_scalp.py
import os
import numpy as np
from scipy.spatial import cKDTree
from simnibs import mesh_io, ElementTags

T = os.path.expanduser('~/Documents/20myknowledge/21-research/insula-ttis-tus-v2/data/ti_ernie_test')
RUNS = [
    (os.path.join(T, 'TI_insula', 'ernie_TDCS_1_scalar.msh'), ('T7', 'P7')),
    (os.path.join(T, 'TI_insula', 'ernie_TDCS_2_scalar.msh'), ('Fp1', 'Fp2')),
    (os.path.join(T, 'Fp1_P8', 'ernie_TDCS_1_scalar.msh'), (None, 'P8')),
]
NAMES = {1: 'WM', 2: 'GM', 3: 'CSF', 5: 'scalp', 6: 'eyes', 7: 'bone_c', 8: 'bone_s', 9: 'blood', 10: 'muscle'}

for path, names in RUNS:
    m = mesh_io.read_msh(path)
    nodes = m.nodes.node_coord
    nl = m.elm.node_number_list
    tri = m.elm.elm_type == 2
    tet = m.elm.elm_type == 4
    bone = nodes[np.unique(nl[tri & (m.elm.tag1 == ElementTags.COMPACT_BONE_TH_SURFACE), :3] - 1)]
    tree = cKDTree(bone)
    scalp_tri = np.where(tri & (m.elm.tag1 == ElementTags.SCALP_TH_SURFACE))[0]
    st = nl[scalp_tri, :3] - 1
    tet_idx = np.where(tet & (m.elm.tag1 < 100))[0]
    tet_c = m.elements_baricenters().value[tet_idx]
    ttree = cKDTree(tet_c)
    for i, name in enumerate(names):
        if name is None:
            continue
        el_tag = ElementTags.SALINE_START + 1 + i
        el_nodes = np.unique(nl[tet & (m.elm.tag1 == el_tag)] - 1)
        inter = scalp_tri[np.all(np.isin(st, el_nodes), axis=1)]
        c = nodes[nl[inter, :3] - 1].mean(axis=1)
        d, _ = tree.query(c)
        # 境目から 15 mm 以内の組織（体積で重み付け）
        near = np.unique(np.concatenate(ttree.query_ball_point(c, 15.0)))
        tags = m.elm.tag1[tet_idx[near]]
        vol = m.elements_volumes_and_areas().value[tet_idx[near]]
        frac = {NAMES.get(int(t), str(t)): vol[tags == t].sum() / vol.sum() for t in np.unique(tags)}
        fs = ' '.join(f'{k} {v:.2f}' for k, v in sorted(frac.items(), key=lambda x: -x[1]))
        print(f'{name}: scalp thickness mm median {np.median(d):.1f} min {d.min():.1f} max {d.max():.1f} | within 15 mm: {fs}')
