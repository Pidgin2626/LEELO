# council

Five AI advisors. One hard question. Three rounds. One verdict.

You give it a decision question. The panel answers independently, then
critiques each other, then a synthesizer reads everything and produces a
verdict with confidence, dissents, and a concrete next step. Each
decision is logged so you can replay it later.

## What the panel looks like

| Advisor | Model (default) | Persona |
|---|---|---|
| Claude | `claude-opus-4-7` | The Skeptic (Munger-style) — invert, find failure modes |
| GPT | `gpt-5` | The Operator — what does Monday look like? |
| Gemini | `gemini-2.5-pro` | The Founder (PG-style) — highest-upside path |
| Grok | `grok-4` | The First-Principles Engineer — what does the math say? |
| DeepSeek | `deepseek-chat` | The Contrarian — what is everyone missing? |

If you don't have all five API keys, the council runs with whatever
keys you've set. With only `ANTHROPIC_API_KEY`, use `--solo` to run all
five personas through Claude.

## Install

PowerShell on Windows:

```powershell
cd C:\Users\johnm\LEELO\apps\llm-council
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

macOS / Linux:

```bash
cd apps/llm-council
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## API keys

Set whichever ones you have. Anthropic is enough on its own (with `--solo`).

```powershell
# Always recommended (also drives the synthesizer)
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Optional — each one unlocks one more advisor
$env:OPENAI_API_KEY    = "sk-..."
$env:GOOGLE_API_KEY    = "..."           # Gemini
$env:XAI_API_KEY       = "xai-..."       # Grok
$env:DEEPSEEK_API_KEY  = "sk-..."        # DeepSeek
```

To persist on Windows, swap the `$env:` calls for:

```powershell
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
```

## Use it

```powershell
council panel
```
Shows which advisors are currently available.

```powershell
council ask "Should I take a job offer at a Series A for 60% of my current pay if it has 0.5% equity?"
```
Runs the panel. You'll see each round's progress, then the final verdict
streams to your terminal. The full transcript is saved automatically.

```powershell
council ask --file question.txt --out decision.md
```
Read a long question from a file, save the full transcript too.

```powershell
council log
```
Lists your previous decisions, newest first.

```powershell
council show 3            # just the verdict
council show 3 --full     # verdict + full 3-round transcript
```

```powershell
council ask "..." --solo
```
Force the all-Claude variant — useful if you only have one API key.

## Model overrides

Set any of these env vars to change which model a given seat uses:

```
COUNCIL_CLAUDE_MODEL   = claude-opus-4-7
COUNCIL_OPENAI_MODEL   = gpt-5
COUNCIL_GEMINI_MODEL   = gemini-2.5-pro
COUNCIL_XAI_MODEL      = grok-4
COUNCIL_DEEPSEEK_MODEL = deepseek-chat
```

## Where decisions are stored

`~/.council/decisions.db` — a SQLite database. Override with
`COUNCIL_HOME` if you want them somewhere else.

## Cost

Each `council ask` is roughly:
- 5 Round-1 calls (~1500 tokens out each)
- 5 Round-2 calls (~2000 tokens out each, plus all Round-1 answers as input)
- 1 synthesizer call (~2500 tokens out, full transcript as input)

For a panel of five frontier models, expect $0.20–$0.80 per question.
The solo (`--solo`) variant is all Claude — cheaper and faster.
