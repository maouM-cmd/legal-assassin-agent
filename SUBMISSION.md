# Legal Assassin Agent — Elastic Hackathon 提出パッケージ

## プロジェクト名

**Legal Assassin Agent** — リーガル・アサシン（著作権保護）エージェント

## エレベーターピッチ（30秒）

VOD 事業者の最大の敵は「ファスト映画」や TikTok への違法切り抜きです。**Legal Assassin** は自社コンテンツのフィンガープリントを Elasticsearch に蓄積し、YouTube・TikTok・X を 24 時間巡回。画面反転・ピッチ変更・速度変更・クロップ・2 画面合成といった巧妙な改変を検出し、DMCA 削除申請を自動生成・送信する著作権保護エージェントです。

## 審査員向け 3 ステップ（必読）

提出 ZIP には動画ファイル（MP4）が含まれません。以下の順でデモを再現してください。

```powershell
cd legal-assassin-agent
.\scripts\bootstrap.ps1          # 必須 — デモクリップ・改変サンプル生成
copy .env.example .env           # 初回のみ
python scripts\verify_setup.py   # セットアップ確認
.\start.bat
```

ブラウザ http://localhost:8001 で:

1. **RUN ALL PATROLS** → TARGET ACQUIRED → TAKEDOWN SENT
2. ヒット行の **COMPARE** → 正解 vs 疑わしい動画のサムネ比較
3. ヘッダーの **EXPORT AUDIT CSV** → コンプライアンスレポート

Elastic 未接続時は [`docs/screenshots/`](docs/screenshots/) の Kibana 参考画像を参照。接続手順: [`docs/elastic_cloud_setup.md`](docs/elastic_cloud_setup.md)

## 技術スタック

| レイヤ | 技術 |
|---|---|
| バックエンド | Python 3.12, FastAPI, APScheduler, WebSocket |
| フロントエンド | HTML / CSS / JavaScript（ダークテーマ ダッシュボード） |
| 検索基盤 | **Elasticsearch**（正解 FP / 侵害ヒット / 撃墜ログ） |
| 映像照合 | pHash（imagehash）+ 反転/分割領域照合 |
| 音声照合 | Chromaprint（fpcalc）+ ffmpeg ピッチ正規化 |
| AI | Google **Gemini** Vision + embedding kNN |
| 巡回 | YouTube Data API / Playwright(TikTok) / X API v2 |
| 撃墜 | Jinja2 DMCA 文面 + Playwright フォーム送信 |

## Elasticsearch 活用ハイライト

| インデックス | 用途 |
|---|---|
| `reference_fingerprints` | 自社 VOD の pHash 列 + 音声 FP + embedding |
| `infringement_hits` | 検出イベント（改変タイプ・スコア・承認状態） |
| `takedown_requests` | DMCA 送信ログ（submitted / pending_manual / failed） |

Kibana ダッシュボード: [`docs/kibana/dashboard.ndjson`](docs/kibana/dashboard.ndjson)  
スクリーンショット: [`docs/screenshots/dashboard-overview.png`](docs/screenshots/dashboard-overview.png)

## デモ手順（5 分）

1. 上記 **審査員向け 3 ステップ**
2. 承認キュー（`DEMO_MODE=false` 時）または自動撃墜（`DEMO_MODE=true`）
3. Kibana ダッシュボードまたはスクリーンショットで ES 可視化を確認

詳細台本: [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md)

## Docker（任意）

ホストで `bootstrap.ps1` 実行後、生成された `data/reference_clips` と `data/evasion_samples` を volume マウントして起動:

```powershell
docker compose up --build
```

## 本番モード

`.env` で `DEMO_MODE=false` にすると:
- `review` ヒットは承認キューへ（自動撃墜しない）
- `confirmed` のみ自動 DMCA 送信

## Phase 10 ハイライト

- ダッシュボード **SETTINGS** — `API_KEY` 環境変数時に `X-API-Key` を UI から設定
- Docker イメージに **fpcalc**（`libchromaprint-tools`）同梱
- `setup_elastic_cloud.ps1` — Elastic Cloud インデックス作成 + 正解ライブラリ投入ワンショット

```powershell
.\scripts\setup_elastic_cloud.ps1
docker compose up --build
```

## Phase 9 ハイライト

- `rehearse_demo.ps1` — デモ動画録画リハーサル（テレプロンプター + サーバー自動起動）
- `update_submission_status.ps1` — 動画 URL / Devpost URL / 提出日を STATUS + DEVPOST_COPY に反映
- `submit_closure_check.ps1` — 提出完走ゲート（全 STATUS done + portal check）
- Devpost 手順書: [`docs/DEVPOST_SUBMIT_WALKTHROUGH.md`](docs/DEVPOST_SUBMIT_WALKTHROUGH.md)

```powershell
.\scripts\submit_portal_check.ps1
.\scripts\rehearse_demo.ps1
# 録画 -> Devpost -> update_submission_status.ps1 -> submit_closure_check.ps1
```

## Phase 8 ハイライト

- `submit_portal_check.ps1` — final_check + ZIP 生成 + Devpost 手順を一括表示
- Devpost 拡張コピペ: [`docs/DEVPOST_EXTENDED.md`](docs/DEVPOST_EXTENDED.md)
- 提出進捗トラッキング: [`docs/SUBMISSION_STATUS.md`](docs/SUBMISSION_STATUS.md)

```powershell
.\scripts\submit_portal_check.ps1
# 動画録画 -> Devpost 貼付 -> SUBMISSION_STATUS.md 更新
```

## Phase 7 ハイライト

- `final_submit_check.ps1` — 提出前の一括自動チェック
- `publish_github.ps1` — public リポジトリ作成・push・CI 確認
- Devpost コピペテンプレ: [`docs/DEVPOST_COPY.md`](docs/DEVPOST_COPY.md)

```powershell
.\scripts\final_submit_check.ps1
.\scripts\publish_github.ps1
```

## Phase 6 ハイライト

- bootstrap/CI で Kibana プレースホルダー PNG 同梱
- `package_submission.ps1` に verify ゲート（未 bootstrap ZIP 防止）
- ポータルチェックリスト + デモ動画台本 + GitHub 公開手順

詳細: [`docs/PORTAL_CHECKLIST.md`](docs/PORTAL_CHECKLIST.md) | [`docs/GITHUB_PUBLISH.md`](docs/GITHUB_PUBLISH.md)

## Phase 5 ハイライト

- 審査員ワンコマンド導線 + `verify_setup.py` 提出ゲート
- ダッシュボード **EXPORT AUDIT CSV** ボタン
- Elastic Cloud セットアップガイド + Kibana スクリーンショット同梱

## Phase 4 ハイライト

- 指数バックオフ付き DMCA リトライ + 失敗撃墜の運用可視化
- Webhook（Slack/Teams）による法務チーム通知
- 監査 CSV エクスポート（コンプライアンス証跡）
- API キーによる破壊的操作の保護（デモ時は未設定でオープン）
- サムネイル比較 UI で審査員向け視覚デモ

## Phase 3 ハイライト

- pHash + 速度/クロップ正規化 + ES kNN + Gemini 二次判定の多層照合
- 承認キュー + DMCA セッション再利用 + 失敗リトライ

## 提出 ZIP 作成

```powershell
.\scripts\bootstrap.ps1
python scripts\verify_setup.py
.\scripts\package_submission.ps1
```

`package_submission.ps1` は verify 未通過時に失敗します。審査員は ZIP 展開後に **bootstrap 必須**（MP4 非同梱）。

ポータル記入: [`docs/PORTAL_CHECKLIST.md`](docs/PORTAL_CHECKLIST.md)  
Devpost 手順: [`docs/DEVPOST_SUBMIT_WALKTHROUGH.md`](docs/DEVPOST_SUBMIT_WALKTHROUGH.md)  
Devpost 基本: [`docs/DEVPOST_COPY.md`](docs/DEVPOST_COPY.md) | 拡張: [`docs/DEVPOST_EXTENDED.md`](docs/DEVPOST_EXTENDED.md)  
提出ステータス: [`docs/SUBMISSION_STATUS.md`](docs/SUBMISSION_STATUS.md)  
動画台本: [`docs/DEMO_VIDEO_SCRIPT.md`](docs/DEMO_VIDEO_SCRIPT.md)

## ライセンス・注意

- デモ動画は `scripts/create_demo_clip.py` で生成される合成クリップ
- 正当な権利者のみ DMCA 送信に使用すること
- プラットフォーム ToS を遵守すること
