from sqlalchemy import text
from sqlalchemy.orm import Session


def source_conversion_metrics(db: Session) -> list[dict]:
    query = text(
        """
        SELECT s.source,
               COUNT(DISTINCT s.id) AS signals,
               COUNT(DISTINCT o.id) AS opportunities,
               COUNT(DISTINCT d.id) AS deals,
               CASE WHEN COUNT(DISTINCT o.id) = 0 THEN 0
                    ELSE COUNT(DISTINCT d.id)::float / COUNT(DISTINCT o.id) END AS close_rate
        FROM signals s
        LEFT JOIN opportunities o ON o.signal_id = s.id
        LEFT JOIN deals d ON d.opportunity_id = o.id
        GROUP BY s.source
        ORDER BY close_rate DESC
        """
    )
    return [dict(r) for r in db.execute(query).mappings().all()]
