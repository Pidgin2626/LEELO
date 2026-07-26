// LEELO Brain — Cloudflare Worker
//
// One tiny server that holds your Anthropic API key and speaks to:
//   - the dashboard  (POST /chat)
//   - Telegram       (POST /telegram)
//
// Set these secrets in Cloudflare (Worker → Settings → Variables):
//   ANTHROPIC_API_KEY          your sk-ant-... key
//   DASHBOARD_TOKEN            any random string; dashboard sends this to prove it's yours
//   TELEGRAM_BOT_TOKEN         the token @BotFather gives you (only needed for Telegram)
//   TELEGRAM_ALLOWED_USER_ID   your Telegram numeric user ID (only your account can chat with the bot)
//   TELEGRAM_WEBHOOK_SECRET    any random string; Telegram must send this back so we know a request is real
//
// The tool manifest below MUST stay in sync with apps/dashboard/index.html's TOOLS list.

const MODEL = "claude-sonnet-4-6";
const MAX_TOKENS = 1500;

const TOOL_MANIFEST = `
TOOL: claudemd
WHAT: CLI that generates a CLAUDE.md config for any project folder. Interview + repo scan.
WHEN: Starting a new project. Or you want Claude to auto-know your preferences in a folder.
COMMAND: cd C:\\path\\to\\your\\project; claudemd init
ALSO (audit existing): cd C:\\path\\to\\project; claudemd audit

TOOL: council (CLI)
WHAT: 5 Claude personalities debate a hard decision. 3 rounds. Verdict with dissent.
WHEN: A hard decision where you want multiple perspectives and a real verdict.
COMMAND: council ask "your question here" --solo
ALSO (see history): council log
ALSO (replay #1): council show 1 --full

TOOL: council (web)
WHAT: Same panel, in a browser. Click, paste key, type question, click Run.
WHEN: You prefer clicking over typing terminal commands.
LAUNCH: apps/llm-council/web/index.html (from the LEELO folder)

TOOL: bookmark pipeline — full
WHAT: Scrapes your X bookmarks, enriches links, and asks Claude to propose apps.
WHEN: Once every few weeks. Refresh your themes / app-idea backlog.
COMMAND: cd C:\\Users\\johnm\\LEELO\\bookmark_agent; .\\.venv\\Scripts\\Activate.ps1; python run.py

TOOL: bookmark pipeline — incremental
WHAT: Only enriches and summarizes bookmarks new since the last run. Cheap.
WHEN: Weekly. See what new saves changed the picture.
COMMAND: cd C:\\Users\\johnm\\LEELO\\bookmark_agent; .\\.venv\\Scripts\\Activate.ps1; python run.py --incremental

TOOL: analyzer — tools
WHAT: Extracts every product/API/MCP mentioned in your bookmarks. Ranked.
WHEN: After a fresh bookmark run, when you want a shopping list.
COMMAND: cd C:\\Users\\johnm\\LEELO\\bookmark_agent; .\\.venv\\Scripts\\Activate.ps1; python analyzer.py tools

TOOL: analyzer — contradictions
WHAT: Finds topics where your bookmarks disagree with each other. Picks a side.
WHEN: When you feel like your bookmarks are giving you conflicting advice.
COMMAND: cd C:\\Users\\johnm\\LEELO\\bookmark_agent; .\\.venv\\Scripts\\Activate.ps1; python analyzer.py contradictions
`.trim();

const CEO_SYSTEM = `You are LEELO Control — John's CEO agent. John is a beginner coder on Windows PowerShell running a personal AI toolkit he built.

Here is John's toolkit — every command below can be pasted into PowerShell:

${TOOL_MANIFEST}

REPORTS John already has generated (Markdown files on his disk, viewable on GitHub):
- bookmark_agent/data/summary.md — themes from his X bookmarks + 11 candidate app ideas
- bookmark_agent/data/tools.md — top 5 tools to try + full alphabetical list + skip list
- bookmark_agent/data/contradictions.md — 2 genuine disagreements in what he follows + picked winners

YOUR JOB when John talks to you:
1. Figure out what he actually needs. Ask ONE clarifying question only if the answer changes what you recommend. Otherwise commit.
2. Pick the right tool from the list above (or the right report to read).
3. Reply in this shape:
   - One line: the tool or report to use, and why (very short).
   - A code block with the EXACT command John should paste, OR a link to open.
   - One line: what he'll see when it works.
4. If no tool fits, just answer his question directly — briefly.
5. If he wants a NEW tool built, name that clearly ("that would be a new build") and suggest he tell you to start it in a fresh message.

Tone: terse, direct, warm. John is overwhelmed by his own toolkit. Don't lecture. Never repeat back what he just said. Never say "great question." Give him the one action.`;

// ---------------------------------------------------------------------------

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") return corsPreflight();

    if (url.pathname === "/" && request.method === "GET") {
      return new Response("LEELO brain is up.\n", {
        headers: { "content-type": "text/plain" },
      });
    }

    if (url.pathname === "/chat" && request.method === "POST") {
      return handleChat(request, env);
    }

    if (url.pathname === "/telegram" && request.method === "POST") {
      return handleTelegram(request, env);
    }

    return new Response("Not found", { status: 404 });
  },
};

async function handleChat(request, env) {
  const auth = request.headers.get("Authorization") || "";
  const token = auth.replace(/^Bearer\s+/i, "").trim();
  if (!env.DASHBOARD_TOKEN || token !== env.DASHBOARD_TOKEN) {
    return corsJson({ error: "Unauthorized" }, 401);
  }
  if (!env.ANTHROPIC_API_KEY) {
    return corsJson({ error: "Worker is missing ANTHROPIC_API_KEY secret" }, 500);
  }

  let body;
  try { body = await request.json(); }
  catch { return corsJson({ error: "Bad JSON" }, 400); }

  if (!body || !Array.isArray(body.messages)) {
    return corsJson({ error: "Expected { messages: [...] }" }, 400);
  }

  const claude = await callAnthropic(env.ANTHROPIC_API_KEY, {
    model: body.model || MODEL,
    max_tokens: body.max_tokens || MAX_TOKENS,
    system: body.system || CEO_SYSTEM,
    messages: body.messages,
  });

  return corsJson(claude);
}

async function handleTelegram(request, env) {
  if (env.TELEGRAM_WEBHOOK_SECRET) {
    const got = request.headers.get("X-Telegram-Bot-Api-Secret-Token");
    if (got !== env.TELEGRAM_WEBHOOK_SECRET) {
      return new Response("Unauthorized", { status: 401 });
    }
  }

  let update;
  try { update = await request.json(); }
  catch { return new Response("OK"); }

  const msg = update?.message;
  if (!msg) return new Response("OK");

  const fromId = String(msg.from?.id ?? "");
  const chatId = msg.chat?.id;
  const text = (msg.text || "").trim();

  if (env.TELEGRAM_ALLOWED_USER_ID && fromId !== String(env.TELEGRAM_ALLOWED_USER_ID)) {
    return new Response("OK");
  }
  if (!text) return new Response("OK");

  if (text === "/start") {
    await sendTelegramMessage(env, chatId,
      "Hey — I'm your LEELO CEO. Tell me where you're stuck and I'll pick the right tool from your toolkit.");
    return new Response("OK");
  }

  let claudeReply;
  try {
    const resp = await callAnthropic(env.ANTHROPIC_API_KEY, {
      model: MODEL,
      max_tokens: MAX_TOKENS,
      system: CEO_SYSTEM,
      messages: [{ role: "user", content: text }],
    });
    claudeReply = extractText(resp) || "(Claude returned no text)";
  } catch (e) {
    claudeReply = "Error talking to Claude: " + (e?.message || e);
  }

  for (const chunk of chunkForTelegram(claudeReply, 3900)) {
    await sendTelegramMessage(env, chatId, chunk);
  }
  return new Response("OK");
}

async function callAnthropic(apiKey, payload) {
  const resp = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(payload),
  });
  const data = await resp.json();
  if (!resp.ok) return { ...data, _http_status: resp.status };
  return data;
}

function extractText(claudeResp) {
  if (!claudeResp || !Array.isArray(claudeResp.content)) return "";
  return claudeResp.content
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("")
    .trim();
}

async function sendTelegramMessage(env, chatId, text) {
  if (!env.TELEGRAM_BOT_TOKEN) return;
  await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text, disable_web_page_preview: true }),
  });
}

function chunkForTelegram(text, size) {
  if (text.length <= size) return [text];
  const out = [];
  let i = 0;
  while (i < text.length) { out.push(text.slice(i, i + size)); i += size; }
  return out;
}

// ---------------------------------------------------------------------------
// CORS helpers — dashboard is hosted on github.io, worker is on workers.dev
// ---------------------------------------------------------------------------

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "86400",
  };
}

function corsPreflight() {
  return new Response(null, { status: 204, headers: corsHeaders() });
}

function corsJson(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", ...corsHeaders() },
  });
}
