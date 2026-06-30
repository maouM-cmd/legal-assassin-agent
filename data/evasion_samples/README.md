# 改変サンプル（Evasion Samples）

`scripts/generate_evasion_samples.py` が生成する改変動画の出力先です（5 種）。

| ファイル | 改変タイプ |
|---------|-----------|
| `evasion_flipped.mp4` | 水平反転 |
| `evasion_pitch.mp4` | ピッチ変更 |
| `evasion_split_game.mp4` | 2 画面（下半分にゲーム風ノイズ） |
| `evasion_speed.mp4` | 速度変更（`speed_changed`） |
| `evasion_crop.mp4` | クロップ（`cropped`） |

デモ巡回時、これらが「侵害候補」として照合されます。

生成: `python -m scripts.generate_evasion_samples`（`bootstrap.ps1` に含まれる）
