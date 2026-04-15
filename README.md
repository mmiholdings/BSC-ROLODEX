# MOORE MONEY SYSTEM

Personal AI-driven event-based arbitrage and middleman operating system.

## Repo Structure

```text
api/                # FastAPI backend + module engines
automation/         # n8n workflow definitions
scrapers/           # data ingestion entrypoints
ai/                 # AI wrappers
routing/            # playbooks + routing configs
tracking/           # tracking docs and assets
tests/              # pytest module checks
scripts/            # bootstrap/run scripts
docs/               # setup + architecture + MVP path
```

## Core Logic

`Signal -> Classify -> Score -> Reply -> Route -> Track -> Learn`

### Scoring Rule

`score = (freshness * urgency * profit * probability) / (effort * risk * complexity)`

## Stack
- **Automation:** n8n
- **Scraping/Data:** Playwright-ready scraper layer + RSSHub + Hacker News API
- **Backend:** FastAPI
- **Database:** PostgreSQL + pgvector
- **Queue/cache:** Redis (optional)
- **AI:** OpenAI or Ollama
- **Messaging:** Telegram Bot API + Gmail API integration hooks

## Quick Start

```bash
cp .env.example .env
docker compose up -d postgres redis n8n
pip install -r requirements.txt
uvicorn api.app.main:app --reload
./scripts/run_real_cycle.sh
# Open interface: http://localhost:8000
```

## Real Data Flow (no fake data)
1. Signal Engine pulls live public posts from RSSHub and Hacker News.
2. Filter Engine drops unpaid/high-complexity tasks.
3. Scoring Engine ranks opportunities.
4. Response Engine drafts a message.
5. Routing Engine sends qualified opportunities to Telegram + playbook.
6. Tracking Engine logs events and margin.
7. Learning Engine reports source close rates.

## Health Checks
`GET /health` verifies:
- signals are flowing
- replies are generated
- deals are active
- errors are visible

Fail mode: retry in n8n + alert Telegram.


## Interface
- Operator UI: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`
