"""Resolve t.co/short URLs, fetch articles, transcripts, and repo READMEs.

Reads data/bookmarks.json, writes data/enriched.json with `enrichment`
attached to each bookmark.

For X-hosted video clips (no transcript API), the bookmark is marked
needs_manual_transcription=True. Drop the audio in data/manual_audio/
and run Whisper separately if you want them in the corpus.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
IN_FILE = DATA_DIR / "bookmarks.json"
OUT_FILE = DATA_DIR / "enriched.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; LEELO-bookmark-agent/1.0; "
        "+https://github.com/pidgin2626/leelo)"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

YOUTUBE_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([A-Za-z0-9_-]{11})"
)
GITHUB_REPO_RE = re.compile(r"^https?://github\.com/([^/]+)/([^/?#]+)")


def resolve_redirects(url: str, timeout: int = 10) -> str:
    try:
        r = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=timeout)
        return r.url
    except Exception:
        return url


def fetch_article_text(url: str, max_chars: int = 30_000) -> dict:
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        article = soup.find("article") or soup.find("main") or soup.body
        text = article.get_text("\n", strip=True) if article else ""
        text = re.sub(r"\n{3,}", "\n\n", text)
        return {
            "kind": "article",
            "title": title,
            "text": text[:max_chars],
            "truncated": len(text) > max_chars,
        }
    except Exception as e:
        return {"kind": "article", "error": str(e)}


def fetch_youtube_transcript(video_id: str) -> dict:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        segments = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join(s["text"] for s in segments)
        return {"kind": "youtube_transcript", "video_id": video_id, "text": text}
    except Exception as e:
        return {"kind": "youtube_transcript", "video_id": video_id, "error": str(e)}


def fetch_github_readme(owner: str, repo: str) -> dict:
    repo = repo.rstrip("/").replace(".git", "")
    for branch in ("main", "master"):
        raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
        try:
            r = requests.get(raw, headers=HEADERS, timeout=15)
            if r.status_code == 200 and r.text.strip():
                return {
                    "kind": "github_readme",
                    "repo": f"{owner}/{repo}",
                    "branch": branch,
                    "text": r.text[:30_000],
                }
        except Exception:
            continue
    return {"kind": "github_readme", "repo": f"{owner}/{repo}", "error": "no README found"}


def classify_and_fetch(url: str) -> dict:
    resolved = resolve_redirects(url)
    parsed = urlparse(resolved)
    host = (parsed.netloc or "").lower()

    if "youtube.com" in host or "youtu.be" in host:
        m = YOUTUBE_RE.search(resolved)
        if m:
            return {"url": resolved, **fetch_youtube_transcript(m.group(1))}

    gh = GITHUB_REPO_RE.match(resolved)
    if gh:
        return {"url": resolved, **fetch_github_readme(gh.group(1), gh.group(2))}

    if host.endswith("x.com") or host.endswith("twitter.com"):
        return {"url": resolved, "kind": "x_link", "note": "internal X link, skipped"}

    return {"url": resolved, **fetch_article_text(resolved)}


def enrich(bookmark: dict) -> dict:
    fetched: list[dict] = []
    for raw_url in bookmark.get("linked_urls", []):
        fetched.append(classify_and_fetch(raw_url))
        time.sleep(0.4)

    needs_manual = bookmark.get("has_video") and not any(
        f.get("kind") == "youtube_transcript" and not f.get("error")
        for f in fetched
    )

    return {
        **bookmark,
        "enrichment": {
            "fetched": fetched,
            "needs_manual_transcription": bool(needs_manual),
        },
    }


def main(in_file: Path = IN_FILE, out_file: Path = OUT_FILE) -> int:
    if not in_file.exists():
        print(f"Missing {in_file}. Run exporter.py first.", file=sys.stderr)
        return 1

    bookmarks = json.loads(in_file.read_text(encoding="utf-8"))
    if not bookmarks:
        print(f"{in_file} is empty — nothing to enrich.")
        out_file.write_text("[]", encoding="utf-8")
        return 0
    print(f"Enriching {len(bookmarks)} bookmarks from {in_file.name}.")

    enriched: list[dict] = []
    for i, bm in enumerate(bookmarks, 1):
        print(f"  [{i}/{len(bookmarks)}] {bm['url']}")
        try:
            enriched.append(enrich(bm))
        except Exception as e:
            print(f"    error: {e}", file=sys.stderr)
            enriched.append({**bm, "enrichment": {"error": str(e)}})

    out_file.write_text(json.dumps(enriched, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
