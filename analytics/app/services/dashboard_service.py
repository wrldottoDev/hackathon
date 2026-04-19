from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal

from sqlalchemy.orm import Session

from ..core.money import to_money
from ..models.investigation import Investigation
from ..models.observed_account import ObservedAccount
from ..models.observed_transaction import ObservedTransaction
from ..models.risk_alert import RiskAlert
from ..schemas.dashboard import (
    CategoryBreakdown,
    DashboardResponse,
    GeographicHotspot,
    HourlyDistribution,
    RiskAccountSummary,
)


def get_dashboard(db: Session) -> DashboardResponse:
    total_accounts = db.query(ObservedAccount).count()
    total_transactions = db.query(ObservedTransaction).count()
    alerts = db.query(RiskAlert).all()
    active_investigations = (
        db.query(Investigation)
        .filter(Investigation.status.in_(["open", "in_progress", "escalated"]))
        .count()
    )

    by_level = Counter(a.level for a in alerts)

    cat_scores: dict[str, list[int]] = defaultdict(list)
    cat_patterns: dict[str, Counter] = defaultdict(Counter)
    for a in alerts:
        cat_scores[a.category].append(a.score)
        cat_patterns[a.category][a.pattern_type] += 1

    alerts_by_category = []
    for cat in sorted(cat_scores):
        scores = cat_scores[cat]
        top_pattern = cat_patterns[cat].most_common(1)[0][0] if cat_patterns[cat] else ""
        alerts_by_category.append(
            CategoryBreakdown(
                category=cat,
                count=len(scores),
                avg_score=round(sum(scores) / len(scores), 1),
                top_pattern=top_pattern,
            )
        )

    account_alerts: dict[str, list[RiskAlert]] = defaultdict(list)
    for a in alerts:
        account_alerts[a.account_number].append(a)

    top_risk_accounts = []
    for acct, acct_alerts in sorted(
        account_alerts.items(),
        key=lambda item: max(a.score for a in item[1]),
        reverse=True,
    )[:15]:
        max_score = max(a.score for a in acct_alerts)
        level = (
            "critical" if max_score > 80
            else "high" if max_score > 50
            else "medium" if max_score > 25
            else "low"
        )
        top_risk_accounts.append(
            RiskAccountSummary(
                account_number=acct,
                bank_code=acct_alerts[0].bank_code,
                max_score=max_score,
                level=level,
                alert_count=len(acct_alerts),
                pattern_types=sorted({a.pattern_type for a in acct_alerts}),
                categories=sorted({a.category for a in acct_alerts}),
            )
        )

    transactions = (
        db.query(ObservedTransaction)
        .filter(ObservedTransaction.status == "completed")
        .all()
    )

    loc_alerts: dict[str, list[RiskAlert]] = defaultdict(list)
    alert_locations: dict[int, str] = {}
    for tx in transactions:
        if tx.location:
            alert_locations[tx.id] = tx.location.strip()
    for a in alerts:
        loc = alert_locations.get(a.observed_transaction_id, "")
        if loc:
            loc_alerts[loc].append(a)

    geographic_hotspots = []
    for loc in sorted(loc_alerts, key=lambda l: len(loc_alerts[l]), reverse=True)[:20]:
        loc_a = loc_alerts[loc]
        scores = [a.score for a in loc_a]
        cats = Counter(a.category for a in loc_a)
        geographic_hotspots.append(
            GeographicHotspot(
                location=loc,
                alert_count=len(loc_a),
                avg_score=round(sum(scores) / len(scores), 1),
                dominant_category=cats.most_common(1)[0][0] if cats else "",
            )
        )

    hourly_tx: dict[int, list] = defaultdict(list)
    hourly_alert_ids = {a.observed_transaction_id for a in alerts}
    hourly_alert_count: dict[int, int] = defaultdict(int)
    for tx in transactions:
        h = tx.created_at.hour
        hourly_tx[h].append(to_money(tx.amount))
        if tx.id in hourly_alert_ids:
            hourly_alert_count[h] += 1

    hourly_distribution = []
    for h in range(24):
        amounts = hourly_tx.get(h, [])
        hourly_distribution.append(
            HourlyDistribution(
                hour=h,
                transaction_count=len(amounts),
                alert_count=hourly_alert_count.get(h, 0),
                total_amount=sum(amounts, Decimal("0.00")),
            )
        )

    pattern_distribution = dict(
        sorted(
            Counter(a.pattern_type for a in alerts).items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )

    return DashboardResponse(
        total_accounts=total_accounts,
        total_transactions=total_transactions,
        total_alerts=len(alerts),
        active_investigations=active_investigations,
        alerts_by_level=dict(sorted(by_level.items())),
        alerts_by_category=alerts_by_category,
        top_risk_accounts=top_risk_accounts,
        geographic_hotspots=geographic_hotspots,
        hourly_distribution=hourly_distribution,
        pattern_distribution=pattern_distribution,
    )
