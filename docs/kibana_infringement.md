# Kibana — 侵害検出・撃墜ダッシュボード

## インデックス

| インデックス | 内容 |
|---|---|
| `reference_fingerprints` | 正解コンテンツのフィンガープリント |
| `infringement_hits` | 検出された侵害候補 |
| `takedown_requests` | DMCA 送信ログ |

## ダッシュボード作成手順

1. Kibana → **Analytics** → **Dashboard** → **Create dashboard**
2. **Create visualization** を追加

### 推奨ビジュアライゼーション

**1. プラットフォーム別検出数（棒グラフ）**
- データビュー: `infringement_hits`
- 集計: Count
- バケット: Terms on `platform.keyword`

**2. 改変タイプ別内訳（円グラフ）**
- データビュー: `infringement_hits`
- 集計: Count
- バケット: Terms on `evasion_types.keyword`

**3. 撃墜成功率（時系列）**
- データビュー: `takedown_requests`
- 集計: Count
- バケット: Date Histogram on `timestamp`
- フィルター: `status: submitted`

**4. 平均照合スコア（メトリック）**
- データビュー: `infringement_hits`
- 集計: Average on `final_score`

## データビュー一括インポート（Phase 4 完全版）

1. Kibana → **Stack Management** → **Saved Objects** → **Import**
2. [`docs/kibana/dashboard.ndjson`](kibana/dashboard.ndjson) を選択
3. インポートされるオブジェクト:
   - データビュー: `infringement_hits`, `takedown_requests`
   - レンズ 4 件: プラットフォーム別検出 / 改変タイプ / 撃墜成功時系列 / 平均スコア
   - ダッシュボード: **Legal Assassin — Infringement Ops**
4. **Analytics** → **Dashboard** → `Legal Assassin — Infringement Ops` を開く

> **注意**: Elastic 8.8 以降を想定。バージョン差異でインポートエラーが出る場合は、下記「推奨ビジュアライゼーション」で手動作成してください。

### スクリーンショット（審査員向け）

Elastic Cloud 未接続時はリポジトリ内の参考画像を使用:

- [`docs/screenshots/dashboard-overview.png`](screenshots/dashboard-overview.png)
- [`docs/screenshots/platform-detections.png`](screenshots/platform-detections.png)

実環境でキャプチャする場合:
1. [`elastic_cloud_setup.md`](elastic_cloud_setup.md) で ES 接続
2. patrol 実行後にダッシュボードを開く
3. 上記 2 枚をキャプチャ（必要なら `python scripts/generate_screenshot_placeholders.py` でプレースホルダー再生成）

## データビューのみインポート（Phase 3 互換）

旧版 NDJSON はデータビュー 2 件のみ。Phase 4 以降は上記完全版を使用。

## データビュー手動作成

1. **Stack Management** → **Data Views** → **Create data view**
2. Name: `infringement_hits`
3. Index pattern: `infringement_hits`
4. Timestamp field: `timestamp`

同様に `takedown_requests` を作成。

## デモモード

Elasticsearch 未設定時はインメモリに蓄積。`/api/hits` と `/api/takedowns` で API 経由確認可能。

Elastic Cloud 接続手順: [elastic_cloud_setup.md](elastic_cloud_setup.md)
