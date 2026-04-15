# MOORE MONEY SYSTEM Architecture

```mermaid
flowchart LR
  A[Signal Engine\nRSSHub + HN + Playwright] --> B[Filter Engine]
  B --> C[Scoring Engine]
  C -->|score >= threshold| D[Response Engine\nOpenAI/Ollama]
  D --> E[Routing Engine\nTelegram + Supplier Playbooks]
  E --> F[Tracking Engine\nPostgreSQL + Logs]
  F --> G[Learning Engine\nClose-rate optimization]
  G --> B
  H[Health Check Engine] --> A
  H --> D
  H --> E
  H --> F
```

## Module Boundaries
- `signal_engine.py`: only ingestion from real public sources.
- `filter_engine.py`: hard qualification rules (simple, paid, fast).
- `scoring_engine.py`: deterministic scoring formula.
- `response_engine.py`: AI messaging generation.
- `routing_engine.py`: playbook match + supplier routing.
- `tracking_engine.py`: event/deal/profit persistence.
- `learning_engine.py`: source-level conversion insights.
- `health_check_engine.py`: safety checks + fail alerts.
