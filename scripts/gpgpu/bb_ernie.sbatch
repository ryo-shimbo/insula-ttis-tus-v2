#!/bin/bash
# 段階0の 4(c): 学内の GPGPU サーバー 2 号機（H100）で、BabelBrain の ernie の左の島皮質（check_babelbrain_ernie.py）を回す
# 使い方（2 号機の ~/insula で）:
#   sbatch --container="$(cat bb_image)" --export=ALL,BB_PPW=6 repo/scripts/gpgpu/bb_ernie.sbatch
#   PPW 9 は既定（32 GB・1 時間）では足りないので上書きする:
#   sbatch --container="$(cat bb_image)" --mem=128G --time=04:00:00 --export=ALL,BB_PPW=9 repo/scripts/gpgpu/bb_ernie.sbatch
#   bb_image: Harbor に置いたイメージの名前（<Harbor>/<自分のプロジェクト>/babelbrain:0.8.8-cuda13）を 1 行で書いたファイル。
#   名前に利用者の ID と学内のサーバー名が入るので、リポジトリには入れず 2 号機の ~/insula/ にだけ置く
#   入力: ~/insula/data/ernie/{m2m_ernie, babelbrain_test/LInsula.txt, babelbrain_test/profile.yaml}
#   出力: ~/insula/runs/<日付>_bb_ernie_ppw<N>_<jobid>/output(_ppw<N>)/ と、Slurm のログ ~/insula/logs/bb_ernie_<jobid>.out（logs/ は先に作っておく）
#SBATCH --partition=research
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=logs/bb_ernie_%j.out
umask 077
set -eu   # 準備の段で失敗したら止める（BabelBrain の実行の前で set +e にする）
export PATH=/opt/conda/envs/babelbrain/bin:$PATH
export QT_QPA_PLATFORM=offscreen MYAPP_DISABLE_TELEMETRY=1   # 利用の記録を Google Forms に送る仕組みを止める
export XDG_RUNTIME_DIR=$(mktemp -d)                  # Qt の「runtime directory を作れない」の警告を消す
# BabelBrain は CUDA で計算するときも GPU のメモリの量を OpenCL で調べる。NVIDIA の OpenCL の本体は Slurm が
# コンテナに渡すが、登録ファイル（/etc/OpenCL/vendors/nvidia.icd）が無いので、一時フォルダに作って教える
export OCL_ICD_VENDORS=$(mktemp -d)
echo "libnvidia-opencl.so.1" > "$OCL_ICD_VENDORS/nvidia.icd"
BASE=$PWD                                   # sbatch を打ったフォルダ（~/insula）
PPW=${BB_PPW:-6}
export BB_DATA=$BASE/data/ernie
export BB_OUTROOT=$BASE/runs/$(date +%Y%m%d)_bb_ernie_ppw${PPW}_${SLURM_JOB_ID:-nojob}   # ジョブごとに分けて上書きを防ぐ
mkdir -p "$BB_OUTROOT"
echo "start $(date) host=$(hostname) PPW=$PPW out=$BB_OUTROOT"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /opt/BabelBrain/BabelBrain
set +e   # BabelBrain は終わるときに Segmentation fault になることがある（出力の後）。成否はログの Step の行で見る
time python BabelBrain.py --headless --execute "$BASE/repo/scripts/archive/check_babelbrain_ernie.py"
status=$?
echo "end $(date) status=$status"   # メモリの最大は sacct -j <jobid> -o MaxRSS で見る
exit $status
