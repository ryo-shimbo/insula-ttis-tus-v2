# 段階0の 2(c): Fp1-Fp2 の校正の誤差の原因を探る（2 つ目の仮説）
# SimNIBS は「3 つの頂点がすべて電極に属する頭皮の三角形」を通る電流だけを数える（fem.py の _calc_flux_electrodes）。
# 額の曲がりで、電極と頭皮の境目の一部（ふちの側面など）が数える対象から漏れているかを確かめる。
# 電極ごとに: 数える境目の三角形の面積（平らなら約 1257 mm2）/ 上面（電圧をかける面・2101 番台）から入る電流 /
#   数える境目から出る電流 / 上面に対する境目の割合（1 に近いほど漏れが無い）。電極の伝導率は共通なので E だけで比べる
# 実行: /opt/anaconda3/envs/simnibs_env/bin/python scripts/archive/check_ti_electrode_flux.py
#   引数なし = TI_insula の 2 組（T7-P7・Fp1-Fp2）。引数 fp1p8 = Fp1_P8 の 1 組（4 つ目の確かめ: 誤差は Fp1 か P8 か）
#   引数がフォルダ名（例 Fp1_P8_d20）なら、data/ti_ernie_test/ の下のその 1 組（Fp1・P8）
import os
import sys
import numpy as np
from simnibs import mesh_io, ElementTags

D = os.path.expanduser('~/Documents/20myknowledge/21-research/insula-ttis-tus-v2/data/ti_ernie_test/TI_insula')


def oriented_flux(m, E, tri, face2tet, centers):
    """三角形 tri を通る E の流れ（電極の内から外を正）と面積の合計"""
    nodes = m.nodes.node_coord
    tl = m.elm.node_number_list[tri, :3] - 1
    p = nodes[tl]
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]) / 2  # 面積ベクトル
    area = np.linalg.norm(n, axis=1)
    keys = [tuple(sorted(r)) for r in tl]
    ok = np.array([key in face2tet for key in keys])
    t = np.array([face2tet[key] for key, o in zip(keys, ok) if o], dtype=int)
    p, n, area = p[ok], n[ok], area[ok]
    if (~ok).any():
        print(f'  ({int((~ok).sum())} triangles are not faces of this electrode)')
    out = p.mean(axis=1) - centers[t]
    n *= np.sign(np.sum(n * out, axis=1))[:, None]
    return np.sum(np.sum(E[t] * n, axis=1)), area.sum()


RUNS = [(os.path.join(D, f'ernie_TDCS_{k}_scalar.msh'), f'pair{k}', names)
        for k, names in ((1, ('T7', 'P7')), (2, ('Fp1', 'Fp2')))]
if sys.argv[1:]:
    sub = 'Fp1_P8' if sys.argv[1] == 'fp1p8' else sys.argv[1]
    RUNS = [(os.path.join(os.path.dirname(D), sub, 'ernie_TDCS_1_scalar.msh'), sub, ('Fp1', 'P8'))]

for path, k, names in RUNS:
    m = mesh_io.read_msh(path)
    E = m.field['E'].value
    centers = m.elements_baricenters().value
    nl = m.elm.node_number_list
    tri_all = np.where(m.elm.elm_type == 2)[0]
    for i, name in enumerate(names):
        el_tag = ElementTags.SALINE_START + 1 + i
        tets = np.where((m.elm.elm_type == 4) & (m.elm.tag1 == el_tag))[0]
        face2tet = {}
        for t in tets:
            q = nl[t] - 1
            for f in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)):
                face2tet[tuple(sorted(q[list(f)]))] = t
        el_nodes = set(np.unique(nl[tets] - 1).tolist())
        # SimNIBS と同じ選び方: 頭皮の三角形（1005）で 3 頂点とも電極の節点
        scalp_tri = tri_all[m.elm.tag1[tri_all] == ElementTags.SCALP_TH_SURFACE]
        st = nl[scalp_tri, :3] - 1
        inter = scalp_tri[np.all(np.isin(st, list(el_nodes)), axis=1)]
        # 上面（2101 番台）
        top = tri_all[m.elm.tag1[tri_all] == 2101 + i]
        f_top, a_top = oriented_flux(m, E, top, face2tet, centers)
        f_int, a_int = oriented_flux(m, E, inter, face2tet, centers)
        print(f'{k} {name}: interface tris {len(inter)} area {a_int:.0f} mm2 | top tris {len(top)} area {a_top:.0f} mm2 | '
              f'flux top {f_top:+.2f} interface {f_int:+.2f} | interface/top {abs(f_int)/abs(f_top):.3f}')
