"""Persistence. Two backends behind one interface:

  - InMemoryRepo : default when DATABASE_URL is unset -> the loop runs with NO docker/pg.
  - PgRepo       : psycopg v3, used when DATABASE_URL is set (docker compose).

Phase 1.A keeps the surface tiny: enough to drive the full approve loop end-to-end.
Both repos enforce brand_id scoping on the decision queue (the Phase1->Phase2 seam).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from app.core.models import Decision, Status, assert_transition
from app.core.settings import get_settings


# ── In-memory (default, $0, no docker) ────────────────────────────────────
class InMemoryRepo:
    def __init__(self):
        self._decisions: dict[str, Decision] = {}
        self._brand_id: str | None = None

    def ensure_brand(self, name: str = "Sin (own)") -> str:
        if self._brand_id is None:
            self._brand_id = str(uuid.uuid4())
        return self._brand_id

    def save_decision(self, d: Decision) -> Decision:
        self._decisions[d.decision_id] = d
        return d

    def get_decision(self, decision_id: str) -> Decision | None:
        return self._decisions.get(decision_id)

    def list_queue(self, brand_id: str, status: Status = Status.SUGGESTED) -> list[Decision]:
        return sorted(
            [d for d in self._decisions.values()
             if d.brand_id == brand_id and d.status == status],
            key=lambda d: d.score, reverse=True,
        )

    def transition(self, decision_id: str, target: Status, **fields) -> Decision:
        d = self._decisions[decision_id]
        assert_transition(d.status, target)        # enforce state machine
        d.status = target
        d.updated_at = datetime.utcnow()
        for k, v in fields.items():
            setattr(d, k, v)
        return d


# ── Postgres (when DATABASE_URL is set) ───────────────────────────────────
class PgRepo:
    def __init__(self, dsn: str):
        import psycopg  # imported lazily so mock loop needs no driver
        self._psycopg = psycopg
        self.dsn = dsn

    def _conn(self):
        return self._psycopg.connect(self.dsn, autocommit=True)

    def ensure_brand(self, name: str = "Sin (own)") -> str:
        with self._conn() as c, c.cursor() as cur:
            cur.execute("SELECT brand_id FROM brands WHERE type='own' LIMIT 1")
            row = cur.fetchone()
            if row:
                return str(row[0])
            cur.execute(
                "INSERT INTO brands (name, type) VALUES (%s, 'own') RETURNING brand_id",
                (name,),
            )
            return str(cur.fetchone()[0])

    def save_decision(self, d: Decision) -> Decision:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """INSERT INTO agent_decisions
                   (decision_id, brand_id, account_id, trigger_type, status,
                    recommendation, score, score_breakdown)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (d.decision_id, d.brand_id, d.account_id, d.trigger_type, d.status.value,
                 d.recommendation.model_dump_json(), d.score,
                 d.score_breakdown.model_dump_json()),
            )
        return d

    def get_decision(self, decision_id: str) -> Decision | None:
        import json
        from app.core.models import Combo, ScoreBreakdown
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT decision_id, brand_id, account_id, trigger_type, status,
                          recommendation, score, score_breakdown, reject_reason,
                          approved_by, asset_url, caption
                   FROM agent_decisions WHERE decision_id=%s""", (decision_id,))
            r = cur.fetchone()
        if not r:
            return None
        return Decision(
            decision_id=str(r[0]), brand_id=str(r[1]),
            account_id=str(r[2]) if r[2] else None, trigger_type=r[3],
            status=Status(r[4]), recommendation=Combo(**_asdict(r[5])),
            score=float(r[6] or 0), score_breakdown=ScoreBreakdown(**_asdict(r[7])),
            reject_reason=r[8], approved_by=r[9], asset_url=r[10], caption=r[11],
        )

    def list_queue(self, brand_id: str, status: Status = Status.SUGGESTED) -> list[Decision]:
        from app.core.models import Combo, ScoreBreakdown
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                """SELECT decision_id, brand_id, account_id, trigger_type, status,
                          recommendation, score, score_breakdown
                   FROM agent_decisions WHERE brand_id=%s AND status=%s
                   ORDER BY score DESC""", (brand_id, status.value))
            rows = cur.fetchall()
        return [
            Decision(decision_id=str(r[0]), brand_id=str(r[1]),
                     account_id=str(r[2]) if r[2] else None, trigger_type=r[3],
                     status=Status(r[4]), recommendation=Combo(**_asdict(r[5])),
                     score=float(r[6] or 0), score_breakdown=ScoreBreakdown(**_asdict(r[7])))
            for r in rows
        ]

    def transition(self, decision_id: str, target: Status, **fields) -> Decision:
        d = self.get_decision(decision_id)
        if d is None:
            raise KeyError(decision_id)
        assert_transition(d.status, target)        # enforce state machine
        cols, vals = ["status=%s", "updated_at=now()"], [target.value]
        for k, v in fields.items():
            cols.insert(-1, f"{k}=%s")
            vals.append(v)
        vals.append(decision_id)
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                f"UPDATE agent_decisions SET {', '.join(cols)} WHERE decision_id=%s", vals)
        return self.get_decision(decision_id)  # type: ignore[return-value]


def _asdict(v):
    import json
    return v if isinstance(v, dict) else json.loads(v)


# ── factory ───────────────────────────────────────────────────────────────
_repo = None


def get_repo():
    global _repo
    if _repo is None:
        dsn = get_settings().database_url
        _repo = PgRepo(dsn) if dsn else InMemoryRepo()
    return _repo
