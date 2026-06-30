# Kibana ダッシュボード — スクリーンショット

Elastic Cloud 未接続の審査員向けに、Kibana ダッシュボードの参考画像を同梱しています。

| ファイル | 内容 |
|---------|------|
| [dashboard-overview.png](dashboard-overview.png) | 4 パネル構成のダッシュボード全体 |
| [platform-detections.png](platform-detections.png) | プラットフォーム別検出数（棒グラフ） |

実際の Kibana で再現する手順: [kibana_infringement.md](../kibana_infringement.md)  
Elastic Cloud 接続: [elastic_cloud_setup.md](../elastic_cloud_setup.md)

プレースホルダー画像の再生成:

```powershell
python scripts/generate_screenshot_placeholders.py
```

本番デモ前に Elastic Cloud へ接続し、実データでキャプチャし直すことを推奨します。
