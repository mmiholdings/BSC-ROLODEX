from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session


def run_health_checks(db: Session) -> dict:
    now = datetime.now(timezone.utc)
    recent_cutoff = now - timedelta(minutes=30)

    signals_recent = db.execute(
        text('SELECT COUNT(*) FROM signals WHERE created_at >= :cutoff'), {'cutoff': recent_cutoff}
    ).scalar_one()
    replies_recent = db.execute(
        text("SELECT COUNT(*) FROM event_logs WHERE module='response_engine' AND created_at >= :cutoff"),
        {'cutoff': recent_cutoff},
    ).scalar_one()
    active_deals = db.execute(text("SELECT COUNT(*) FROM deals WHERE status IN ('open','in_progress')")).scalar_one()
    recent_errors = db.execute(
        text("SELECT COUNT(*) FROM event_logs WHERE level='ERROR' AND created_at >= :cutoff"),
        {'cutoff': recent_cutoff},
    ).scalar_one()

    return {
        'signals_flowing': signals_recent > 0,
        'replies_sending': replies_recent > 0,
        'active_deals': active_deals,
        'recent_errors': recent_errors,
        'status': 'ok' if recent_errors == 0 else 'degraded',
    }
