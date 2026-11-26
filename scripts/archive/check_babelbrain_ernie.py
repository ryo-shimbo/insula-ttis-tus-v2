# 段階0の 4(b-2): BabelBrain で、例の頭 ernie の左の島皮質に超音波を当てる計算（Step 1 と 2）が手元で通るかを確かめる
# BabelBrain の中で動くスクリプト（launch・wait_until などは BabelBrain が用意する。import は要らない）
# 実行: ~/Applications/BabelBrain.app/Contents/MacOS/BabelBrain --headless --execute scripts/archive/check_babelbrain_ernie.py
#   入力は data/babelbrain_test/（.gitignore 済み）:
#   - LInsula.txt: Brainsight 形式の軌道。標的は MNI (-38, 6, 2) を ernie に写した (-33.53, 31.60, 18.41) mm、
#     3 列目（m2n*）= (-1, 0, 0) が標的からトランスデューサへの向き（左の横から当てる）
#   - profile.yaml: 熱の計算の条件（Step 3 は今回は回さない）
#   4(c): 環境変数 BB_PPW（1 波長あたりの点の数・既定 6）と BB_STEPS（'1' なら Step 1 だけ・既定 '12'）で変える。
#   出力は PPW 6 なら output/、それ以外は output_ppw<N>/
import os

DATA = os.path.expanduser('~/Documents/20myknowledge/21-research/insula-ttis-tus-v2/data')
WORK = os.path.join(DATA, 'babelbrain_test')
PPW = int(os.environ.get('BB_PPW', '6'))
STEPS = os.environ.get('BB_STEPS', '12')
OUT = 'output' if PPW == 6 else f'output_ppw{PPW}'
print(f'PPW={PPW} STEPS={STEPS} OUT={OUT}')

bb = launch(
    t1w=os.path.join(DATA, 'm2m_ernie', 'T1.nii.gz'),
    simbnibs=os.path.join(DATA, 'm2m_ernie') + '/',
    simbnibs_type='charm',
    trajectory=os.path.join(WORK, 'LInsula.txt'),
    trajectory_type='brainsight',
    thermal_profile=os.path.join(WORK, 'profile.yaml'),
    transducer='CTX_500',   # 500 kHz のリング型（文書の例と同じ）
    ct_type='NONE',         # CT なし（骨は charm の分け方から）
    frequency_khz=500,
    ppw=PPW,                # 6 = 早い見積もり（メモリを抑える）・9 = 他のツールと合わせる細かさ
    output_path=os.path.join(WORK, OUT) + '/',
)
auto_answer_dialogs(question=QMessageBox.Yes)  # 前の結果があっても計算し直す

# Step 1: 計算の領域を作る（頭皮・骨・脳の分け方を格子に写す）
bb.testing_error = False
bb.Widget.CalculatePlanningMask.click()
wait_until(bb.Widget.tabWidget.isEnabled, timeout_ms=900_000)
check_no_error(bb)
print('Step 1 OK')

# Step 2: 音響の場を計算する（焦点はそのまま・ステアリングなし）。BB_STEPS='1' なら回さない
if STEPS != '1':
    bb.Widget.tabWidget.setCurrentIndex(1)
    for i in range(bb.AcSim._txTabs.count()):
        bb.AcSim._txTabs.setCurrentIndex(i)
        if hasattr(bb.AcSim.Widget, 'ZSteeringSpinBox'):
            bb.AcSim.Widget.ZSteeringSpinBox.setValue(0.0)
        bb.AcSim.Widget.CalculateAcField.click()
        wait_until(bb.Widget.tabWidget.isEnabled, timeout_ms=3_600_000)
        check_no_error(bb)
    print('Step 2 OK')
