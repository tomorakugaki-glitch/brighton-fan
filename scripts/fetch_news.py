"""
Brighton Fan Intelligence — ニュース自動収集スクリプト
毎朝 GitHub Actions で実行（21:00 UTC = 06:00 JST）

収集ソース:
  - The Guardian API  (最大15件/実行)
  - BBC Sport RSS     (最大10件/実行)
  - Sky Sports RSS    (最大10件/実行)

出力: docs/data/news.json
"""

import html as htmllib
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
BRIGHTON_QUERY = 'Brighton AND (Gross OR "van Hecke" OR Wieffer OR "De Cuyper" OR Kadıoğlu OR Gómez OR Ayari OR "Conference League")'
WORLDCUP_QUERY = '"Pascal Gross" OR "Jan Paul van Hecke" OR "Mats Wieffer" OR "Maxim De Cuyper" OR "Ferdi Kadıoğlu"'

# W杯開催期間（この期間中は WORLDCUP_QUERY も実行）
WORLDCUP_START = datetime(2026, 6, 11, tzinfo=timezone.utc)
WORLDCUP_END   = datetime(2026, 7, 20, tzinfo=timezone.utc)

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


def clean_html(text: str) -> str:
    """HTMLタグを除去し、エンティティをデコード"""
    text = re.sub(r"<[^>]+>", "", text or "")
    return htmllib.unescape(text).strip()


def guess_category(title_en: str, url: str = "") -> str:
    lower = (title_en + " " + url).lower()
    for cat, keywords in CATEGORY_RULES:
        if any(kw in lower for kw in keywords):
            return cat
    return "クラブ"


def is_worldcup_period() -> bool:
    """現在がFIFA W杯2026の開催期間（2026-06-11〜2026-07-19）か"""
    now = datetime.now(timezone.utc)
    return WORLDCUP_START <= now < WORLDCUP_END


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


def load_previous_urls() -> set:
    """前回の news.json から取得済みURLのセットを返す（is_new 判定用）"""
    try:
        prev = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        return {a.get("url", "") for a in prev.get("articles", [])}
    except Exception:
        return set()


def fetch_guardian() -> list[dict]:
    if not GUARDIAN_API_KEY:
        print("  [Guardian] APIキー未設定 — スキップ", file=sys.stderr)
        return []

    queries = [BRIGHTON_QUERY]
    if is_worldcup_period():
        queries.append(WORLDCUP_QUERY)
        print("  [Guardian] W杯期間中 — W杯選手クエリも実行")

    articles = []
    for query in queries:
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
                fields = item.get("fields", {})
                articles.append({
                    "source": "The Guardian",
                    "trust": "★★★★☆",
                    "title_en": item.get("webTitle", ""),
                    "summary_en": clean_html(fields.get("trailText", "")),
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
            # RSSのdescription/summaryを要約ベースとして取得
            raw_summary = clean_html(entry.get("summary", "") or entry.get("description", ""))
            articles.append({
                "source": source,
                "trust": trust,
                "title_en": title,
                "summary_en": raw_summary[:400] if raw_summary else "",
                "url": entry.get("link", ""),
                "published": published,
            })
        return articles
    except Exception as e:
        print(f"  [{source}] 取得エラー: {e}", file=sys.stderr)
        return []


def add_translations(articles: list[dict], glossary: dict, prev_urls: set) -> list[dict]:
    """タイトルと要約をDeepLで翻訳 → 用語集で固有名詞を統一"""
    n = len(articles)
    titles_en   = [a["title_en"] for a in articles]
    summaries_en = [a.get("summary_en", "") for a in articles]

    # タイトルと要約をまとめて1回のAPIコールで翻訳
    all_ja = translate_deepl(titles_en + summaries_en)

    # 翻訳結果数が足りない場合は原文をフォールバック
    while len(all_ja) < 2 * n:
        all_ja.append((titles_en + summaries_en)[len(all_ja)])

    for i, article in enumerate(articles):
        article["title_ja"]   = apply_glossary(all_ja[i], glossary)
        article["summary_ja"] = apply_glossary(all_ja[n + i], glossary).strip()
        article["category"]   = guess_category(article["title_en"], article.get("url", ""))
        article["is_new"]     = article.get("url", "") not in prev_urls

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

    clean_articles = []
    for idx, article in enumerate(articles):
        a = dict(article)
        a.setdefault("id", build_article_id(a, idx))
        a.pop("summary_en", None)  # 内部処理用フィールドは出力しない
        clean_articles.append(a)
    articles = clean_articles

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
    glossary  = load_glossary()
    prev_urls = load_previous_urls()

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

    print(f"[4] DeepL 翻訳中… ({len(all_articles)}件, タイトル+要約)")
    all_articles = add_translations(all_articles, glossary, prev_urls)

    print("[5] 保存中…")
    save_output(all_articles)

    new_count = sum(1 for a in all_articles if a.get("is_new"))
    print(f"=== 完了: {len(all_articles)}件（うち新着 {new_count}件）===")


if __name__ == "__main__":
    main()
