from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from api.app.core.db import Base, engine, get_db
from api.app.core.logging import configure_logging
from api.app.models.entities import Opportunity, Signal
from api.app.modules import (
    filter_engine,
    health_check_engine,
    learning_engine,
    response_engine,
    routing_engine,
    scoring_engine,
    signal_engine,
    tracking_engine,
)
from api.app.schemas.opportunity import CycleResult

configure_logging()
app = FastAPI(title='MOORE MONEY SYSTEM', version='0.1.0')
Base.metadata.create_all(bind=engine)


@app.get('/health')
def health(db: Session = Depends(get_db)):
    return health_check_engine.run_health_checks(db)


@app.get('/profit')
def profit(db: Session = Depends(get_db)):
    return tracking_engine.profit_summary(db)


@app.get('/learn')
def learn(db: Session = Depends(get_db)):
    return learning_engine.source_conversion_metrics(db)


@app.post('/run-cycle', response_model=CycleResult)
def run_cycle(db: Session = Depends(get_db)):
    signals = signal_engine.ingest_real_signals()
    ingested = 0
    qualified = 0
    replies_sent = 0
    routed = 0

    for rs in signals:
        if db.query(Signal).filter(Signal.url == rs.url).first():
            continue

        signal_row = Signal(
            source=rs.source,
            title=rs.title[:500],
            body=rs.body,
            author=rs.author,
            url=rs.url,
            created_at_source=rs.created_at_source,
        )
        db.add(signal_row)
        db.commit()
        db.refresh(signal_row)
        ingested += 1

        if not filter_engine.qualifies(rs):
            continue

        features = scoring_engine.estimate_features(f'{rs.title}\n{rs.body}')
        features.freshness = scoring_engine.freshness_factor(rs.created_at_source)
        score = scoring_engine.compute_score(features)

        opp = Opportunity(
            signal_id=signal_row.id,
            task_type='micro-service',
            urgency=features.urgency,
            freshness=features.freshness,
            profit=features.profit,
            probability=features.probability,
            effort=features.effort,
            risk=features.risk,
            complexity=features.complexity,
            score=score,
            status='qualified',
        )
        db.add(opp)
        db.commit()
        db.refresh(opp)
        qualified += 1

        reply = response_engine.generate_reply(f'{rs.title}\n{rs.body}')
        tracking_engine.log_event(db, 'response_engine', 'reply_generated', context=reply[:1000])
        replies_sent += 1

        playbook_key, playbook = routing_engine.choose_playbook(f'{rs.title}\n{rs.body}')
        if playbook_key:
            routed_ok = routing_engine.route_to_telegram(
                f"[Route] Playbook={playbook_key} URL={rs.url}\nReply draft:\n{reply}"
            )
            if routed_ok:
                routed += 1
                tracking_engine.log_event(db, 'routing_engine', f'routed via {playbook_key}')

    return CycleResult(
        ingested_signals=ingested,
        qualified_opportunities=qualified,
        replies_sent=replies_sent,
        routed_deals=routed,
    )
