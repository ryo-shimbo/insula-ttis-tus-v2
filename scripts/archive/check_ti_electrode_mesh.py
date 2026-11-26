# 段階0の 2(c): Fp1-Fp2 の電流の校正の誤差（7.6 %）の原因を探る。電極ごとのメッシュの形を比べる
# 校正の誤差 = 片方の電極から出た電流と、もう片方に入った電流の食い違い（simnibs/simulation/fem.py）
# 電極は直径 40 mm・厚さ 2 mm の円なので、崩れていなければ体積は約 2513 mm3
# 実行: /opt/anaconda3/envs/simnibs_env/bin/python scripts/archive/check_ti_electrode_mesh.py
import os
import numpy as np
from simnibs import mesh_io, ElementTags

D = os.path.expanduser('~/Documents/20myknowledge/21-research/insula-ttis-tus-v2/data/ti_ernie_test/TI_insula')
for k, names in ((1, ('T7', 'P7')), (2, ('Fp1', 'Fp2'))):
    m = mesh_io.read_msh(os.path.join(D, f'ernie_TDCS_{k}_scalar.msh'))
    tet = m.elm.elm_type == 4
    vol = m.elements_volumes_and_areas().value
    # 要素の形の悪さ: 体積 / (最長の辺^3)。正四面体で 0.118、0 に近いほど潰れている
    nodes = m.nodes.node_coord
    el = m.elm.node_number_list - 1
    skin_tet_nodes = set(np.unique(el[tet & (m.elm.tag1 == ElementTags.SCALP)]).tolist())
    for i, name in enumerate(names):
        tag = ElementTags.SALINE_START + 1 + i  # 厚さ 1 層の電極はゲルの札（501・502）で入る
        sel = tet & (m.elm.tag1 == tag)
        e = el[sel]
        p = nodes[e]
        edges = [np.linalg.norm(p[:, a] - p[:, b], axis=1) for a, b in ((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))]
        lmax = np.max(edges, axis=0)
        q = vol[sel] / lmax**3
        # 肌に触れている節点の数（電極と頭皮の両方に属する節点）
        enodes = set(np.unique(e).tolist())
        shared = len(enodes & skin_tet_nodes)
        print(f'pair{k} {name}: tag {tag} tets {int(sel.sum())} volume {vol[sel].sum():.0f} mm3 '
              f'quality min {q.min():.4f} p1 {np.percentile(q,1):.4f} median {np.median(q):.4f} '
              f'nodes touching scalp {shared}')
