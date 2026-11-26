# 段階0の 2(c): 額の 40 mm の電極で境目の電流の数えが外れる場所を探る（7 つ目の仮説）
# 仮説: 外れは 40 mm の電極の外側の部分（額の曲がりが強いところ・眉や目に近いところ）から来る（20 mm では外れない）
# 40 mm の Fp1-P8 の結果で、電極を中心からの距離の輪（0-10・10-15・15 mm 超）に分け、輪ごとに
#   境目の電流 / 上面の電流 と、頭皮の面の傾き（電極全体の向きからのずれの角度）を出す
#   Fp1 だけ外側の輪で比が大きく下がり、そこで傾きも大きければ仮説に合う。どの輪でも同じように下がれば外れ
# 実行: /opt/anaconda3/envs/simnibs_env/bin/python scripts/archive/check_ti_electrode_rings.py
import os
import numpy as np
from simnibs import mesh_io, ElementTags

PATH = os.path.expanduser('~/Documents/20myknowledge/21-research/insula-ttis-tus-v2/data/ti_ernie_test/Fp1_P8/ernie_TDCS_1_scalar.msh')
RINGS = [(0, 10), (10, 15), (15, 99)]

m = mesh_io.read_msh(PATH)
E = m.field['E'].value
nodes = m.nodes.node_coord
nl = m.elm.node_number_list
centers = m.elements_baricenters().value
tri_all = np.where(m.elm.elm_type == 2)[0]
scalp_tri = tri_all[m.elm.tag1[tri_all] == ElementTags.SCALP_TH_SURFACE]


def per_tri(tri, face2tet):
    """三角形ごとの E の流れ（電極の内から外を正）・中心・単位法線・面積。電極の面でない三角形は落とす"""
    tl = nl[tri, :3] - 1
    keys = [tuple(sorted(r)) for r in tl]
    ok = np.array([k in face2tet for k in keys])
    tl = tl[ok]
    t = np.array([face2tet[k] for k, o in zip(keys, ok) if o], dtype=int)
    p = nodes[tl]
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]) / 2
    c = p.mean(axis=1)
    n *= np.sign(np.sum(n * (c - centers[t]), axis=1))[:, None]
    area = np.linalg.norm(n, axis=1)
    return np.sum(E[t] * n, axis=1), c, n / area[:, None], area


for i, name in enumerate(('Fp1', 'P8')):
    tets = np.where((m.elm.elm_type == 4) & (m.elm.tag1 == ElementTags.SALINE_START + 1 + i))[0]
    face2tet = {}
    for t in tets:
        q = nl[t] - 1
        for f in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)):
            face2tet[tuple(sorted(q[list(f)]))] = t
    el_nodes = np.unique(nl[tets] - 1)
    st = nl[scalp_tri, :3] - 1
    inter = scalp_tri[np.all(np.isin(st, el_nodes), axis=1)]
    top = tri_all[m.elm.tag1[tri_all] == 2101 + i]
    fi, ci, ni, ai = per_tri(inter, face2tet)
    ft, ct, nt, at = per_tri(top, face2tet)
    # 電極の中心と向き: 境目の三角形の面積で重み付けした中心と、外向き法線の平均（頭皮の内向きなので反転）
    c0 = np.average(ci, axis=0, weights=ai)
    n0 = -np.average(ni, axis=0, weights=ai)
    n0 /= np.linalg.norm(n0)

    def radius(c):
        v = c - c0
        return np.linalg.norm(v - np.outer(v @ n0, n0), axis=1)

    ri, rt = radius(ci), radius(ct)
    tilt = np.degrees(np.arccos(np.clip(-ni @ n0, -1, 1)))
    print(f'{name}: total interface/top {abs(fi.sum())/abs(ft.sum()):.3f}')
    for lo, hi in RINGS:
        si, sti = (ri >= lo) & (ri < hi), (rt >= lo) & (rt < hi)
        print(f'  r {lo:>2}-{hi:<2} mm: area int {ai[si].sum():6.0f} top {at[sti].sum():6.0f} | '
              f'flux int {abs(fi[si].sum()):7.1f} top {abs(ft[sti].sum()):7.1f} ratio {abs(fi[si].sum())/abs(ft[sti].sum()):.3f} | '
              f'tilt deg median {np.median(tilt[si]):5.1f} max {tilt[si].max():5.1f}')
