# LEELO Schedule Tracker

A personal tool that scrapes the user's X (Twitter) bookmarks, turns them into app ideas using Gemini, and then helps build those apps. The repo currently contains a React/Vite front-end plus a Python `bookmark_agent/` that does the scraping, and an `apps/` directory where generated apps live.

## Stack
- **Front-end:** React 19 + TypeScript, Vite 6, lucide-react icons
- **Back-end / agent:** Python (in `bookmark_agent/`)
- **AI:** Google Gemini API (via `GEMINI_API_KEY` env var)
- **Runtime:** Node.js for the web app, Python for the scraper

## How to run / test / build
The user is on **Windows PowerShell**. Use PowerShell-friendly commands (no `&&` chaining — use `;` or run commands one at a time).

Front-end (from repo root):
```powershell
npm install
npm run dev      # starts Vite on http://localhost:3000
npm run build    # production build
npm run preview  # preview the build
```

Python agent (from `bookmark_agent/`):
```powershell
cd bookmark_agent
# check for a requirements.txt or pyproject.toml first, then:
pip install -r requirements.txt
python <entry_script>.py
```

The Gemini API key goes in a file called `.env.local` at the repo root:
```
GEMINI_API_KEY=your_key_here
```
Vite picks it up automatically (see `vite.config.ts`).

## Project layout
- `App.tsx`, `index.tsx`, `index.html` — React entry points
- `constants.ts`, `types.ts` — shared values and TypeScript types
- `vite.config.ts` — Vite config; exposes `GEMINI_API_KEY` to the app as `process.env.API_KEY`
- `tsconfig.json` — TS config; `@/*` is an alias for the repo root
- `bookmark_agent/` — Python scripts that scrape X bookmarks and feed them to Gemini
- `apps/` — generated apps live here, one per idea
- `metadata.json` — AI Studio metadata, don't hand-edit

## Conventions
- Imports from the repo root use the `@/` alias, e.g. `import { Foo } from '@/types'`.
- React components are `.tsx`, plain TypeScript is `.ts`.
- No test framework or linter is set up yet — if you add one, tell the user first and explain why.
- Generated apps go inside `apps/<app-name>/` and should be self-contained.

## How to talk to me
- I'm **brand new to coding**. Explain things simply and avoid jargon — if you must use a technical term, define it in the same sentence.
- Walk me through changes **step by step**. Tell me what each command does before I run it.
- When you edit files, say *which* file and *why* in plain English.
- I'm on **Windows PowerShell**, so give me PowerShell commands, not bash. Don't use `&&` to chain commands.
- If something might break my setup, warn me first.

## Never do
- **Never push to `main`** (or any branch) without asking me first.
- **Never delete files** without confirming with me — even if they look unused.
- Don't run `npm install <new-package>` without telling me what the package does and why we need it.
- Don't commit `.env.local` or anything containing the Gemini API key.
- Don't auto-edit `metadata.json`.

## Notes
- This project was bootstrapped from Google AI Studio (see README link). The Vite config maps `GEMINI_API_KEY` to both `process.env.API_KEY` and `process.env.GEMINI_API_KEY` — either works in the React code.
- If `bookmark_agent/` has no `requirements.txt`, check the Python files' `import` statements and tell me what to `pip install` — don't guess silently.
- The scraping side likely needs X login cookies or an API token. If you see references to credentials, ask me where they should live before assuming.
