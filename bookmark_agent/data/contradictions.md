# Contradictions in Your Bookmarks

I found **2 genuine contradictions** in this corpus. Most bookmarks are complementary (different tools, different tasks) or restatements of the same "Anthropic blueprint / Claude Cowork" idea. Reporting only what actually clashes.

---

## Should you write prompts, or stop writing prompts and build a system that prompts itself?

- **What's at stake**: This decides whether the hours you spend on Claude go into collecting "7 prompt" packs or into building a persistent file/skill/loop infrastructure. It's the biggest fork in your workflow.
- **Position A — Prompts are the product**: The bulk of the corpus is "Here are 7/8/10 prompts to do X." Explicit examples: Bookmark 3 (Tanmoy_ai) "7 prompts to install your life OS," Bookmark 46 (TomBilyeu) "Steal every prompt," Bookmark 51 (TomBilyeu) "$20/month Claude does the work of a 5-person team" via prompt packs, Bookmark 84 (hasantoxr) "every AI prompt you'll ever need in one place," Bookmark 108 (Rixhabh__) "7 prompts that feel ILLEGAL."
- **Position B — Prompts are the wrong altitude**: Bookmark 57 (rubenhassid): *"Prompting is the worst way to use Claude. Here's what the top 1% do instead: They set up these 8 files once. Then they barely prompt again."* Bookmark 17 (eng_khairallah1) quoting an Anthropic engineer: *"You're not supposed to prompt Claude. You're supposed to build a system that prompts itself."* Bookmark 48 (kirillk_web3): *"Not prompts. Not chats. Skills."* Bookmark 2 (shmidtqq): *"PROMPTS ARE DEAD. LOOPS JUST REPLACED YOUR $200K ENGINEER."* Bookmark 51 (TomBilyeu) even hedges toward this camp: *"The secret sauce isn't prompts… it's which Claude feature each role runs on."*
- **My read**: Position B is stronger for anything you'll do more than twice. The "prompt pack" bookmarks are optimized to be screenshotted, not to be run for six months — notice that the "Anthropic blueprint" bookmarks you saved (22, 40, 42, 41) all describe *agents/skills/loops*, not prompt libraries. Definitive test: pick one workflow you currently run via a copy-pasted prompt (e.g., the Meta Ads brief in Bookmark 38, or the ad generator in Bookmark 30). Rebuild it once as a CLAUDE.md + skill + scheduled task per Bookmark 33/48/54. If token cost and time-to-result drop the way Bookmark 59 (–68% tokens) and Bookmark 60 (–60% output) claim, Position B wins for you.

---

## Is CLAUDE.md one file, or a system of many files?

- **What's at stake**: If you're about to sit down and set up Claude Code / Cowork "properly," you need to know whether to write one big file or a folder of small ones — the two setups take very different times and are annoying to migrate between.
- **Position A — One file**: Bookmark 33 (charliejhills, quoting Boris Cherny's setup): *"CLAUDE .md is one text file. It sits in your project folder. Claude reads it before every reply."* Bookmark 60 (NainsiDwiv50980): *"CLAUDE.md is a tiny config… Drop one file → cut output tokens by ~60%."*
- **Position B — Eight files**: Bookmark 57 (rubenhassid): *"They set up these 8 files once… File 1: about-me .md (Your identity)… Claude reads this before every task."* Bookmark 32 (rubenhassid) also pushes a folder structure ("3 subfolders: About me, Outputs & …") rather than a single config.
- **My read**: These are less irreconcilable than they look, but the framing genuinely conflicts — Position A says "the important file is CLAUDE.md, singular"; Position B says the identity/context lives in `about-me.md` and CLAUDE.md is barely mentioned. Position A is stronger because it's sourced to the person who built Claude Code (Boris Cherny, per Bookmark 33) and matches the official plugin behavior in Bookmark 19 (`claude-code-setup`). Test: read Bookmark 33's linked CLAUDE.md structure and Bookmark 57's 8-file structure side-by-side. If Ruben's 8 files are just sections that could be `@`-imported from a single CLAUDE.md, the contradiction collapses into a style preference. If they require the multi-file split to work, Position B is doing something Position A isn't.

---

Note: I looked hard for a contradiction on Extended Thinking / token usage / "adaptive thinking" and didn't find one — Bookmarks 32 and 43 both say turn Extended Thinking ON, and the token-reduction bookmarks (59, 60) are about verbosity, not about disabling thinking. Also looked for disagreement on the "1-human company / Cofounder 2" thesis (Bookmarks 22, 40, 41, 42) — every author who touches it agrees. No contradiction there to report.
