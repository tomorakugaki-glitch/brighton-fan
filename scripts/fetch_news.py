"""
Brighton Fan Intelligence — ニュース自動収集スクリプト
毎朝 GitHub Actions で実行（21:00 UTC = 06:00 JST）

収集ソース:
  - The Guardian API  (最大15件/実行)
  - BBC Sport RSS     (最大10件/実行)
  - Sky Sports RSS    (最大10件/実行)

出力: docs/data/news.json
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import feedparser
import requests
from dotenv import load_dotenv

load_dotenv()

# ─── 設定 ───────────────────────────────────────────────
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY", "")
DEEPL_API_KEY    = os.getenv("DEEPL_API_KEY", "")

GUARDIAN_URL  = "https://content.guardianapis.com/search"
DEEPL_URL     = "https://api-free.deepl.com/v2/translate"

BBC_RSS_URL  = "https://feeds.bbci.co.uk/sport/football/rss.xml"
SKY_RSS_URL  = "https://www.skysports.com/rss/12040"

OUTPUT_PATH  = Path(__file__).parent.parent / "docs" / "data" / "news.json"
ARCHIVE_DIR  = Path(__file__).parent.parent / "docs" / "data" / "archive"
GLOSSARY_PATH = Path(__file__).parent.parent / "config" / "glossary.json"

MAX_GUARDIAN = 15
MAX_RSS      = 10

JST = timezone(timedelta(hours=9))

# Guardian 検索クエリ
BRIGHTON_QUERY    = 'Brighton AND (Gross OR "van Hecke" OR Wieffer OR "De Cuyper" OR Kadıoğlu OR Gómez OR Ayari OR "World Cup")'
WORLDCUP_QUERY    = '"Pascal Gross" OR "Jan Paul van Hecke" OR "Mats Wieffer" OR "Maxim De Cuyper" OR "Ferdi Kadıoğlu"'

# カテゴリ推定キーワード（英語）
CATEGORY_RULES = [
    ("W杯",   ["world cup", "wc2026", "world cup 2026", "squad", "national team"]),
    ("移籍",   ["transfer", "signing", "sign", "deal", "bid", "fee", "loan"]),
    ("試合",   ["match", "game", "result", "score", "defeat", "beat", "drew", "win", "lost"]),
    ("欧州",   ["conference league", "europa", "champions league", "uefa"]),
    ("監督",   ["manager", "head coach", "hürzeler", "hurzeler"]),
    ("コメント", ["says", "claims", "insists", "admits", "reveals", "interview"]),
    ("戦術",   ["tactic", "formation", "system", "pressing", "analysis"]),
    ("選手",   ["player", "career", "injury", "return", "milestone"]),
    ("クラブ",  ["club", "brighton", "ownership", "stadium", "board"]),
]


def load_glossary() -> dict:
    try:
        return json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def apply_glossary(text: str, glossary: dict) -> str:
    """固有名詞を日本語表記に統一（長い表記から順に適用）"""
    for en, ja in sorted(glossary.items(), key=lambda x: -len(x[0])):
        text = text.replace(en, ja)
    return text


def guess_category(title_en: str, url: str = "") -> str:
    lower = (title_en + " " + url).lower()
    for cat, keywords in CATEGORY_RULES:
        if any(kw in lower for kw in keywords):
            return cat
    return "クラブ"


def translate_deepl(texts: list[str]) -> list[str]:
    """DeepL無料APIでまとめて翻訳（1回のAPIコール）"""
    if not DEEPL_API_KEY or not texts:
        return texts
    try:
        resp = requests.post(
            DEEPL_URL,
            data={
                "auth_key": DEEPL_API_KEY,
                "text": texts,
                "source_lang": "EN",
                "target_lang": "JA",
            },
            timeout=15,
        )
        resp.raise_for_status()
        return [t["text"] for t in resp.json()["translations"]]
    except Exception as e:
        print(f"  [DeepL] 翻訳エラー: {e}", file=sys.stderr)
        return texts


def fetch_guardian() -> list[dict]:
    if not GUARDIAN_API_KEY:
        print("  [Guardian] APIキー未設定 — スキップ", file=sys.stderr)
        return []

    articles = []
    for query in [BRIGHTON_QUERY, WORLDCUP_QUERY]:
        try:
            params = {
                "q": query,
                "api-key": GUARDIAN_API_KEY,
                "page-size": MAX_GUARDIAN,
                "order-by": "newest",
                "show-fields": "headline,trailText",
            }
            resp = requests.get(GUARDIAN_URL, params=params, timeout=15)
            resp.raise_for_status()
            results = resp.json().get("response", {}).get("results", [])
            for item in results:
                articles.append({
                    "source": "The Guardian",
                    "trust": "★★★★☆",
                    "title_en": item.get("webTitle", ""),
                    "url": item.get("webUrl", ""),
                    "published": item.get("webPublicationDate", "")[:10],
                })
        except Exception as e:
            print(f"  [Guardian] 取得エラー: {e}", file=sys.stderr)
        time.sleep(0.5)

    # 重複除去（URLベース）
    seen = set()
    unique = []
    for a in articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)
    return unique


def fetch_rss(url: str, source: str, trust: str) -> list[dict]:
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:MAX_RSS]:
            title = entry.get("title", "")
            # ブライトン関連のみ絞り込み
            if "brighton" not in title.lower() and "bha" not in title.lower():
                continue
            published = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = time.strftime("%Y-%m-%d", entry.published_parsed)
            articles.append({
                "source": source,
                "trust": trust,
                "title_en": title,
                "url": entry.get("link", ""),
                "published": published,
            })
        return articles
    except Exception as e:
        print(f"  [{source}] 取得エラー: {e}", file=sys.stderr)
        return []


def add_translations(articles: list[dict], glossary: dict) -> list[dict]:
    """タイトルをDeepLで翻訳 → 用語集で固有名詞を統一"""
    titles_en = [a["title_en"] for a in articles]
    titles_ja = translate_deepl(titles_en)

    for article, title_ja in zip(articles, titles_ja):
        article["title_ja"] = apply_glossary(title_ja, glossary)
        article["category"] = guess_category(article["title_en"], article.get("url", ""))
        article["summary_ja"] = ""  # Phase 2b で本文要約を追加予定
        article["is_new"] = True

    return articles


def build_article_id(article: dict, idx: int) -> str:
    url = article.get("url", "")
    slug = re.sub(r"[^a-z0-9]", "-", url.split("/")[-1].lower())[:40]
    return f"{article['published']}-{slug}" if slug else f"article-{idx:04d}"


def save_output(articles: list[dict]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    now_jst = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    date_str = datetime.now(JST).strftime("%Y%m%d")

    for idx, article in enumerate(articles):
        article.setdefault("id", build_article_id(article, idx))

    payload = {
        "updated_at": now_jst,
        "is_demo": False,
        "article_count": len(articles),
        "articles": articles,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  保存: {OUTPUT_PATH} ({len(articles)}件)")

    archive_path = ARCHIVE_DIR / f"news_{date_str}.json"
    archive_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  アーカイブ: {archive_path}")


def main():
    print("=== Brighton Fan Intelligence — ニュース収集開始 ===")
    glossary = load_glossary()

    print("[1] Guardian API 取得中…")
    guardian_articles = fetch_guardian()
    print(f"    {len(guardian_articles)}件取得")

    print("[2] BBC Sport RSS 取得中…")
    bbc_articles = fetch_rss(BBC_RSS_URL, "BBC Sport", "★★★★☆")
    print(f"    {len(bbc_articles)}件取得")

    print("[3] Sky Sports RSS 取得中…")
    sky_articles = fetch_rss(SKY_RSS_URL, "Sky Sports", "★★★★☆")
    print(f"    {len(sky_articles)}件取得")

    all_articles = guardian_articles + bbc_articles + sky_articles

    # 公開日降順ソート
    all_articles.sort(key=lambda a: a.get("published", ""), reverse=True)

    print(f"[4] DeepL 翻訳中… ({len(all_articles)}件)")
    all_articles = add_translations(all_articles, glossary)

    print("[5] 保存中…")
    save_output(all_articles)

    print(f"=== 完了: {len(all_articles)}件 ===")


if __name__ == "__main__":
    main()
