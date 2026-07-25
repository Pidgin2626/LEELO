# LEELO Brain — Cloudflare Worker

One tiny server (free on Cloudflare) that:
- Holds your Anthropic API key so no device needs to
- Answers dashboard chat requests
- Answers Telegram messages from your bot

## Endpoints

| Path | Who calls it | Auth |
|---|---|---|
| `GET /` | Anyone (health check) | none |
| `POST /chat` | The dashboard | `Authorization: Bearer <DASHBOARD_TOKEN>` |
| `POST /telegram` | Telegram's webhook | `X-Telegram-Bot-Api-Secret-Token: <TELEGRAM_WEBHOOK_SECRET>` |

## Secrets to set in Cloudflare

Under **Worker → Settings → Variables and secrets** (add each as a **Secret**, not a plain variable):

| Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your `sk-ant-...` key |
| `DASHBOARD_TOKEN` | any random string — the dashboard sends this to prove it's yours |
| `TELEGRAM_BOT_TOKEN` | the token @BotFather gives you |
| `TELEGRAM_ALLOWED_USER_ID` | your numeric Telegram user ID |
| `TELEGRAM_WEBHOOK_SECRET` | any random string — Telegram sends this back so the worker knows a message is real |

## Register the Telegram webhook

After the worker is deployed and Telegram vars are set, run once:

```
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://leelo-brain.<subdomain>.workers.dev/telegram&secret_token=<TELEGRAM_WEBHOOK_SECRET>"
```
