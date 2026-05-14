# claudemd

Generate a tailored `CLAUDE.md` for any project, by interview + repo scan.

`CLAUDE.md` is the per-project "house rules" file Claude reads
automatically when working in that directory. A good one makes Claude
behave like it actually knows your project; a missing one makes it
generic.

## What you get

- **`claudemd init`** — scans your folder, asks 7 quick questions,
  writes a polished `CLAUDE.md`.
- **`claudemd audit`** — reads an existing `CLAUDE.md` and tells you
  what's missing, what's vague, and what to add.

## Install

From the repo root on Windows PowerShell:

```powershell
cd C:\Users\johnm\LEELO\apps\claudemd
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

On macOS/Linux:

```bash
cd apps/claudemd
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
export ANTHROPIC_API_KEY=sk-ant-...
```

The `pip install -e .` step gives you a global `claudemd` command
inside that venv.

## Use it

Go to any project folder you want a `CLAUDE.md` for, then:

```powershell
cd C:\path\to\some\project
claudemd init
```

It will:

1. Look around your folder (languages, frameworks, config files, README).
2. Ask you 7 short questions — hit Enter on any you want to skip.
3. Stream the generated `CLAUDE.md` to your screen and save it to the
   project root.

To audit an existing one:

```powershell
cd C:\path\to\some\project
claudemd audit
```

That prints a review with concrete suggestions — copy what you like
into your `CLAUDE.md` by hand.

## Options

`claudemd init`:

| Flag | What it does |
|---|---|
| `--path PATH` | Run against a folder other than the current one. |
| `--force` | Overwrite an existing `CLAUDE.md` without confirming. |
| `--no-interview` | Skip the questions and let Claude infer everything from the scan. Best for empty/new folders. |

`claudemd audit`:

| Flag | What it does |
|---|---|
| `--path PATH` | Audit a `CLAUDE.md` in a folder other than the current one. |

## What goes into the generated file

The generator targets these sections (it includes only the ones that
apply to your project):

- **Stack** — languages and key libraries it detected.
- **How to run / test / build** — literal commands.
- **Project layout** — what lives where.
- **Conventions** — naming, formatters, test framework, etc.
- **How to talk to me** — tone and skill level from your answers.
- **Never do** — hard rules.
- **Notes** — anything else from your "extra" answer.

## Cost

Each `init` is one Claude API call. Typical cost: a few cents. `audit`
is cheaper (smaller output).
