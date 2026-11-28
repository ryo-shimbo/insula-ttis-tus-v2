# scripts/ 配置

直下＝本番パイプライン＋解析、`archive/`＝一度きりの調査・使い捨て検証（履歴として保存）。

段階ごとに節を足していく。

## 0 道具の確認

すべて `archive/`。入力と出力は `data/` の下（.gitignore 済み）。実行のしかたは各ファイルの冒頭に書いてある。

| 段階 | スクリプト | 確かめること |
|---|---|---|
| 2(c) | `check_ti_ernie.py` | SimNIBS の公式の TI の例（F5–P5・F6–P6）が ernie で手元で通るか |
| 2(c) | `check_ti_ernie_insula.py` | 左の島皮質向けの電極（Montage I）での TI と選択性 |
| 2(c) | `check_ti_electrode_mesh.py` | 電流の校正の誤差の原因の調べ: 電極ごとのメッシュの形 |
| 2(c) | `check_ti_electrode_flux.py` | 同: 電極ごとの境目と上面の電流 |
| 2(c) | `check_ti_fp1_far.py` | 同: Fp1 の相手を遠い P8 に替える・電極の直径を変える（`TI_DIAM`） |
| 2(c) | `check_ti_electrode_scalp.py` | 同: 電極の下の頭皮の厚さと組織 |
| 2(c) | `check_ti_electrode_rings.py` | 同: 電極の中心からの距離ごとの電流と頭皮の傾き |
| 4(b)(c) | `check_babelbrain_ernie.py` | BabelBrain で ernie の左の島皮質に超音波を当てる計算（`BB_PPW`・`BB_STEPS`） |
| 5(b) | `check_aberra_load.py` | Aberra の錐体細胞を NEURON で読み込めるか |
| 5(c) | `check_aberra_iclamp.py` | Aberra の錐体細胞が電流で発火するか |
| 6(b) | `check_pysonic_point.py` | PySONIC の点神経（RS）に超音波を当てる計算 |
| 6(c) | `check_morphosonic_mrg.py` | MorphoSONIC の MRG 軸索に超音波を当てる計算 |

## 学内の GPGPU サーバー（`gpgpu/`）

学内の演習用計算機システム（GPGPU）2 号機（H100）で BabelBrain を回すためのもの。2 号機の `~/insula/` の下に `repo/`（このリポジトリ）・`data/ernie/`・`runs/`・`logs/` を置く前提。

| 段階 | ファイル | 中身 |
|---|---|---|
| 4(c) | `gpgpu/docker/babelbrain/Dockerfile`・`env_trim.yml` | BabelBrain v0.8.8 を CUDA 13 で動かすイメージ（作者の `environment_linux_cuda_13_driver_580.yml` から、計算に要らない重い部品を外した） |
| 4(c) | `gpgpu/bb_ernie.sbatch` | Slurm のジョブ: コンテナで `check_babelbrain_ernie.py` を回す（使い方は冒頭。イメージの名前は `--container` で渡す） |
| 4(c) | `gpgpu/compare_bb_outputs.py` | 2 つの出力（Mac と 2 号機など）の音場が同じかを比べる（全体と、標的 ±10 mm の焦点） |
