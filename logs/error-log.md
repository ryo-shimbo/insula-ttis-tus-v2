# エラーログ

その日に出たエラーを**下に追記していく**。1件ごとに次の3点を書く。

- **症状**: 出たメッセージ・観測された挙動（そのまま貼る）
- **原因と解決**: 何が起きていたか / どう直したか
- **なぜその方法を選んだか**: 代替案と、それを採らなかった理由（技術選定の根拠）

進捗は `progress-log.md`。

---

## 2026-11-09

### 手元で charm を走らせたら、メモリが足りず Mac が落ちた
- **症状**: 例の頭 ernie で `charm ernie_test org/ernie_T1.nii.gz org/ernie_T2.nii.gz` を手元の Mac（Apple M4・メモリ 16 GB）で走らせたら、画面が落ちて Mac が止まった。charm のログ（`data/m2m_ernie_test/charm_log.html`）は `Starting surface creation` → `Estimating cortical surfaces` で終わっていて、その先が無い。`/usr/bin/time -l` の結果も残っていない。
- **原因と解決**: 皮質の表面を作る段（Topofit）でメモリを使い切った。charm は 8 スレッドで動いていた。SimNIBS の要件は「メモリ 8 GB・16 GB を強く推奨」で、手元はぎりぎり満たしていたが、他のアプリを開いたままでは足りなかった。解決は、charm を手元で回さず、クラウドで回すこと。公開データの ernie は GitHub Actions（ubuntu-latest・16 GB・8 GB のスワップを足す）で回し直している（#1）。
- **なぜその方法を選んだか**: 手元で他のアプリを閉じて回し直す手もあるが、また落ちれば作業中のものを失い、論文版では頭を何体も作るので毎回 Mac を数時間止めることになる。無料で使えるクラウドの中では、v2 が公開リポジトリなので GitHub Actions が無料で無制限、ワークフローとして手順も残る。申請で入手するデータは公開のログに載せられないので、そちらは Kaggle（メモリ約 30 GB）か大学の計算機を候補にした。AWS は無料プランだと起動できるサーバーが 8 GB までで足りず、有料プランに上げるとクレジットの後にカードに請求されるので外した。

## 2026-11-28

### GPGPU 2 号機の BabelBrain が Step 1 で OpenCL のエラーで止まった
- **症状**: `bb_ernie.sbatch`（PPW 6）で、Step 1 の頭皮のメッシュを格子に写す `VoxelizeFilter` の中で止まった。`pyopencl._cl.LogicError: clGetPlatformIDs failed: PLATFORM_NOT_FOUND_KHR`（`GPUFunctions/GPUUtils.py` の `get_default_step`）。
- **原因と解決**: BabelBrain は CUDA で計算するときも、GPU のメモリの量を OpenCL で調べる作りになっている。NVIDIA の OpenCL の本体（`libnvidia-opencl.so.1`）は Slurm がコンテナに渡しているが、登録ファイル `/etc/OpenCL/vendors/nvidia.icd` がコンテナに無いので、OpenCL から GPU が見えなかった。sbatch で一時フォルダに `nvidia.icd`（中身 `libnvidia-opencl.so.1`）を作り、`OCL_ICD_VENDORS` でそこを指すようにして通った。
- **なぜその方法を選んだか**: イメージに `/etc/OpenCL/vendors/nvidia.icd` を入れて作り直す手もあるが、作り直しと Harbor への送り直しが要るので、まずは sbatch の数行で直した（後でイメージにも入れる。ただし conda の ocl-icd は `$CONDA_PREFIX/etc/OpenCL/vendors` を読む作りのことがあり、`/etc/` に置いても効かない可能性があるので、入れるときに確かめる）。BabelBrain の `get_default_step` を CUDA でメモリを調べるように書き換える手もあるが、配られているコードを変えることになり、Mac との比べの前提が崩れるので採らなかった。

### GPGPU 2 号機の BabelBrain が、終わるときに Segmentation fault になる・Slurm の記録が成功のままになる
- **症状**: PPW 6 は「Step 1 OK」「Step 2 OK」「script completed with no error」まで出た後、`Segmentation fault (core dumped)`（`status=139`）で終わった。また、Step 1 で失敗したジョブも含めて、Slurm の記録（`sacct`）は `COMPLETED`・`0:0` になった。
- **原因と解決**: Segmentation fault の原因は未確認（画面なしの Qt か VTK の後片付けの見込み）。出力は全部書き出された後なので、結果には影響しない。Slurm の記録が成功になるのは、コンテナのジョブではスクリプトの終了コードが Slurm に伝わらないためと見ている（未確認）。成否は、ログの「Step 1 OK」「Step 2 OK」の行で判断する。
- **なぜその方法を選んだか**: 終わるときの落ち方を直すには BabelBrain の後片付けを調べる必要があるが、結果に影響しないので、今は判断の仕方を変えるだけにした。本番で人数分を回すときは、ログの Step の行を見るスクリプトで成否を集める。
