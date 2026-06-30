# GitHub 公開手順

Legal Assassin Agent を public リポジトリとして公開し、CI を有効化する手順です。

## 前提

- [Git](https://git-scm.com/) インストール済み
- GitHub アカウント
- ローカルで `bootstrap.ps1` と `pytest` が pass

## 1. 初回 commit（未実施の場合）

```powershell
cd C:\Users\admin\Projects\legal-assassin-agent
git init
git add .
git status   # .env が含まれていないことを確認
git commit -m "Initial commit: Legal Assassin Agent (Phases 1-6)"
```

`.env` は `.gitignore` で除外済みです。**API キーを commit しないでください。**

## 2. GitHub にリポジトリ作成

1. https://github.com/new
2. Repository name: `legal-assassin-agent`（任意）
3. **Public** を選択
4. README / .gitignore は追加しない（ローカルに既存）

## 3. push

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USER/legal-assassin-agent.git
git push -u origin main
```

## 4. CI 確認

1. GitHub → **Actions** タブ
2. `CI` ワークフローが green であることを確認
3. 失敗時: bootstrap ステップのログを確認（ffmpeg は CI イメージに含まれる）

## 5. ポータルへの記入

- リポジトリ URL を [PORTAL_CHECKLIST.md](PORTAL_CHECKLIST.md) に記入
- SUBMISSION.md のクイックスタートリンクを更新（任意）

## トラブルシューティング

| 問題 | 対処 |
|------|------|
| `git push` 認証エラー | GitHub CLI (`gh auth login`) または PAT を使用 |
| CI で evasion 不足 | workflow の bootstrap ステップを確認 |
| 大きな ZIP が commit された | `legal-assassin-agent-submission.zip` を `.gitignore` に追加して削除 |
