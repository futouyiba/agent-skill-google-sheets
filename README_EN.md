# Agent Skill: Google Sheets (Service Account Edition)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Google Sheets API](https://img.shields.io/badge/Google%20Sheets-API-34A853?logo=googlesheets&logoColor=white)](https://developers.google.com/sheets/api)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-8A2BE2)](https://modelcontextprotocol.io)
[![Agent Skills](https://img.shields.io/badge/compatible%20with-Agent%20Skills%20standard-ff69b4)](https://www.anthropic.com/news/skills)
[![uv](https://img.shields.io/badge/depends%20on-uv-de5c21?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)

**English · [中文版](README.md)**

A portable Agent Skill package that lets any AI client supporting the [Agent Skills](https://www.anthropic.com/news/skills) standard (Claude Code, Claude Desktop, and compatible third-party agent clients) safely read and write your Google Sheets.

## 📑 Table of Contents

- [Why a "local server + share-to-email" pattern?](#why-a-local-server--share-to-email-pattern)
- [Contents](#contents)
- [Setup](#setup)
  - [Step 1: Google Cloud side](#step-1-google-cloud-side-10-minutes-all-in-the-browser)
  - [Step 2: Register the MCP server](#step-2-register-the-mcp-server-claude-code--compatible-clients)
  - [Step 3: Install the skill](#step-3-install-the-skill)
- [Security notes](#security-notes)
- [Appendix: the official remote MCP route](#appendix-the-better-route-if-you-have-a-workspace-account-official-remote-mcp)
- [License](#license)

## Why a "local server + share-to-email" pattern?

There are three usual routes to give an AI client access to Google Sheets — and the first two are closed to individual users:

| Route | Barrier | Verdict |
|---|---|---|
| ① Google's official remote MCP (`sheetsmcp.googleapis.com`) | Requires the backing GCP project to be enrolled in the **Google Workspace Developer Preview Program** — and that program's sign-up form **rejects personal Gmail addresses**; only Workspace (company/organization) accounts may join | Individuals are locked out |
| ② The claude.ai custom Connector | Requires a Claude Pro/Max/Team/Enterprise subscription; the OAuth callback runs through claude.ai's backend, so users on third-party API tokens / self-hosted relays can't use it | Non-subscribers are locked out |
| ③ This repo: **local MCP server + service account** | Just a free Google Cloud project | ✅ Works for everyone |

This package runs [mcp-google-sheets](https://github.com/xing5/mcp-google-sheets) as a local MCP server and talks to the **GA (generally available) Sheets API** through a **Google Cloud service account** (a programmatic identity, not a human account):

- **No subscription, no preview enrollment** — it rides the stable, generally-available API.
- **Clean permission boundary**: the service account can only see spreadsheets **explicitly shared with it**. None of your other files are visible to it. The only cost: share each spreadsheet with the service-account email once (same as sharing with a colleague).

> If you do have a Workspace (company) account, prefer the official remote MCP (①): it acts as your own Google identity with access to all your spreadsheets and no per-sheet sharing. See the appendix at the end.

## 📁 Contents

- `SKILL.md` — the skill itself (drop into your client's skills directory)
- `proxy-patch/sitecustomize.py` — optional proxy patch for restricted networks (where googleapis.com is not directly reachable)

## 🚀 Setup

### Step 1: Google Cloud side (~10 minutes, all in the browser)

1. Open [Google Cloud Console](https://console.cloud.google.com) and create a project (e.g. `sheets-mcp`).
2. Enable the **Google Sheets API** and **Google Drive API** (APIs & Services → Enable).
3. Create a service account: IAM & Admin → Service Accounts → Create (no roles needed).
4. Create a **JSON key** for the service account and download it to e.g. `~/.config/mcp-google-sheets/service-account.json`.
5. Note the `client_email` inside that JSON (looks like `xxx@yyy.iam.gserviceaccount.com`) — **every spreadsheet you want to use must be shared with this email** (Editor access).

### Step 2: Register the MCP server (Claude Code / compatible clients)

If your network reaches googleapis.com directly:

```bash
claude mcp add gsheets -s user \
  -e GOOGLE_APPLICATION_CREDENTIALS=~/.config/mcp-google-sheets/service-account.json \
  -- uvx --with 'mcp<2' mcp-google-sheets
```

On a restricted network (e.g. mainland China, local proxy at 127.0.0.1:7897): copy this repo's `proxy-patch/` to `~/.config/mcp-google-sheets/bootstrap/`, then:

```bash
claude mcp add gsheets -s user \
  -e GOOGLE_APPLICATION_CREDENTIALS=~/.config/mcp-google-sheets/service-account.json \
  -e PYTHONPATH=~/.config/mcp-google-sheets/bootstrap \
  -- uvx --with 'mcp<2' --with pysocks mcp-google-sheets
```

Notes:

- Keep `--with 'mcp<2'`: mcp-google-sheets is not yet compatible with mcp 2.x (FastMCP was renamed).
- `--with pysocks` + the `PYTHONPATH` patch: httplib2 ignores proxy environment variables; the patch forces a ProxyInfo at startup. Override the proxy address with `GSHEETS_PROXY_HOST` / `GSHEETS_PROXY_PORT` (defaults: 127.0.0.1:7897).
- Requires [uv](https://docs.astral.sh/uv/) (`uvx`). Dependencies download automatically on first start.

### Step 3: Install the skill

Copy the `SKILL.md` directory into your client's skills directory, e.g. for Claude Code:

```bash
mkdir -p ~/.claude/skills/gsheets   # or your project's .claude/skills/gsheets
cp SKILL.md ~/.claude/skills/gsheets/
```

Start a new session and it's live. Then just say "read my xx spreadsheet".

## 🔒 Security notes

- **`service-account.json` is a secret. Never commit it to a repo or share it.** This repository must not contain any key files.
- The service account only sees spreadsheets explicitly shared with it — a clean permission boundary. Choose Viewer vs. Editor per spreadsheet as needed.
- If a key leaks or expires: delete it in Google Cloud and generate a new one.

## 📎 Appendix: the better route if you have a Workspace account (official remote MCP)

1. Follow the official doc [Configure the Sheets MCP server](https://developers.google.com/workspace/sheets/api/guides/configure-mcp-server) to create an OAuth client (add redirect URI `http://localhost:7777/callback`) and enroll your project in the Workspace Developer Preview Program (requires a company email).
2. `claude mcp add -s user --transport http --client-id <your-client-id> --callback-port 7777 gsheets https://sheetsmcp.googleapis.com/mcp/v1`
3. `claude mcp login gsheets` (export proxy env vars first on restricted networks).

The official route acts as your own Google account with access to all your spreadsheets — no per-sheet sharing needed.

## License

MIT
