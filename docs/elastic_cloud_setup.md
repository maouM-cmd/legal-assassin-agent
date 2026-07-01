# Elastic Cloud セットアップ（審査員向け）

Legal Assassin Agent を Elasticsearch / Kibana と接続する手順です。未設定でも `DEMO_MODE=true` でインメモリ動作しますが、ハッカソン審査では ES 連携のデモを推奨します。

## ワンショット（推奨）

`.env` に Elastic 認証情報を設定後:

```powershell
.\scripts\bootstrap.ps1
.\scripts\setup_elastic_cloud.ps1
.\start.bat
```

上記でインデックス作成 + 正解ライブラリ投入まで一括実行します。接続確認のみなら `.\scripts\verify_elastic_cloud.ps1`。

## 1. Elastic Cloud トライアル

1. [Elastic Cloud](https://cloud.elastic.co/) でアカウント作成
2. **Create deployment** → Elasticsearch 8.8 以降を選択
3. Deployment 作成後、**Manage** から以下を控える:
   - **Cloud ID** (`ELASTIC_CLOUD_ID`)
   - **API Key**（`manage_security` 権限付き）

## 2. `.env` 設定

```env
ELASTIC_CLOUD_ID=your-deployment:base64...
ELASTIC_API_KEY=your-api-key
ELASTIC_INDEX_REFERENCE=reference_fingerprints
ELASTIC_INDEX_HITS=infringement_hits
ELASTIC_INDEX_TAKEDOWNS=takedown_requests
```

ローカル Elasticsearch を使う場合:

```env
ELASTIC_URL=http://localhost:9200
ELASTIC_API_KEY=your-api-key
```

## 3. インデックス作成

```powershell
cd C:\Users\admin\Projects\legal-assassin-agent
.\.venv\Scripts\python.exe -m scripts.index_elasticsearch
```

正解ライブラリの投入（bootstrap 済みの場合）:

```powershell
.\.venv\Scripts\python.exe -m scripts.index_reference
```

## 4. Kibana ダッシュボードインポート

1. Kibana → **Stack Management** → **Saved Objects** → **Import**
2. [`docs/kibana/dashboard.ndjson`](kibana/dashboard.ndjson) を選択
3. **Analytics** → **Dashboard** → **Legal Assassin — Infringement Ops** を開く

詳細: [kibana_infringement.md](kibana_infringement.md)

Elastic 未接続の審査員向けに、リポジトリ内のスクリーンショットも参照できます: [screenshots/](screenshots/)

## 5. デモデータ投入

```powershell
.\scripts\bootstrap.ps1
.\start.bat
```

ブラウザで **RUN ALL PATROLS** を実行後、Kibana ダッシュボードに以下が表示されます:

- プラットフォーム別検出数
- 改変タイプ内訳（`speed_changed`, `cropped` 含む）
- 撃墜成功時系列
- 平均照合スコア

## 6. トラブルシューティング

| 症状 | 対処 |
|------|------|
| `Elasticsearch: demo mode` | `.env` の Cloud ID / API Key を確認 |
| Kibana インポート失敗 | Elastic 8.8+ を使用。手動作成は [kibana_infringement.md](kibana_infringement.md) 参照 |
| ダッシュボードが空 | patrol 実行後にデータが `infringement_hits` に蓄積されるか `/api/hits` で確認 |
