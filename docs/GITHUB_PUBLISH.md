# GitHub 公開手順

Legal Assassin Agent を public リポジトリとして公開し、CI を有効化する手順です。

## クイック公開（推奨）

```powershell
cd C:\Users\admin\Projects\legal-assassin-agent
.\scripts\final_submit_check.ps1
.\scripts\publish_github.ps1
```

`publish_github.ps1` は以下を実行します:

1. `final_submit_check.ps1`（verify + pytest + screenshots）
2. `gh auth status` 確認
3. リモート未設定時: `gh repo create legal-assassin-agent --public --source=. --remote=origin --push`
4. リモート設定済み時: `git push -u origin main`
5. CI workflow の状態表示（可能なら `gh run watch`）

前提: [GitHub CLI](https://cli.github.com/) で `gh auth login` 済み

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
git commit -m "Initial commit: Legal Assassin Agent"
```

`.env` は `.gitignore` で除外済みです。**API キーを commit しないでください。**

## 2. GitHub にリポジトリ作成（手動）

1. https://github.com/new
2. Repository name: `legal-assassin-agent`（任意）
3. **Public** を選択
4. README / .gitignore は追加しない（ローカルに既存）

## 3. push（手動）

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USER/legal-assassin-agent.git
git push -u origin main
```

## 4. CI 確認

```powershell
gh run list --workflow=ci.yml --limit 1
gh run watch
```

または GitHub → **Actions** タブで `CI` が green であることを確認。

## 5. ポータルへの記入

- リポジトリ URL を [PORTAL_CHECKLIST.md](PORTAL_CHECKLIST.md) に記入
- Devpost コピペ: [DEVPOST_COPY.md](DEVPOST_COPY.md)

## トラブルシューティング

| 問題 | 対処 |
|------|------|
| `git push` 認証エラー | GitHub CLI (`gh auth login`) または PAT を使用 |
| workflow ファイル push 拒否 | `gh auth refresh -h github.com -s workflow` を実行 |
| CI で evasion 不足 | workflow の bootstrap ステップを確認 |
| 大きな ZIP が commit された | `legal-assassin-agent-submission.zip` を `.gitignore` に追加して削除 |
| `gh repo create` でリポジトリ名衝突 | `$env:GITHUB_REPO_NAME = "legal-assassin-agent-2"` を設定して再実行 |
