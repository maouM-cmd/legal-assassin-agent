# 提出ポータルチェックリスト

Devpost / Elastic Hackathon 等への記入用。コピペ元は [SUBMISSION.md](../SUBMISSION.md)。

**そのまま貼れる文面:** [DEVPOST_COPY.md](DEVPOST_COPY.md) + [DEVPOST_EXTENDED.md](DEVPOST_EXTENDED.md)  
**提出進捗:** [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md)

## 基本情報

| 欄 | 記入内容 |
|----|----------|
| **プロジェクト名** | Legal Assassin Agent |
| **短い説明** | VOD 向け 24/7 著作権パトロール — pHash + 音声 + Gemini + Elasticsearch + DMCA 自動化 |
| **長い説明** | SUBMISSION.md の「エレベーターピッチ」+ Phase 3/4/5 ハイライトを結合 |

## リンク

| 欄 | 記入内容 |
|----|----------|
| **リポジトリ URL** | GitHub public URL（[GITHUB_PUBLISH.md](GITHUB_PUBLISH.md) 参照） |
| **デモ動画 URL** | [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md) で録画後にアップロード |
| **ライブデモ** | http://localhost:8001（審査員は bootstrap 必須） |

## Elastic 活用（審査向け）

| 項目 | 説明 |
|------|------|
| `reference_fingerprints` | 正解 pHash / 音声 FP / embedding |
| `infringement_hits` | 検出イベント（改変タイプ・スコア） |
| `takedown_requests` | DMCA 送信ログ |
| Kibana | `docs/kibana/dashboard.ndjson` インポート |
| スクリーンショット | `docs/screenshots/dashboard-overview.png` |

## 審査員向けセットアップ（README にも記載）

```powershell
.\scripts\bootstrap.ps1
copy .env.example .env
python scripts\verify_setup.py
.\start.bat
```

ZIP 利用時: MP4 は含まれないため **bootstrap 必須**。

## Phase 8: Devpost 提出完走

```powershell
.\scripts\submit_portal_check.ps1
```

上記で final_check + ZIP 生成 + 次の手順を一括表示。

| 順序 | 作業 |
|------|------|
| 1 | `submit_portal_check.ps1` — 自動チェック + ZIP |
| 2 | [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md) で録画・アップロード |
| 3 | Devpost に [DEVPOST_COPY.md](DEVPOST_COPY.md) + [DEVPOST_EXTENDED.md](DEVPOST_EXTENDED.md) を貼付 |
| 4 | [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md) を更新（動画 URL / Devpost URL / 提出日） |

## 提出前セルフチェック

- [ ] `.\scripts\submit_portal_check.ps1` が pass（verify + pytest + ZIP）
- [ ] `docs/screenshots/*.png` がリポジトリに存在
- [ ] GitHub Actions CI が green
- [ ] デモ動画をアップロードし URL を [DEVPOST_COPY.md](DEVPOST_COPY.md) + [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md) に記入
- [ ] リハーサル: [scripts/rehearsal_checklist.md](../scripts/rehearsal_checklist.md)

## 提出 ZIP

```powershell
.\scripts\bootstrap.ps1
python scripts\verify_setup.py
.\scripts\package_submission.ps1
```

出力: `legal-assassin-agent-submission.zip`（ルート直下）
