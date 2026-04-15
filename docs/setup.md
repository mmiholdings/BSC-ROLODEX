# Setup (MVP)

## 1) Prerequisites
- Docker + Docker Compose
- Python 3.11+
- Telegram bot token
- OpenAI API key or local Ollama

## 2) Environment
Copy `.env.example` to `.env` and fill real credentials.

## 3) Start infra
```bash
docker compose up -d postgres redis n8n
```

## 4) Install API
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.app.main:app --reload
```

## 5) Initialize pgvector
```bash
psql "$DATABASE_URL" -f scripts/bootstrap_db.sql
```

## 6) Import n8n workflow
- Open n8n UI at `http://localhost:5678`
- Import `automation/workflows/moore-money-core.json`
- Configure Telegram credential
- Activate workflow

## 7) Open interface
- Operator UI: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`

## 8) Run first live cycle
```bash
./scripts/run_real_cycle.sh
```

This fetches real demand from RSSHub/Hacker News, scores opportunities, and posts routed items to Telegram.
