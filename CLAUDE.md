# Brighton Fan Intelligence Project — CLAUDE.md

> このファイルはClaude Codeへの指示書です。作業前に全体を読んでください。

---

## Tomoの目的

> プレミアリーグのブライトン＆ホーヴ・アルビオンのファン（初心者）として、イングランドメディアの最新情報を通じてクラブを深く知りたい。
> 選手・マネージャー・オーナー・チームスタッフ・戦術・移籍・選手価値など多角的な視点で、試合以外の部分も含めてシーズン全体を楽しむことが目標。
> Claude Codeを活用して、情報収集・整理・表示を自動化し、継続的に詳しくなっていく仕組みを作る。

---

## フェーズ一覧

### Phase 1：壁打ち・設計 ✅ 完了（このチャットで実施済み）

| カテゴリ | 完了内容 |
|---|---|
| クラブ情報把握 | オーナー・CEO・SD・TD・コーチングスタッフ6名を調査・整理 |
| 最新情報確認 | カンファレンスリーグ出場権確定・フロント人事変更など |
| メディアソース整理 | Guardian・BBC・Sky・Transfermarkt等の信頼度・利用方法を確定 |
| UI設計 | ダッシュボードv1〜v5をチャット内で試作。配色・タブ・動画埋め込みを決定 |
| インフラ決定 | GitHub Pages採用・Discord不要の決定 |
| Git / GitHub | 更新履歴の保存（git）・制作物の保存（GitHub）として利用。設定はClaude Codeが担当 |
| システム設計A | ニュース自動収集フロー・JSONスキーマ・スクリプト構成を確定 |
| システム設計B | 6種類のデータファイル・スキーマ・更新頻度を確定 |
| コンプライアンス | 担当者設置・各ソースの利用規約確認・セキュリティルール策定 |
| CLAUDE.md整備 | Claude Codeへの指示書として構造化 |

### Phase 2a：ニュース自動収集 ✅ 完了（2026-05-28）

| 完了内容 | 詳細 |
|---|---|
| GitHubリポジトリ作成 | `tomorakugaki-glitch/brighton-fan`（Public）|
| GitHub Pages有効化 | https://tomorakugaki-glitch.github.io/brighton-fan/ |
| ダッシュボード公開 | `docs/index.html`（ブライトンカラー・モバイル対応・デモデータ表示中） |
| fetch_news.py 作成 | Guardian API + BBC/Sky RSS・DeepL翻訳（タイトル+要約）・用語集適用 |
| GitHub Actions設定 | 毎朝6時JST自動実行・失敗時Issue通知 |
| デモデータ整備 | `docs/data/demo_news.json`（4記事・日本語翻訳済み） |
| requirements.txt | `requests feedparser python-dotenv` |
| pre-commit hook | `.env` 誤コミット防止 |
| is_new ロジック | 前回取得済みURLと比較して新着フラグを付与 |
| W杯期間クエリ制御 | 2026-06-11〜07-19 のみ WORLDCUP_QUERY を追加実行 |
| summary_ja 実装 | Guardian trailText・RSS description を DeepL 翻訳して表示 |
| スマホUX | フィルターボタン 44px タップ領域確保 |

**残作業（Tomo実施）：** 検討事項 #9・#10・#11（APIキー取得→GitHub Secrets登録）が完了すると本番データが流れ始める。

### Phase 2b：データ全体自動化（Phase 2a完了後）

試合結果・選手情報・移籍・動画の自動収集と全タブのデータ連携。

### Phase 3：発展（Phase 2b完了後）

カンファレンスリーグ情報追加・来シーズン対応・データ蓄積と振り返り機能。

---

## 現在のタスク（Phase 2b 待機中）

Phase 2a はすべて完了。Tomoが検討事項 #9〜#11（APIキー取得・GitHub Secrets登録）を実施後、本番データの流入を確認してから Phase 2b に進む。

次回セッション開始時は「フェーズ一覧 > Phase 2a 完了内容」と「検討事項リスト」を確認すること。

---

## 検討事項リスト（未タスク・将来対応）

現状のPhase 2aには含めないが、必要になったら実装を検討する項目。

| # | 項目 | 検討時期 | 備考 |
|---|---|---|---|
| 1 | カテゴリ自動分類＋フィルタUI | Phase 2b以降 | 月150記事規模では不要と判断。記事量が増えた時 or 「特定カテゴリだけ見たい」要望が出た時に再検討。実装方式はキーワードルール（LLM不使用・コストゼロ）を想定 |
| 2 | 重複記事の自動排除（複数ソース統合） | Phase 2b以降 | 同上。記事量が少ないうちは被っても許容 |
| 3 | 既読/未読ステート管理 | 未定 | `is_new` フラグだけでは弱い。ブラウザlocalStorageで管理する案 |
| 4 | embedding によるニュースクラスタリング | 未定 | 記事量が月500本を超えたら検討 |
| 5 | Transfermarkt スクレイピング導入 | Phase 2b以降 | **クラウド実行（GitHub Actions等）では即ブロックされるため除外中。** 導入する場合は「自宅PC＋タスクスケジューラ限定」か「Football-Data.org等の公式API代替」で再検討。実施前にrobots.txt再確認・コンプライアンス承認必須 |
| 6 | 【教訓】プロジェクト立ち上げ時のGitHub Pages設計確認 | 次回プロジェクト時 | GitHub Pages無料プランはPublicリポジトリのみ対応。立ち上げ前に「公開可能か？」を最初に確認し、Private必須の場合はNetlify/Cloudflare Pagesを選択肢に入れる |
| 7 | 【教訓】GitHub Pages構成では最初からdocs/内にdata/を配置 | 次回プロジェクト時 | Pages配信ルートはdocs/固定のため、JSONデータも最初からdocs/data/に置く設計にする。後からの移動は余計なgit history汚染になる |
| 8 | 【教訓】Previewサーバーの.claude/launch.json配置先 | 次回プロジェクト時 | preview_start等のPreviewツールはCWD（Claude Codeの起動ディレクトリ）の.claude/launch.jsonを参照する。サブプロジェクト内ではなくCWD側に作成すること |
| 9 | **【Tomo作業】Guardian APIキー取得** | 本格稼働前に必須 | https://open-platform.theguardian.com/access/ で無料登録。取得後はGitHub Secretsに `GUARDIAN_API_KEY` として登録 |
| 10 | **【Tomo作業】DeepL APIキー取得** | 本格稼働前に必須 | https://www.deepl.com/pro#developer で無料登録（クレカ不要）。取得後はGitHub Secretsに `DEEPL_API_KEY` として登録 |
| 11 | **【Tomo作業】GitHub Secretsにキーを登録** | #9・#10完了後すぐ | https://github.com/tomorakugaki-glitch/brighton-fan/settings/secrets/actions → `GUARDIAN_API_KEY` と `DEEPL_API_KEY` を追加。登録後にActions → Run workflow で動作確認 |

---

## 絶対に守るルール

- **言語：** Tomoへの報告・説明はすべて日本語
- **コスト：** 費用が発生する選択肢を採用する前に必ずTomoに確認する
- **セキュリティ：** APIキー・パスワードは `.env` にのみ記載。`.gitignore` で除外し、GitHubには絶対にpushしない
- **データ削除：** `data/archive/` の中身は削除しない。上書き・論理削除のみ
- **承認：** 設計に迷ったときはTomoに確認してから進める
- **コンプライアンス：** 新ソース追加・スクレイピング実装・データ利用変更の前に、必ず下記「コンプライアンス担当」セクションを確認してから実装する

---

## 🛡️ コンプライアンス担当（COMPLIANCE OFFICER）

**役割：** セキュリティ・サイト利用規約・法的コンプライアンスの観点から開発全般を監視する。新機能追加・ソース変更・データ利用の際は必ずこのセクションを参照すること。

### セキュリティチェックリスト

実装前に以下を必ず確認する。

- [ ] APIキー・パスワードが `.env` 以外に記載されていないか
- [ ] `.gitignore` に `.env` が含まれているか
- [ ] `git status` で機密ファイルがステージングに含まれていないか
- [ ] ハードコードされた認証情報がコード内にないか
- [ ] エラーログにAPIキーが出力される可能性がないか
- [ ] **pre-commit hook** を設定して `.env` の誤コミットをブロックしているか（`.git/hooks/pre-commit` で `.env` を含むコミットを拒否）
- [ ] GitHub Actionsに移行後、APIキーは `.env` ではなく **GitHub Secrets** に設定されているか

### 各ソースの利用規約（確認済み）

| ソース | 利用方法 | 許可範囲 | 注意事項 |
|---|---|---|---|
| Guardian API | 公式API | 個人・非商用は無料。帰属表示（"Powered by The Guardian"）が必要 | 商用利用は別途契約が必要 |
| BBC Sport RSS | RSSフィード | 個人利用は可。記事の全文転載は不可 | 要約・リンク表示にとどめる |
| Sky Sports RSS | RSSフィード | 個人利用は可。全文転載は不可 | 要約・リンク表示にとどめる |
| Transfermarkt | スクレイピング | 個人・非商用の軽量アクセスは黙認範囲。公式APIなし | アクセス間隔3秒以上必須。過負荷をかけない |
| Football-Data.org | 公式API | 無料プランで個人利用可。帰属表示推奨 | 10コール/分の制限を厳守 |
| YouTube Data API | 公式API | Google利用規約に準拠。動画のダウンロード・保存は禁止 | 動画IDと埋め込み表示のみ |
| GitHub Pages | ホスティング | 個人・非商用は無料 | 公開リポジトリに機密情報を含めない |

### コンプライアンスルール

**データの扱い：**
- 記事の全文をJSONに保存しない。タイトル・要約・URLのみ保存する
- ダッシュボードには必ず元記事へのリンクを表示する
- リンクは**原文URLを直接貼る**（Google Translateラッピングは不安定なため使用しない）
- **記事タイトル自体をクリッカブルリンクにする**（「日本語で読む」等のラベルテキストは追加しない）
- 新しいタブで開く（`target="_blank"`）
- スマホChromeの「ページを翻訳」自動ポップアップ機能で日本語化される前提
- 翻訳は日本語化したタイトル・要約レベルにとどめ、原文の大量複製にならないようにする
- **翻訳エンジン：DeepL API 無料枠固定**（月50万文字無料・本プロジェクトは月約1.5万文字使用のため永久に無料枠内）

**BBC/Sky RSS 要約翻訳ルール（派生著作物対策）：**
- RSS から取得した記事本文・全文を JSON に保存しない。タイトル・URLのみ取得する
- `summary_ja` はDeepL翻訳後に**必ず自分の言葉で要約し直す**（原文の翻訳そのままはNG）
- `summary_ja` は2〜3文・120〜200字以内に収める
- ダッシュボード上に必ず**原文URLへのリンクを記事タイトルとして表示**する
- 原文タイトルを DeepL 翻訳したものを `title_ja` として表示してよい（短文の翻訳は許容範囲）
- `summary_ja` に「〜と報じられている」「〜とされる」等の**伝聞形を使い、原文の大量複製にならないよう注意**する

**スクレイピング：**
- 実装前に対象サイトの `robots.txt` を確認し、禁止パスにアクセスしない
- アクセス間隔は最低3秒。エラー時は指数バックオフで再試行する
- User-Agentを偽装しない。プロジェクト名を含めた正直なUser-Agentを使用する

**新ソース追加時の手順：**
1. 対象サイトの `robots.txt` と利用規約を確認する
2. このセクションの表に追記してからTomoに承認を得る
3. 承認後に実装する

---

## プロジェクト概要

Tomoがブライトン＆ホーヴ・アルビオンについてイングランドメディアを通じて深く知り、シーズンを通して多角的に楽しむための情報収集・自動化プロジェクト。

**Tomoについて：** コードは書かない。Claude Codeへ自然言語で指示する。プッシュ通知は不要で、自分からダッシュボードを見に行くスタイル。

**知りたい領域：** 選手・監督・戦術・移籍・選手価値・オーナー・フロント・チームスタッフ

---

## 環境・ツール

| 項目 | 状態 |
|---|---|
| Claude Code | セットアップ済み |
| Git / GitHub | セットアップ済み。リポジトリ: https://github.com/tomorakugaki-glitch/brighton-fan |
| Chrome | セットアップ済み |
| Guardian API | **未取得**（検討事項#9参照） |
| DeepL API | **未取得**（検討事項#10参照） |
| GitHub Secrets | **未登録**（検討事項#11参照） |
| ダッシュボード公開先 | GitHub Pages: https://tomorakugaki-glitch.github.io/brighton-fan/（`master`ブランチの `/docs` フォルダ） |
| OS | Windows |
| Python | 3.11（GitHub Actions上で動作確認済み） |

---

## 技術仕様

### A：ニュース自動収集（現在のタスク）

#### リポジトリ構成

```
brighton-fan/                    ← GitHubリポジトリ（Public）
├── .env                         ← APIキー（gitignore対象・絶対にpushしない。ローカルテスト用）
├── .env.example                 ← テンプレート（pushしてOK。実際のキーは書かない）
├── .gitignore                   ← .env / .env.local を除外
├── requirements.txt             ← requests feedparser python-dotenv
├── .github/
│   └── workflows/
│       └── fetch_news.yml       ← GitHub Actions（毎朝21:00 UTC = 6:00 JST・失敗時Issue通知）
├── scripts/
│   ├── fetch_news.py            ← ✅ Phase 2a完了（Guardian API + BBC/Sky RSS + DeepL翻訳）
│   ├── fetch_all.py             ← 全モジュールをまとめて実行（Phase 2b〜）
│   ├── modules/                 ← Phase 2bで追加
│   │   ├── news.py
│   │   ├── matches.py
│   │   ├── players.py
│   │   ├── transfers.py
│   │   └── videos.py
│   └── utils/                   ← Phase 2bで追加
│       ├── translate.py
│       └── archive.py
├── config/
│   └── glossary.json            ← 人名・用語表記統一辞書（翻訳後にreplace処理）
└── docs/                        ← GitHub Pages配信ルート（masterブランチの/docs）
    ├── index.html               ← ✅ Phase 2a完了（ブライトンカラー・モバイル対応）
    └── data/
        ├── news.json            ← 最新ニュース（毎回上書き・0件時はデモにフォールバック）
        ├── demo_news.json       ← 初期表示用デモデータ（削除しない）
        ├── match.json           ← Phase 2b〜
        ├── players.json         ← Phase 2b〜
        ├── transfers.json       ← Phase 2b〜
        ├── videos.json          ← Phase 2b〜
        ├── club.json            ← Phase 2b〜
        └── archive/             ← news_YYYYMMDD.json で日付別保存（削除しない）
```

> `config.py` は不要（python-dotenvで直接読込）。`utils/git_push.py` は不要（GitHub Actionsが直接push）。`modules/` `utils/` はPhase 2bで追加。`dashboard/` フォルダは廃止（`docs/` に統合済み）。

#### 自動実行フロー

```
GitHub Actions cron（毎朝21:00 UTC = 日本時間6:00）
→ fetch_news.py 実行
→ 各ソースから記事取得（Guardian API・BBC RSS・Sky RSS）
→ DeepL API（無料枠）でタイトル・要約を日本語翻訳（1回のAPIコールでまとめて処理）
→ glossary.json で人名表記を統一（翻訳後にreplace処理）
→ docs/data/news.json 上書き・archive/ にバックアップ
→ git add docs/data/ → git commit → git push（Actions内で自動）
→ GitHub Pages が自動反映
→ 失敗時：GitHub Issue を自動作成してTomoに通知
```

#### 収集ソース

| ソース | 方法 | APIキー | 信頼度 |
|---|---|---|---|
| The Guardian | 公式API | 要取得（無料・5000回/日） | ★★★★☆ |
| BBC Sport | RSS | 不要 | ★★★★☆ |
| Sky Sports | RSS | 不要 | ★★★★☆ |
| ~~Transfermarkt~~ | ~~スクレイピング~~ | — | **Phase 2a除外**（クラウド実行でブロックリスク。検討事項#5参照） |

#### news.json スキーマ

```json
{
  "updated_at": "2026-05-28 07:00",
  "article_count": 12,
  "articles": [
    {
      "id": "guardian-abc123",
      "source": "The Guardian",
      "trust": "★★★★☆",
      "category": "移籍",
      "title_en": "Brighton eye summer signing...",
      "title_ja": "ブライトン、夏の補強候補を視察",
      "summary_ja": "詳細説明...",
      "url": "https://...",
      "published": "2026-05-28",
      "is_new": true
    }
  ]
}
```

`updated_at` は `"YYYY-MM-DD HH:MM"` 形式で統一（全JSONファイル共通）。デモデータは `"is_demo": true` フラグで識別。

`category` は参考分類（必須ではない）。定義値：「移籍」「試合」「戦術」「クラブ」「選手」「欧州」「監督」「コメント」「W杯」。Phase 2a では分類不要。

`summary_ja` は2〜3文・120〜200字以内。BBC/Sky記事の要約は原文の大量複製にならないよう必ず自分の言葉で要約し、原文タイトルリンクを必ず併記すること（コンプライアンス要件）。

**summary_ja 品質基準（初心者ファン向け）：**
- **5W1H を意識**：誰が・何を・どこで・いつ・なぜ・どのように の主要要素を盛り込む
- **プレミアリーグ初心者向けに書く**：「GW38」は「第38節（最終節）」、「ウィンドウ」は「移籍市場」など用語を補足する
- **数字・固有名詞は正確に**：スコア・順位・移籍金など具体的な数字は省略しない
- **語調**：「〜とみられる」「〜と報じられている」など報道ベースの表現で中立を保つ
- **翻訳後、glossary.json の replace 処理**を必ず適用してから保存する（人名表記統一のため）

#### ダッシュボード要件（docs/index.html）

- **配色：** ブライトンブルー `#0057B8`・ゴールド `#FFCD00`・ダーク背景 `#07111f`
- **Phase 2aタブ構成：** **ニュースのみ**（概要/スカッド/戦術/移籍/動画/クラブはPhase 2b実装時に順次追加）
- **ニュースタブ：** `data/news.json` を fetch して表示。`news.json` 未存在時は `demo_news.json` を自動表示
- **記事リンク：** 原文URLを直接貼る。**記事タイトル自体をクリッカブルリンクにする**（別途ラベルは不要）・新しいタブで開く・スマホChromeの自動翻訳ポップアップで日本語化される
- **動画タブ：** Phase 2bで追加（公式BHAFC YouTube・U-NEXT YouTube 埋め込み）
- **フォント：** Barlow Condensed（英語見出し）+ Noto Sans JP（日本語本文）
- **スマホUX基準：**
  - タップ領域：最小44×44px
  - フォントサイズ：最小16px（iOS自動ズーム防止）
  - 横スクロール禁止（`overflow-x: hidden`）
  - 画像・カード：`width: 100%`
  - カード間余白：最小12px

---

#### デモデータ（data/demo_news.json）

ダッシュボード初回公開時・fetch_news.pyが未実行の場合に表示する初期データ。
ルートの `data/` フォルダに配置する。`data/news.json` が存在しない場合は自動的にこのデモデータを表示すること。

```json
{
  "updated_at": "2026-05-28 07:00",
  "is_demo": true,
  "article_count": 4,
  "articles": [
    {
      "id": "demo-001",
      "source": "BBC Sport",
      "trust": "★★★★☆",
      "category": "欧州",
      "is_demo": true,
      "title_en": "Brighton secure Conference League spot with sixth-place finish",
      "title_ja": "ブライトン、6位フィニッシュでカンファレンスリーグ出場権を確保",
      "summary_ja": "2025-26シーズン最終節でマンチェスター・ユナイテッドに0-3で敗れたものの、6位でシーズンを終えUEFAカンファレンスリーグの出場権を獲得。クラブ史上2度目の欧州挑戦となる。",
      "url": "https://www.bbc.co.uk/sport/football/brighton",
      "published": "2026-05-24",
      "is_new": false
    },
    {
      "id": "demo-002",
      "source": "The Guardian",
      "trust": "★★★★☆",
      "category": "監督",
      "title_en": "Hürzeler: 'We should be proud of what we achieved this season'",
      "title_ja": "フュルツェラー「今シーズンの成果を誇りに思う」",
      "summary_ja": "ヘッドコーチのファビアン・フュルツェラーが最終節後の会見でシーズンを振り返り、欧州出場権確保を称えるコメントを発表。就任2年目でさらなる飛躍を誓った。",
      "url": "https://www.theguardian.com/football/brighton",
      "published": "2026-05-24",
      "is_new": false
    },
    {
      "id": "demo-003",
      "source": "Sky Sports",
      "trust": "★★★★☆",
      "category": "移籍",
      "title_en": "Brighton eyeing summer reinforcements ahead of Conference League campaign",
      "title_ja": "ブライトン、カンファレンスリーグ参戦に向けて夏の補強を検討",
      "summary_ja": "スポーツディレクターのジェイソン・アイトが複数のターゲットを視察中との報道。欧州戦に対応できるスカッドの厚みを加えることが優先事項とされている。",
      "url": "https://www.skysports.com/football/brighton",
      "published": "2026-05-25",
      "is_new": false
    },
    {
      "id": "demo-004",
      "source": "The Guardian",
      "trust": "★★★★☆",
      "category": "クラブ",
      "title_en": "Tony Bloom's Brighton: the data-driven club reshaping English football",
      "title_ja": "トニー・ブルームのブライトン：イングランド・フットボールを塗り替えるデータ駆動型クラブ",
      "summary_ja": "オーナーのトニー・ブルームが構築した「発掘→育成→売却」モデルと、スポーツベッティング会社Starlizardのデータ分析がいかにブライトンを変えたかを解説する長編記事。",
      "url": "https://www.theguardian.com/football/brighton",
      "published": "2026-05-20",
      "is_new": false
    }
  ]
}
```

**表示ルール：**
- `docs/data/news.json` が存在し **かつ** `article_count > 0` の場合 → 実データを表示
- `news.json` が存在しない・取得失敗・`article_count === 0` のいずれかの場合 → `demo_news.json` に自動フォールバック
- `is_demo: true` のデータ表示中は画面上部に「⚠ デモデータ表示中 — 実データは毎朝6時（JST）に自動更新されます」と表示する

---

#### 用語集仕様（config/glossary.json）

DeepL翻訳後にPythonのreplace処理で表記を統一する。

**適用ルール：**
- `title_ja` および `summary_ja` の生成後、保存前に replace 処理を実行する
- キーは**長いものから順に**適用する（例：「Jan Paul van Hecke」→「ファン・ヘッケ」の順でないと部分一致で上書きされる）
- 新選手加入・人事変更のたびにこのファイルに追記し、フルネーム → 省略名の2パターンを必ず登録する
- 表記のブレ例：「フュルツェラー」vs「ヒュルツェラー」→ glossary で統一側に揃える

```json
{
  "Hürzeler": "フュルツェラー",
  "Fabian Hürzeler": "ファビアン・フュルツェラー",
  "van Hecke": "ファン・ヘッケ",
  "Jan Paul van Hecke": "ヤン・パウル・ファン・ヘッケ",
  "Wieffer": "ヴィーファー",
  "De Cuyper": "デ・クイペル",
  "Kadıoğlu": "カディオール",
  "Verbruggen": "フェルブルッゲン",
  "Tony Bloom": "トニー・ブルーム",
  "Jason Ayto": "ジェイソン・アイトー",
  "Brighton": "ブライトン",
  "Brighton & Hove Albion": "ブライトン＆ホーヴ・アルビオン"
}
```

> 新選手加入・人事変更のたびに追記する。

---

#### W杯選手追跡クエリ設計（Guardian API）

W杯期間中（2026年6月11日〜7月19日）はブライトン選手のW杯関連記事も自動収集する。

```python
# Guardian API メインクエリ（毎日実行）
BRIGHTON_QUERY = 'Brighton AND (Gross OR "van Hecke" OR Wieffer OR "De Cuyper" OR Kadıoğlu OR Gómez OR Ayari OR "Conference League")'

# W杯期間中のみ追加実行（2026-06-11〜07-19）
WORLDCUP_QUERY = '"Pascal Gross" OR "Jan Paul van Hecke" OR "Mats Wieffer" OR "Maxim De Cuyper" OR "Ferdi Kadıoğlu"'
```

> W杯期間中は1日2回取得（朝6時・夜21時）に増やすことを検討事項#6として追加予定。



### B：データ全体設計（Phase 2a 完了後に実装）

設計は完了済み。詳細は「技術仕様 > B」を参照。

---

## 参照データ

### クラブ関係者（選手以外）

| 名前 | 役職 | 備考 |
|---|---|---|
| Tony Bloom | オーナー・会長 | £1.3B資産。Starlizard創設者。「ザ・リザード」。累計投資£360M超 |
| Paul Barber OBE | 副会長・CEO | クラブ日常経営を統括 |
| Jason Ayto | スポーツディレクター | 2025年9月就任。元アーセナル暫定SD |
| Mike Cave | テクニカルディレクター | 2025年9月昇格。2022年フラムより加入 |
| Fabian Hürzeler 🇩🇪🇺🇸 | ヘッドコーチ | 2024年6月就任。就任時31歳でプレミア史上最年少監督 |
| Jonas Scheuermann 🇩🇪 | アシスタントヘッドコーチ | 元アウクスブルクコーチ |
| Andrew Crofts 🏴󠁧󠁢󠁷󠁬󠁳󠁿 | アシスタントヘッドコーチ | 元ブライトン主将。ウェールズ代表コーチも兼務 |
| Daniel Niedzkowski 🇩🇪 | アシスタントコーチ | 2025年1月加入。元DFBプロライセンス責任者 |
| Jelle ten Rouwelaar 🇳🇱 | GKコーチ | 2025年7月加入 |
| Jack Stern 🇬🇧 | GKコーチ | フュルツェラー就任時から在籍 |

### 最新情報ログ

| 日付 | カテゴリ | 内容 | 信頼度 |
|---|---|---|---|
| 2026-05-24 | 結果 | ブライトン 0-3 マンU（GW38 最終節）6位確定 | ✅ 確定 |
| 2026-05-24 | **欧州** | **2026/27 UEFAカンファレンスリーグ出場権獲得**（史上2度目） | ✅ 確定 |
| 2026-05-24 | コメント | フュルツェラー「この成果を誇りに思う」（公式） | ✅ 確定 |
| 2025-09月 | 人事 | Jason Ayto（SD）就任・Mike Cave（TD）昇格 | ✅ 確定 |
| 2025-12月 | 経営 | ブルームに$17.5M賭博利益配分訴訟。ブルーム側は全面否定 | ✅ 確定 |

### 🌍 FIFA ワールドカップ 2026 — ブライトン選手の代表選出状況

**開催：** 2026年6月11日〜7月19日（アメリカ・カナダ・メキシコ）  
**最終スカッド締切：** 2026年6月2日

| 選手 | 代表 | ポジション | 選出状況 |
|---|---|---|---|
| Pascal Groß（グロス） | 🇩🇪 ドイツ | MF | ✅ 選出確定 |
| Jan Paul van Hecke（ファン・ヘッケ） | 🇳🇱 オランダ | CB | ✅ 選出確定 |
| Mats Wieffer（ヴィーファー） | 🇳🇱 オランダ | MF | ✅ 選出確定 |
| Maxim De Cuyper（デ・クイペル） | 🇧🇪 ベルギー | LB | ✅ 選出確定 |
| Ferdi Kadıoğlu（カディオール） | 🇹🇷 トルコ | LB/MF | ✅ 選出確定 |
| Diego Gómez（ゴメス） | 🇵🇾 パラグアイ | MF | ✅ 選出確定 |
| Yasin Ayari（アヤリ） | 🇸🇪 スウェーデン | MF | ✅ 選出確定 |

**→ 計7選手がワールドカップに出場予定**（最終スカッドは6月2日確定）

**注目ポイント：**
- グロスがドイツ代表に選出。ブライトンの中心選手がW杯の舞台へ
- オランダ代表に2人（ファン・ヘッケ・ヴィーファー）同時選出
- ヴィーファーは今シーズン加入後すぐ代表定着

**ワールドカップ情報の追跡方針：**
- ニュースタブで対象選手のW杯関連記事も自動収集する
- `news.py` のキーワードに選手名を追加して対応する
- `match.json` にW杯試合結果トラッキングを追加する（Phase 2b）

---

*最終更新：2026-05-28（Phase 2a完了・仕様修正・コード改善済み）*

---

### B：データ全体設計（設計完了・Phase 2a完了後に実装）

#### データファイル一覧

| ファイル | 更新頻度 | タイミング | 取得ソース |
|---|---|---|---|
| news.json | 毎日 | 朝6時 | Guardian API・BBC RSS・Sky RSS |
| transfers.json | 毎日 | 朝6時 | Guardian・Sky RSS・Fabrizio Romano RSS |
| match.json | 週2回 | 月・試合翌日 | Football-Data.org（無料API・チームID: 397） |
| players.json | 週1回 | 月曜朝 | Transfermarkt スクレイピング（3秒間隔） |
| videos.json | 試合翌日 | 試合翌朝 | YouTube Data API または手動更新 |
| club.json | 週1回 | 月曜朝6時 | 公式サイトスクレイピング＋ニュース記事からの人事変更検出（自動化を試みる。困難な場合はTomoに変更候補を提示して承認後に更新） |

#### リポジトリ構成（完全版）

```
brighton/
├── .env
├── .gitignore
├── scripts/
│   ├── fetch_all.py           ← 全モジュールを順番に実行
│   ├── modules/
│   │   ├── news.py
│   │   ├── matches.py
│   │   ├── players.py
│   │   ├── transfers.py
│   │   └── videos.py
│   ├── utils/
│   │   ├── translate.py       ← DeepL API翻訳（共通・python-dotenvで直接読込）
│   │   ├── archive.py         ← archiveバックアップ（共通）
│   │   └── git_push.py        ← git add/commit/push（ローカル実行時のみ。GitHub Actions移行後は不要）
│   └── run_daily.bat          ← ローカルPC実行用（GitHub Actions移行後は廃止予定）
├── data/
│   ├── news.json
│   ├── match.json
│   ├── players.json
│   ├── transfers.json
│   ├── videos.json
│   ├── club.json
│   └── archive/               ← YYYY-MM-DD/ で日付別保存（削除しない）
└── dashboard/
    ├── index.html
    ├── app.js
    └── style.css
```

#### 各JSONスキーマ

**match.json**
```json
{
  "updated_at": "2026-05-28 07:00",
  "next_match": {
    "date": "2026-08-16", "time_jst": "21:00",
    "opponent": "Arsenal", "venue": "home",
    "competition": "プレミアリーグ", "matchweek": 1
  },
  "recent_results": [
    {
      "date": "2026-05-24", "opponent": "Manchester United",
      "score_for": 0, "score_against": 3, "result": "L",
      "venue": "home", "competition": "プレミアリーグ", "matchweek": 38
    }
  ],
  "season_stats": {
    "position": 6, "played": 38, "won": 16, "drawn": 4,
    "lost": 18, "goals_for": 48, "goals_against": 62, "points": 52
  }
}
```

**players.json**
```json
{
  "updated_at": "2026-05-26 06:00",
  "players": [
    {
      "id": "bart-verbruggen", "number": 1,
      "name": "Bart Verbruggen", "name_ja": "バルト・フェルブルッゲン",
      "nationality": "🇳🇱", "position": "GK", "age": 23,
      "market_value": "€25M", "contract_until": "2028",
      "stats": { "appearances": 30, "goals": 0, "assists": 0 }
    }
  ]
}
```

**transfers.json**
```json
{
  "updated_at": "2026-05-28 07:00",
  "confirmed": [
    {
      "direction": "IN", "player": "Yankuba Minteh",
      "from_club": "Newcastle", "fee": "€35M",
      "date": "2024-07-01", "season": "2024-25", "source_url": "https://..."
    }
  ],
  "rumours": [
    {
      "direction": "IN", "player": "未公表・中盤選手",
      "from_league": "Bundesliga", "trust": "★★☆☆☆",
      "source": "The Guardian", "date": "2026-05-25",
      "summary_ja": "夏のウィンドウに向けて視察中との報道"
    }
  ]
}
```

**videos.json**
```json
{
  "updated_at": "2026-05-25 06:00",
  "official_bhafc": [
    {
      "video_id": "dmzWWLEXBb0",
      "title_en": "HIGHLIGHTS | Leeds v Brighton",
      "title_ja": "リーズ vs ブライトン ハイライト",
      "matchweek": "GW37", "date": "2026-05-17", "type": "highlight"
    }
  ],
  "unext_youtube": [
    {
      "video_id": "Ce_-pZq8Ld8",
      "title_ja": "ブライトン v マンU｜ショートハイライト",
      "matchweek": "第38節", "date": "2026-05-24"
    }
  ]
}
```

**club.json**（自動化を目指す。困難な場合は変更候補をTomoに提示して承認後に更新）
```json
{
  "updated_at": "2026-05-27 06:00",
  "board": [
    {
      "name": "Tony Bloom", "role": "オーナー・会長", "emoji": "🦎",
      "nationality": "🇬🇧",
      "bio": "£1.3B資産。Starlizard創設者。「ザ・リザード」。累計投資£360M超"
    }
  ],
  "coaching_staff": [],
  "philosophy": [],
  "related_clubs": [],
  "current_topics": []
}
```

#### スケジューラの動作

`run_daily.bat` を毎朝6時に実行。`fetch_all.py` が曜日・試合日を判定して必要なモジュールだけ動かす。

```
毎日実行：news.py・transfers.py
月曜のみ：players.py
試合翌日：matches.py・videos.py
```

#### club.json 自動化仕様（modules/club.py）

自動化を最大限に試みる。段階的に実装すること。

**Step 1（必須実装）：ニュース記事からの人事変更検出**
- 毎週月曜に実行済みのnews.jsonを解析する
- 「appointed」「sacked」「resigned」「joins」「leaves」「new manager」「new director」等のキーワードを含むブライトン関連記事を検出する
- 検出した場合、変更候補をターミナルに出力してTomoに確認を促す

**Step 2（可能なら実装）：公式サイトスクレイピング**
- `https://www.brightonandhovealbion.com/club/staff` または類似ページをスクレイピングする
- 現在のclub.jsonの内容と差分を比較する
- 差分がある場合のみTomoに確認を促す（差分がなければ何もしない）

**Step 3（困難な場合の対応）：**
- Step 1・2の実装が技術的に困難または利用規約上問題がある場合は、実装せずにTomoへ報告する
- 「club.jsonの自動更新は現状困難です。手動更新の手順を案内します」と日本語で伝える
- 手動更新の簡易手順をわかりやすく案内する

**いずれの場合もclub.jsonを自動で上書きしない。必ずTomoの承認を得てから更新する。**
