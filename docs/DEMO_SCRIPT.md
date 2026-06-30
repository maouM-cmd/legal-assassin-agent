# 審査員向けデモ台本（約 5 分）

## 1. 導入（30 秒）

「**Legal Assassin** は VOD 事業者向けの著作権保護エージェントです。自社コンテンツのフィンガープリントを学習し、YouTube・TikTok・X を 24 時間巡回。反転・ピッチ変更・速度変更・クロップ・2 画面合成を検出し、DMCA 削除申請まで自動化します。」

## 2. 正解ライブラリ + kNN（45 秒）

1. ダッシュボードの **Reference Library** を表示
2. 「5 秒間隔の pHash 列と Chromaprint 音声指紋を Elasticsearch に保存」
3. ヘルスバッジの **kNN** 表示を指し、「embedding で候補を絞り込み → フル fingerprint 照合の 2 段階マッチ」

## 3. 改変検出デモ（90 秒）

1. **RUN ALL PATROLS** をクリック（または単一プラットフォーム）
2. 5 種 evasion サンプルの検出を確認:
   - `flipped`, `pitch_shifted`, `split_screen_game`
   - **Phase 3 追加**: `speed_changed`, `cropped`
3. ヒット行の evasion バッジを説明
4. **COMPARE** ボタン → 正解 vs 疑わしい動画のサムネ左右比較
5. トースト **TARGET ACQUIRED** → **TAKEDOWN SENT**（または承認待ち）

## 4. 承認キュー・本番ゲート（45 秒）

1. `.env` で `DEMO_MODE=false` の場合: **Approval Queue** にヒットが滞留
2. **APPROVE & STRIKE** / **REJECT** / **DMCA PREVIEW** を実演
3. `DEMO_MODE=true` では高スコアは自動撃墜（デモ用）

## 5. 運用基盤（Phase 4）（60 秒）

- **Failed Takedowns** + **RETRY FAILED**: 指数バックオフ（60s → 120s → 240s）
- **Webhook**（任意）: `WEBHOOK_ENABLED=true` で Slack/Teams に通知
- **監査 CSV**: ヘッダーの **EXPORT AUDIT CSV** ボタン、または `GET /api/audit/export`
- **API キー**: 本番では `API_KEY` + `X-API-Key` ヘッダで patrol/approve を保護

## 6. Kibana（30 秒）

1. `docs/kibana/dashboard.ndjson` をインポート（Elastic 8.8+）
2. 4 パネル: プラットフォーム別検出 / 改変タイプ / 撃墜成功時系列 / 平均スコア

## 7. Q&A 想定

| 質問 | 回答 |
|------|------|
| 誤検知は？ | 動画+音声+Vision+Gemini 二次判定、閾値以上のみ自動撃墜 |
| 本番運用は？ | 承認キュー + API キー + Webhook + 監査 CSV |
| 法的問題は？ | 正当な権利者のみ使用。ES + CSV で監査証跡 |

リハーサルチェックリスト: [`scripts/rehearsal_checklist.md`](../scripts/rehearsal_checklist.md)
