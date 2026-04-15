from sqlalchemy import text
from sqlalchemy.orm import Session

from api.app.models.entities import EventLog


def log_event(db: Session, module: str, message: str, level: str = 'INFO', context: str | None = None):
    evt = EventLog(module=module, message=message, level=level, context=context)
    db.add(evt)
    db.commit()


def profit_summary(db: Session) -> dict:
    query = text(
        """
        SELECT
            COUNT(*) as total_deals,
            COALESCE(SUM(realized_profit), 0) as realized_profit,
            COALESCE(SUM(quoted_price - supplier_cost), 0) as expected_margin
        FROM deals
        """
    )
    row = db.execute(query).mappings().one()
    return dict(row)
