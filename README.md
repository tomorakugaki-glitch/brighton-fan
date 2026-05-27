# Brighton Fan Intelligence

ブライトン＆ホーヴ・アルビオンのファン向け情報収集ダッシュボード。

イングランドメディア（Guardian・BBC・Sky Sports）の最新情報を自動収集・日本語化して表示します。

## 構成

- `scripts/fetch_news.py` — ニュース自動収集スクリプト
- `data/news.json` — 最新ニュース（GitHub Actionsが毎朝更新）
- `dashboard/` — GitHub Pages 公開ダッシュボード

## セットアップ

`.env.example` をコピーして `.env` を作成し、APIキーを設定してください。

```
GUARDIAN_API_KEY=...
DEEPL_API_KEY=...
```

GitHub Secretsにも同じキーを設定してください（Actions自動実行用）。
