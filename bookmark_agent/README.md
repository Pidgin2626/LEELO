# X Bookmark Agent

Three-stage pipeline that pulls your X (Twitter) bookmarks, fetches the
linked articles / YouTube transcripts / GitHub READMEs, and asks Claude
to propose buildable software projects from what it finds.

Runs on your machine (the browser login can't happen anywhere else).

## Setup

```bash
cd bookmark_agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
export ANTHROPIC_API_KEY=sk-ant-...
```

## Run

```bash
python run.py
```

Or run the stages individually:

```bash
python exporter.py     # browser opens; log in once; scrolls bookmarks
python enricher.py     # fetches articles, transcripts, READMEs
python summarizer.py   # Claude proposes app ideas -> data/summary.md
```

## Outputs

- `data/bookmarks.json` — raw scrape (tweet text, author, linked URLs, has_video)
- `data/enriched.json` — same, plus fetched article text / transcripts / READMEs
- `data/summary.md` — themes + 5-15 concrete app ideas with scope and stack

## Limitations

- **X-hosted video clips** can't be auto-transcribed (no public transcript
  API). Bookmarks containing them get
  `enrichment.needs_manual_transcription: true`. If you want the audio
  in the corpus, drop a WAV/MP3 into `data/manual_audio/` and run
  Whisper separately.
- **Rate-limited articles / paywalls** show up in `enriched.json` with
  an `error` field — they're skipped, not retried.
- The exporter scrolls up to 400 times. Bump `max_scrolls` in
  `exporter.py` if you have a larger bookmark history.

## After the summary

Once `data/summary.md` is generated, point me (Claude) at which app ideas
you want built and I'll scaffold and implement them in this repo.
