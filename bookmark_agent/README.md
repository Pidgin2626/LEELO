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

Two modes:

```bash
python run.py                # full run — scrape, enrich, and summarize EVERYTHING
python run.py --incremental  # only process bookmarks NEW since the last run
```

The first time you run either mode, all your current bookmarks count as
"new." After that, incremental mode remembers which tweet IDs it has
already enriched (in `state/seen_ids.json`) and skips them on later
runs, so re-running weekly costs a fraction of the full pipeline. If
there are no new bookmarks, the incremental run exits with a "nothing
to do" message before spending any API tokens.

You can also run the stages individually:

```bash
python exporter.py     # browser opens; log in once; scrolls bookmarks
python enricher.py     # fetches articles, transcripts, READMEs
python summarizer.py   # Claude proposes app ideas -> data/summary.md
```

## Outputs

Full run:

- `data/bookmarks.json` — raw scrape (tweet text, author, linked URLs, has_video)
- `data/enriched.json` — same, plus fetched article text / transcripts / READMEs
- `data/summary.md` — themes + 5-15 concrete app ideas with scope and stack

Incremental run (each file gets a timestamp):

- `data/bookmarks-new-YYYYMMDD-HHMMSS.json` — just the tweets new this run
- `data/enriched-new-YYYYMMDD-HHMMSS.json` — enriched versions of those
- `data/summary-new-YYYYMMDD-HHMMSS.md` — themes + app ideas for what's new

State:

- `state/seen_ids.json` — tweet IDs already enriched; drives the diff

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
