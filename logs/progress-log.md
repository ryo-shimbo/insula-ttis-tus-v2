# 進捗ログ

その日の進捗を**下に追記していく**。エラーとその解決は `error-log.md`。
Obsidian 側の詳細な時系列は `myrepository/DailyLogs/`。

## 現在地（2026-11-26）
段階0（道具の確認）の残りは 3・4(c)・7。3 は CERMEP の審査の返事待ち。4(c)（BabelBrain の PPW 9）は手元の Mac（16 GB）ではメモリが足りず、計算機待ち。7 は 3 と 4(c) の後。

段階0の項目: 1 Mac の性能 ✅ → 2 SimNIBS（(a) ✅ (b) ✅ (c) charm と TI ✅）→ 3 CT 付きの公開頭部データ（CERMEP の審査待ち）→ 4 BabelBrain・k-Wave（(a) ✅ (b) ✅ (c) PPW 9 ← 計算機待ち）→ 5 NEURON と Aberra の錐体細胞 ✅ → 6 MorphoSONIC と PySONIC ✅ → 7 使うツールを決める。

計画の案（決定ではない）: 0 道具の確認 → 1 頭部モデルと島皮質のサブ領域 ROI → 2 tTIS の場 → 3 TUS の場 → 4 場のレベルの比較 → 5 神経（錐体細胞の tTIS → 錐体細胞の TUS。MorphoSONIC の軸索はコンテスト版の再現の照合と予備）→ 6 頭の間のばらつきと感度解析 → 7 執筆と投稿。

---

## 2026-11-05
- リポジトリ H4guk/insula-ttis-tus-v2 を作った（private）。README を最初のコミットにした。
- insula-tTIS-TUS に合わせて `.gitignore`・`requirements.txt`・`docs/`・`notebooks/`・`results/`・`scripts/` を置いた。

## 2026-11-09
- 段階0の 1（Mac の性能）: Apple M4・メモリ 16 GB・空き 314 GB。TUS の3次元計算は手元では粗い格子まで。
- 神経の比較は錐体細胞だけにすると決めた。MorphoSONIC の軸索は照合と予備に留める。
- 段階0の 2(a): SimNIBS 4.6.0 は Apple Silicon だけに対応（macOS 14.6・15.3 で試験済み）。メモリは 8 GB 必要・16 GB を強く推奨。Apple Silicon では PARDISO が動かず MUMPS を使う。TI は `TesFlexOptimization`（`max_TI`）で電極の最適化までできる。
- 段階0の 2(b): 公式の conda の手順で、conda 環境 `simnibs_env` に SimNIBS 4.6.0 を入れた（`.pkg` は使っていない）。
- 段階0の 2(c): 例のデータを `data/`（`.gitignore` 済み）に置き、手元で `charm ernie_test` を走らせたが、「Estimating cortical surfaces」の段でメモリが足りず Mac が落ちた。分割の段までは通り、骨を緻密骨（`Bone-Cortical`）と海綿骨（`Bone-Cancellous`）に分けていることを確かめた。
- 段階0の 3（1回目）: 健常者で T1・T2・CT がそろった公開データは見つからなかった。CT 付きの健常者なら CERMEP-IDB-MRXFDG（37 人・T1・FLAIR・CT・申請制）がいちばん近い。頭皮まで写っているか、使ってよい条件は未確認。
- 頭部データは「きちんと比較できること」を優先し、CT 付きを第一候補にする。CT から作った骨の形を tTIS と TUS の両方に使う。tTIS の骨は緻密骨と海綿骨の2層を主にし、CT から場所ごとの導電率を入れる方法は感度解析で試す。
- charm は手元では回さず、無料のクラウドで回す。ernie（公開データ）は GitHub Actions で試している（#1・`chore/1-charm-ernie-ci`）。申請で入手するデータは公開リポジトリのログに載せられないので、Kaggle か大学の計算機を候補にする。AWS は無料プランだと charm に足りるサーバーを使えないので外す。

## 2026-11-09（続き）
- 段階0の 6: PySONIC の点神経（RS）と MorphoSONIC の MRG 軸索に超音波を当てる計算が、環境 `insula-sonic` で通った。RS の表は git-lfs で取った（`check_pysonic_point.py`・`check_morphosonic_mrg.py`）。

## 2026-11-10
- 段階0の 2(c): ernie の charm が GitHub Actions で通った（1 時間 31 分・最大 10.9 GB・#1 → PR #2）。
- 段階0の 5: Aberra の錐体細胞（ModelDB 241165）を NEURON 9.0.2 で読み込み、細胞体への電流で発火した（`check_aberra_load.py`・`check_aberra_iclamp.py`）。モデルはリポジトリに入れない（CC BY-NC-SA 4.0）。

## 2026-11-19
- 段階0の 4(a)(b): BabelBrain v0.8.8 を入れ、ernie の左の島皮質（MNI (-38, 6, 2)）に 500 kHz で当てる Step 1・2 が手元で通った（PPW 6・501 秒・最大 RSS 5.0 GB）。脳の中の最大は標的から 5.4 mm（`check_babelbrain_ernie.py`）。
- 段階0の 3: CERMEP-IDB-MRXFDG の申請フォームを送った。利用の条件により、CERMEP の画像は GitHub Actions（公開リポジトリ）で処理しない。

## 2026-11-20
- 段階0の 4(c): PPW 9 の Step 1 は、見張りがスワップの急増で止めた（Mac は落ちていない）。手元の Mac では回せない。

## 2026-11-24〜26
- 段階0の 2(c): SimNIBS の TI の計算が ernie で手元で通った（1 回 約 5 分・最大 RSS 約 2 GB）。左の島皮質向けの Montage I（T7–P7 0.891 mA・Fp1–Fp2 1.109 mA・直径 40 mm）で、標的（半径 5 mm の灰白質）の TImax は平均 0.0985 V/m、選択性（灰白質全体の平均 / 標的の平均）は 0.395（スクリプトが出す `ROI mean / GM mean` 2.530 の逆数・先行研究の ≈0.40 と同じ）。
- 電流の校正の誤差は Fp1–Fp2 で 7.6 %。Fp1 の相手を遠い P8 に替えると 15.8 % に増え、Fp1–P8 を直径 20 mm にすると 0.5 % に下がった。額の 40 mm の電極の外側（曲がりが強いところ）で電流の数えが外れるため。誤差は場の大きさの倍率にだけ効き、比の指標には効かない。本番では毎回この誤差を記録する。
- tTIS の道具は SimNIBS でよい（最終の決定は段階0の 7）。
