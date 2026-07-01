# デモ動画台本（3〜5 分）

ライブデモの代わりに提出ポータルへアップロードする画面録画用台本です。  
ライブ台本: [DEMO_SCRIPT.md](DEMO_SCRIPT.md) | ポータル記入: [PORTAL_CHECKLIST.md](PORTAL_CHECKLIST.md)

**録画リハーサル:** `.\scripts\rehearse_demo.ps1`（サーバー起動 + テレプロンプター表示）

## 推奨設定

- 解像度: 1920x1080 または 1280x720
- ツール: OBS / Loom / Xbox Game Bar
- マイク: ナレーション推奨（英語または日本語）
- 事前準備: `bootstrap.ps1` 済み、`start.bat` で http://localhost:8001 を表示

## タイムライン

| 時間 | 画面 | ナレーション例 |
|------|------|----------------|
| 0:00–0:30 | タイトル + ダッシュボード全体 | 「Legal Assassin は VOD 向け著作権保護エージェントです。自社動画のフィンガープリントを Elasticsearch に蓄積し、改変動画を検出して DMCA まで自動化します。」 |
| 0:30–1:00 | Reference Library + モードバッジ（DEMO / kNN） | 「pHash と音声指紋を正解ライブラリに登録。kNN で候補を絞り込み、フル照合で精度を上げます。」 |
| 1:00–2:30 | **RUN ALL PATROLS** → ヒット一覧 | 「5 種の改変（反転・ピッチ・速度・クロップ・2画面）を検出。TARGET ACQUIRED のトーストを確認。」 |
| 2:30–3:15 | **COMPARE** モーダル | 「正解と疑わしい動画のサムネを並べて、法務レビューを支援します。」 |
| 3:15–3:45 | **EXPORT AUDIT CSV** クリック | 「コンプライアンス用に hits と takedowns を CSV エクスポート。」 |
| 3:45–4:30 | Kibana スクリーンショットまたは実ダッシュボード | 「Elasticsearch の 3 インデックスを Kibana で可視化。プラットフォーム別検出と改変タイプ内訳。」 |
| 4:30–5:00 | エンディング（SUBMISSION の技術スタック） | 「FastAPI、Gemini、Playwright DMCA、Elastic 8.8 ダッシュボードで 24/7 著作権パトロールを実現。」 |

## 撮影チェックリスト

- [ ] ブラウザズーム 100%、ダークテーマが見える
- [ ] Patrol 前に Recent Hits が空でも可（検出の変化がわかる）
- [ ] COMPARE で両サムネが表示される
- [ ] CSV ダウンロードがブラウザで開始される
- [ ] 個人情報（`.env` の API キー）が画面に映らない

## アップロード先

- YouTube（限定公開 / 公開）
- Loom / Google Drive（リンク共有）

URL を [DEVPOST_COPY.md](DEVPOST_COPY.md) の Demo Video 欄に記入し、`.\scripts\update_submission_status.ps1` で [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md) を更新してください。
