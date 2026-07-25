# Tool Shopping List

## Start here — top 5

Ranked by frequency × fit with your themes (Claude power-user, agent-driven marketing, local-service lead gen, second-brain) × speed to first result.

1. **Meta Ads MCP + CLI** — Direct authorized access to your Meta Ads account from Claude/ChatGPT via natural language.
   - **This week's action**: Install the Meta Ads MCP from Bryan Cano's resources (bookmark 47), connect one active ad account, and have Claude run "audit my last 30 days of creatives and flag the 3 worst-performing ad sets."

2. **Obsidian** — Local markdown vault; the substrate for the "neural-network-shaped second brain" pattern in bookmark 5.
   - **This week's action**: Install Obsidian, create a vault called `brain`, drop in 10 markdown notes from your recent projects, then point Claude Code at that folder (per Karpathy's second-brain pattern in bookmarks 10–11) and ask it to build a concept map.

3. **Google Antigravity** — Google's new agentic dev environment; bookmark 107 shows building a shipped thing in 30 minutes.
   - **This week's action**: Go to Antigravity, pick one tweet/idea from your bookmarks (e.g., the ad-generator in bookmark 30), and ship a working prototype in one sitting.

4. **openclaw / Clawdbot** — Open-source personal AI with full system access, interfaces via WhatsApp/Discord/Telegram (bookmarks 92–94). Directly relevant to your local-service automation interests (a user in b92 used it to schedule shifts for a tea store).
   - **This week's action**: Deploy openclaw on AWS free tier (the one-command install from bookmark 94), wire it to your personal WhatsApp, and give it one recurring task like "summarize my calendar every morning at 7am."

5. **Pika MCP** — Gives Claude a face, name, personality, and multimodal generation (bookmark 45). Fastest way to turn Claude into a branded content engine, which pairs with your Instagram/carousel/Reels bookmarks (14, 20, 55, 67, 74).
   - **This week's action**: Install Pika MCP, define one persona ("brand strategist for [your niche]"), and generate one 6-slide carousel to A/B against your normal output.

---

## Full list (alphabetical)

### AWS (free tier)
- **What it does**: Cloud hosting; used in the corpus to deploy openclaw in <5 minutes.
- **Category**: hosted platform
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 94
- **Why you'd care**: Cheapest way to keep a personal AI agent (openclaw) running 24/7.
- **Setup effort**: medium

### Canva
- **What it does**: Drag-and-drop graphic design.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 87
- **Why you'd care**: Fallback for social/ad creatives when your AI pipeline outputs raw text.
- **Setup effort**: trivial

### Cartesia Sonic 3
- **What it does**: Low-latency commercial voice model.
- **Category**: API
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 105
- **Why you'd care**: Only mentioned as a benchmark that Chatterbox Turbo beats — useful reference point, not a buy.
- **Setup effort**: medium

### Chatterbox Turbo
- **What it does**: MIT-licensed voice model with <150ms latency and 5-second voice cloning; beats ElevenLabs Turbo per bookmark 105.
- **Category**: open-source library
- **Cost tier**: free
- **Mentioned in bookmarks**: 105
- **Why you'd care**: Self-hosted voiceover for your Reels/Instagram automations (b55, b67) with no per-character billing.
- **Setup effort**: medium

### ChatGPT
- **What it does**: OpenAI's chatbot.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 24, 47, 79, 87, 104, 108, 116, 128
- **Why you'd care**: Cross-reference model for prompts you already run in Claude; useful when a workflow requires GPT-specific tools.
- **Setup effort**: trivial

### claude-code-setup (Anthropic plugin)
- **What it does**: Official plugin that scans your project and recommends hooks, subagents, and skills for Claude Code.
- **Category**: open-source library
- **Cost tier**: free
- **Mentioned in bookmarks**: 19
- **Why you'd care**: Fastest upgrade path for your Claude Code setup — directly on your dominant theme.
- **Setup effort**: trivial

### Claude Cowork (mode)
- **What it does**: Claude's file/folder-scoped workspace mode; the "voice lives here" setup discussed in b32, b43, b58, b64, b81, b100.
- **Category**: other (Claude mode — included per your callout rule)
- **Cost tier**: included in Claude plan
- **Mentioned in bookmarks**: 15, 32, 43, 58, 63, 64, 68, 81, 100
- **Why you'd care**: The single most-mentioned "power user" surface across your corpus.
- **Setup effort**: medium

### Cofounder 2
- **What it does**: Agent orchestration infra for running a "one-person billion-dollar company" across engineering, sales, marketing, ops, design (b41).
- **Category**: hosted platform
- **Cost tier**: unknown
- **Mentioned in bookmarks**: 41
- **Why you'd care**: If you buy the "zero-headcount company" thesis pushed throughout the corpus (b22, b40, b42, b46), this is the operational layer.
- **Setup effort**: heavy

### Cursor AI
- **What it does**: AI-native code editor.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 126 (as comparison to Firebase Studio)
- **Why you'd care**: Namechecked only; if you're deep in Claude Code you likely don't need it.
- **Setup effort**: trivial

### Descript
- **What it does**: Podcast/video editing by editing a transcript.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 87
- **Why you'd care**: Post-production for the AI voiceover Reels flow (b55).
- **Setup effort**: trivial

### Discord
- **What it does**: Chat platform; used as an interface for openclaw.
- **Category**: SaaS product
- **Cost tier**: free
- **Mentioned in bookmarks**: 94
- **Why you'd care**: Cheap control surface for personal AI agents.
- **Setup effort**: trivial

### ElevenLabs
- **What it does**: Voice synthesis and cloning.
- **Category**: SaaS product / API
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 87, 105
- **Why you'd care**: Default hosted voice for Reels scripts (b55) if you don't want to self-host Chatterbox.
- **Setup effort**: trivial

### Firebase Studio
- **What it does**: Google's browser-based app build/edit/deploy environment (b126).
- **Category**: hosted platform
- **Cost tier**: free
- **Mentioned in bookmarks**: 126
- **Why you'd care**: Alternative to Antigravity for shipping quick tools without local setup.
- **Setup effort**: trivial

### Gamma
- **What it does**: AI-generated slide decks and documents.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 87
- **Why you'd care**: Faster output than Claude for Word/PowerPoint for pitch-shaped assets.
- **Setup effort**: trivial

### Gemini (incl. Gemini 4.0)
- **What it does**: Google's LLM family; corpus uses it for consulting-grade answers, startup validation, video channel building.
- **Category**: SaaS product / API
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 52, 73, 90, 96, 99, 111, 114
- **Why you'd care**: Second opinion / longer-context model for your Claude workflows; several prompt-frameworks in the corpus are Gemini-specific.
- **Setup effort**: trivial

### Google Ads
- **What it does**: Google's paid-search platform.
- **Category**: hosted platform
- **Cost tier**: pay-per-click
- **Mentioned in bookmarks**: 63
- **Why you'd care**: b63 shows Claude Cowork wired into a Google Ads account for CPA/search-term analysis — directly relevant to local-service lead gen.
- **Setup effort**: medium

### Google Antigravity
- **What it does**: Google's agentic dev environment ("you can just build things").
- **Category**: hosted platform
- **Cost tier**: unknown
- **Mentioned in bookmarks**: 107
- **Why you'd care**: Top-5 pick — fastest 0-to-shipped for bookmark ideas.
- **Setup effort**: trivial

### Google Cloud
- **What it does**: Google's cloud platform.
- **Category**: hosted platform
- **Cost tier**: enterprise
- **Mentioned in bookmarks**: 9
- **Why you'd care**: Namechecked only (Google Cloud Next); no reason to adopt from this corpus alone.
- **Setup effort**: heavy

### Google Drive
- **What it does**: File storage; b113 wires it into Grok Business API console.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 113
- **Why you'd care**: If you go the Grok direction (b98–113), Drive is the file layer.
- **Setup effort**: trivial

### Google Maps
- **What it does**: Business directory used as a scraping source for local-lead workflows.
- **Category**: hosted platform
- **Cost tier**: free (frontend)
- **Mentioned in bookmarks**: 24, 49
- **Why you'd care**: Directly relevant to your local-service lead-gen theme — the roofer story (b24) and the niche-scraper (b49) both use it.
- **Setup effort**: trivial

### Google Stitch
- **What it does**: One-prompt generation of app screens, landing pages, UI flows (b72).
- **Category**: hosted platform
- **Cost tier**: unknown
- **Mentioned in bookmarks**: 72
- **Why you'd care**: Skip Figma for MVP mockups.
- **Setup effort**: trivial

### Grok / Grok Business
- **What it does**: xAI's LLM; corpus uses it for research automation, content scheduling, and Google Drive integration.
- **Category**: SaaS product / API
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 98, 101, 110, 113
- **Why you'd care**: Alternative to Claude for research-heavy tasks; several prompt frameworks (R-T-F, T-A-G, B-A-B, R-I-S-E) are Grok-focused.
- **Setup effort**: trivial

### Instagram
- **What it does**: Social platform; content target for many workflows in corpus.
- **Category**: hosted platform
- **Cost tier**: free
- **Mentioned in bookmarks**: 14, 20, 55, 67, 122
- **Why you'd care**: Distribution channel for the Claude carousel / Reels-voiceover workflows.
- **Setup effort**: trivial

### Matplotlib
- **What it does**: Python plotting library.
- **Category**: open-source library
- **Cost tier**: free
- **Mentioned in bookmarks**: 128
- **Why you'd care**: Only if you're running the stock-scraper prompt in b128.
- **Setup effort**: trivial

### Meta Ads MCP + Meta Ads CLI
- **What it does**: Anthropic-style MCP + CLI giving AI clients direct, authorized access to Meta Ads accounts (build, launch, optimize campaigns via natural language).
- **Category**: MCP server + CLI tool
- **Cost tier**: free (tool) + ad spend
- **Mentioned in bookmarks**: 38, 47, 68
- **Why you'd care**: Highest-frequency agent-marketing tool in the corpus and the single fastest win for anyone running paid social for local clients.
- **Setup effort**: medium

### Microsoft Excel / PowerPoint / Word / Outlook (Claude integrations)
- **What it does**: Claude connectors carrying conversation context across Microsoft apps (b36).
- **Category**: SaaS product
- **Cost tier**: enterprise
- **Mentioned in bookmarks**: 36
- **Why you'd care**: If your clients live in Microsoft 365, this is the least-friction Claude surface.
- **Setup effort**: medium

### NanoBanana 2
- **What it does**: Image gen model; used in b71 as the engine for a full brand-guide-to-ad-creative pipeline from a URL.
- **Category**: API (per b71's open-sourced tool)
- **Cost tier**: unknown
- **Mentioned in bookmarks**: 71
- **Why you'd care**: Direct match for the "ad generator from a product URL" pattern (b30, b71).
- **Setup effort**: medium

### openclaw / Clawdbot
- **What it does**: Open-source personal AI with full system access; interfaces via WhatsApp, Discord, Telegram; one-command AWS deploy.
- **Category**: open-source library
- **Cost tier**: free (self-hosted)
- **Mentioned in bookmarks**: 92, 93, 94
- **Why you'd care**: Top-5 pick — a genuinely deployable personal agent, unlike most vaporware in this corpus.
- **Setup effort**: medium

### OpenWA
- **What it does**: Self-hostable open-source alternative to the WhatsApp Business API — messages, groups, media, no per-message fees.
- **Category**: open-source library
- **Cost tier**: free (self-hosted)
- **Mentioned in bookmarks**: 25
- **Why you'd care**: Directly enables WhatsApp-based lead-gen agents for local businesses without WhatsApp BSP costs.
- **Setup effort**: heavy

### Obsidian
- **What it does**: Local markdown notes app; the "8,893 nodes, 4,729 links" second-brain vault in b5.
- **Category**: SaaS product (local-first)
- **Cost tier**: cheap ($10/mo per b5, though free tier exists)
- **Mentioned in bookmarks**: 5
- **Why you'd care**: Top-5 pick — the canonical second-brain substrate, and pairs cleanly with the Karpathy "point Claude Code at a folder" pattern (b10, b11).
- **Setup effort**: trivial

### Perplexity
- **What it does**: Search-native LLM.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 87
- **Why you'd care**: Sourced research when Claude's browsing is weak.
- **Setup effort**: trivial

### PicWish
- **What it does**: Background removal / image cleanup.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 87
- **Why you'd care**: Utility step in an ad-creative pipeline.
- **Setup effort**: trivial

### Pika MCP
- **What it does**: MCP server giving Claude a face/name/personality plus multimodal generation.
- **Category**: MCP server
- **Cost tier**: unknown (Pika is freemium)
- **Mentioned in bookmarks**: 45
- **Why you'd care**: Top-5 pick — turns Claude into a branded content generator.
- **Setup effort**: medium

### RecCloud
- **What it does**: Recording/transcription utility.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 87
- **Why you'd care**: Only if you don't already have a preferred transcription tool.
- **Setup effort**: trivial

### Runway
- **What it does**: AI video editing/generation.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 87
- **Why you'd care**: Video generation for the AI-shortform-channel workflow (b52).
- **Setup effort**: trivial

### Suno
- **What it does**: AI music generation.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 87
- **Why you'd care**: Background audio for the Reels/voiceover pipeline.
- **Setup effort**: trivial

### Telegram
- **What it does**: Chat platform; openclaw interface option.
- **Category**: SaaS product
- **Cost tier**: free
- **Mentioned in bookmarks**: 94
- **Why you'd care**: Bot API is easier than WhatsApp's for personal-agent control.
- **Setup effort**: trivial

### v0 (Vercel)
- **What it does**: AI UI generation.
- **Category**: SaaS product
- **Cost tier**: freemium
- **Mentioned in bookmarks**: 126 (comparison only)
- **Why you'd care**: Only mentioned as a benchmark against Firebase Studio.
- **Setup effort**: trivial

### WhatsApp
- **What it does**: Messaging platform; interface for OpenWA and openclaw.
- **Category**: SaaS product
- **Cost tier**: free
- **Mentioned in bookmarks**: 25, 94
- **Why you'd care**: Primary channel for local-service lead comms in most non-US markets.
- **Setup effort**: trivial

### Yahoo Finance
- **What it does**: Free market data source scraped in b128's prompt.
- **Category**: hosted platform
- **Cost tier**: free
- **Mentioned in bookmarks**: 128
- **Why you'd care**: Only if b128's stock-scraper prompt is on your list.
- **Setup effort**: trivial

### Yelp
- **What it does**: Business reviews platform; source for the HVAC speed-to-lead conversion data in b35.
- **Category**: hosted platform
- **Cost tier**: free (frontend), paid for advertisers
- **Mentioned in bookmarks**: 35
- **Why you'd care**: Lead source for the local-service AI-response agent pattern.
- **Setup effort**: trivial

---

## Skip list

- **Cofounder 2** — Impressive demo, but heavy commitment and no pricing/access signal in the corpus; wait until it's out of the "grandma-in-the-launch-video" phase.
- **Cartesia Sonic 3** — Only referenced as a benchmark Chatterbox beats; no reason to pay for it if you're going open-source.
- **v0 / Cursor AI** — Only namechecked as comparisons for Firebase Studio; you're already deep in Claude Code, don't context-switch.
- **RecCloud, PicWish, Gamma** — Generic utilities from the b87 listicle with no evidence you actually need them beyond "tool influencer put them on a list."
- **Google Cloud** — Namechecked once (Google Cloud Next keynote); the corpus gives you zero concrete reason to adopt it.
- **Matplotlib + Yahoo Finance** — Only relevant if you actually run the b128 stock-prediction prompt, which is a demo, not a strategy.
