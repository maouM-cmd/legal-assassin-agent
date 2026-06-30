# Legal Assassin Agent — 著作権保護エージェント

![CI](https://github.com/maouM-cmd/legal-assassin-agent/actions/workflows/ci.yml/badge.svg)

VOD 事業者の自社コンテンツを正解データとして学習し、YouTube / TikTok / X を 24 時間巡回。反転・ピッチ変更・2 画面合成などの巧妙な違法アップロードを検出し、DMCA 削除申請を自動生成・送信するエージェント。

## 提出前（Phase 8）

```powershell
.\scripts\submit_portal_check.ps1
```

Devpost 記入: [`docs/DEVPOST_COPY.md`](docs/DEVPOST_COPY.md) + [`docs/DEVPOST_EXTENDED.md`](docs/DEVPOST_EXTENDED.md)  
提出進捗: [`docs/SUBMISSION_STATUS.md`](docs/SUBMISSION_STATUS.md)

## Phase 8: Devpost 提出完走

- **ワンストップゲート**: [`scripts/submit_portal_check.ps1`](scripts/submit_portal_check.ps1) — final_check + ZIP + 手順表示
- **Devpost 拡張フィールド**: [`docs/DEVPOST_EXTENDED.md`](docs/DEVPOST_EXTENDED.md) — Inspiration / Challenges / Accomplishments 等
- **提出ステータス**: [`docs/SUBMISSION_STATUS.md`](docs/SUBMISSION_STATUS.md) — 動画 URL / Devpost URL / 提出日

## Phase 7: GitHub 公開 + 提出完走

- **最終ゲート**: [`scripts/final_submit_check.ps1`](scripts/final_submit_check.ps1) — verify + pytest + screenshots
- **GitHub 公開**: [`scripts/publish_github.ps1`](scripts/publish_github.ps1) — `gh` で public push + CI 確認
- **Devpost コピペ**: [`docs/DEVPOST_COPY.md`](docs/DEVPOST_COPY.md)
- **CI バッジ**: push 後に README の `YOUR_USER` を置換

## Phase 6: 提出ポータル完走

- **Kibana スクリーンショット同梱**: bootstrap/CI で `docs/screenshots/*.png` 自動生成
- **パッケージゲート**: `package_submission.ps1` が `verify_setup` 通過後のみ ZIP 作成
- **ポータル資料**: [`docs/PORTAL_CHECKLIST.md`](docs/PORTAL_CHECKLIST.md)、[`docs/DEMO_VIDEO_SCRIPT.md`](docs/DEMO_VIDEO_SCRIPT.md)
- **Git 公開手順**: [`docs/GITHUB_PUBLISH.md`](docs/GITHUB_PUBLISH.md)

提出前: `bootstrap.ps1` → `verify_setup.py` → `package_submission.ps1` → GitHub push → 動画アップロード

## Phase 5: 提出仕上げ

- **審査員導線**: `bootstrap.ps1` → `start.bat` → Patrol → COMPARE → **EXPORT AUDIT CSV**
- **verify_setup.py**: デモデータ必須チェック（reference >= 1, evasion >= 5）— 提出前ゲート
- **Elastic Cloud ガイド**: [`docs/elastic_cloud_setup.md`](docs/elastic_cloud_setup.md)
- **Kibana スクリーンショット**: [`docs/screenshots/`](docs/screenshots/)（Elastic 未接続時のフォールバック）
- **CI**: bootstrap → verify_setup → smoke test 直列化

提出 ZIP 作成前に `python scripts/verify_setup.py` が pass することを推奨。

## Phase 4: 運用基盤・デモ仕上げ

- **リトライ指数バックオフ**: `last_retry_at` + 60/120/240 秒待機、`list_failed_takedowns_ready()`
- **Webhook 通知**: `WEBHOOK_URL` + `WEBHOOK_ENABLED` — Slack/Teams 互換 JSON
- **監査 CSV**: `GET /api/audit/export?from=...&to=...` — hits + takedowns 結合レポート
- **API キー認証**: `API_KEY` 設定時、patrol / approve / retry に `X-API-Key` 必須
- **サムネ比較 UI**: `GET /api/hits/{id}/thumbnails` + ダッシュボード **COMPARE** モーダル
- **Kibana 完全版**: 4 レンズ + ダッシュボード saved object（Elastic 8.8+）
- **CI**: GitHub Actions (`pytest` + smoke test)

## Phase 3: 照合強化・撃墜本番化

- **改変検出 v2**: 速度変更（`speed_changed`）・クロップ（`cropped`）を追加
- **ES kNN 照合**: `HYBRID_MATCH=true` で embedding 候補絞り込み → フル fingerprint 照合
- **Gemini 二次判定**: スコア 0.70〜閾値帯を `secondary_review()` で補強
- **DMCA 本番化**: Playwright `storageState` + フォーム自動入力（[`scripts/save_platform_session.py`](scripts/save_platform_session.py)）
- **リトライ**: 失敗撃墜を 30 分間隔で自動再送、`POST /api/takedowns/retry`
- **Kibana**: [`docs/kibana/dashboard.ndjson`](docs/kibana/dashboard.ndjson) インポート

## Phase 2: ハッカソン提出・本番ゲート

- **承認キュー**: `DEMO_MODE=false` 時、`review` ヒットは法務承認待ち → ダッシュボードで Approve/Reject
- **DMCA プレビュー**: 送信前に通知文面を確認
- **URL 重複排除**: 既処理 URL はスキップ
- **提出 ZIP**: `.\scripts\package_submission.ps1`
- **Docker**: `docker compose up --build`

詳細: [SUBMISSION.md](SUBMISSION.md)

## クイックスタート

```powershell
cd C:\Users\admin\Projects\legal-assassin-agent
.\scripts\bootstrap.ps1
copy .env.example .env
python scripts\verify_setup.py
.\start.bat
```

ブラウザ: [http://localhost:8001](http://localhost:8001)

> **提出 ZIP 利用時**: MP4 は ZIP に含まれません。展開後に必ず `.\scripts\bootstrap.ps1` を実行してください。

## デモ手順

1. `bootstrap.ps1` でデモクリップ・正解インデックス・改変サンプル（5 種）を生成
2. ダッシュボードで **RUN ALL PATROLS** → 検出 → DMCA 撃墜
3. **COMPARE** でサムネ比較、**EXPORT AUDIT CSV** で監査レポート取得

詳細: [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | リハーサル: [scripts/rehearsal_checklist.md](scripts/rehearsal_checklist.md)

## アーキテクチャ

```
scan → download → fingerprint → match → evasion_check → dmca_generate → submit → log
```

| コンポーネント | 技術 |
|---|---|
| 映像照合 | pHash（imagehash） |
| 音声照合 | Chromaprint（fpcalc） |
| 改変検出 | 反転/ピッチ正規化 + Gemini Vision |
| 巡回 | YouTube Data API / Playwright(TikTok) / X API v2 |
| 撃墜 | Jinja2 DMCA 文面 + Playwright フォーム送信 |
| ログ | Elasticsearch（未設定時インメモリ） |

## API

| Method | Path | 説明 |
|--------|------|------|
| GET | `/api/health` | ヘルスチェック（demo_mode, hybrid_match, webhook, api_key） |
| GET | `/api/stats` | 検出・撃墜統計 + 巡回状態 |
| GET | `/api/references` | 正解ライブラリ一覧 |
| GET | `/api/hits` | 侵害ヒット一覧 |
| GET | `/api/review-queue` | 承認待ちキュー |
| GET | `/api/pending-manual` | CAPTCHA 待ち撃墜 |
| GET | `/api/hits/{id}` | ヒット詳細 |
| GET | `/api/hits/{id}/dmca-preview` | DMCA 文面プレビュー |
| GET | `/api/hits/{id}/thumbnails` | サムネ比較用 base64 JPEG |
| GET | `/api/audit/export` | 監査 CSV（`?from=` / `?to=` または `from_date` / `to_date`） |
| GET | `/api/takedowns` | 撃墜ログ（`?status=failed` 等） |
| POST | `/api/hits/{id}/approve` | 承認して撃墜（`X-API-Key` 任意） |
| POST | `/api/hits/{id}/reject` | 却下（`X-API-Key` 任意） |
| POST | `/api/takedowns/retry` | 失敗撃墜リトライ（`X-API-Key` 任意） |
| POST | `/api/patrol` | 全プラットフォーム巡回（`X-API-Key` 任意） |
| POST | `/api/patrol/{platform}` | 単一プラットフォーム巡回 |
| POST | `/api/analyze` | ローカル動画照合 |
| POST | `/api/process-candidate` | 候補 URL を手動処理 |
| WS | `/ws/events` | リアルタイムイベント |

## 環境変数

`.env.example` を参照。Elastic / Gemini / YouTube / X 未設定でも `DEMO_MODE=true` でデモ可能。

## 注意事項

- 本ツールは正当な権利者による DMCA 通知の自動化を目的とします
- プラットフォーム ToS・各国法規を遵守してください
- 誤検知時の法的責任に注意し、閾値・二段階照合を適切に設定してください
- TikTok 本番運用は公式パートナー API の利用を推奨

## システム依存（任意）

- `ffmpeg` — 改変サンプル生成・ピッチ正規化
- `fpcalc` — Chromaprint 音声フィンガープリント
