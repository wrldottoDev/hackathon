from collections import defaultdict

from sqlalchemy.orm import Session

from ..core.money import ZERO_MONEY, to_money
from ..models.observed_transaction import ObservedTransaction
from ..models.risk_alert import RiskAlert
from ..schemas.network import GraphEdge, GraphNode, GraphResponse


def _risk_rank(level: str) -> int:
    return {"low": 1, "medium": 2, "high": 3}.get(level, 0)


def _max_risk(levels: list[str]) -> str:
    if not levels:
        return "low"
    return max(levels, key=_risk_rank)


def get_network_graph(db: Session) -> GraphResponse:
    transactions = (
        db.query(ObservedTransaction)
        .filter(ObservedTransaction.status == "completed")
        .order_by(ObservedTransaction.created_at.asc(), ObservedTransaction.id.asc())
        .all()
    )
    alerts = db.query(RiskAlert).all()

    node_levels: dict[str, list[str]] = defaultdict(list)
    for alert in alerts:
        node_levels[alert.account_number].append(alert.level)

    node_counts: dict[str, int] = defaultdict(int)
    edge_map: dict[tuple[str, str], dict[str, object]] = {}

    for transaction in transactions:
        node_counts[transaction.source_account_number] += 1
        node_counts[transaction.destination_account_number] += 1
        key = (transaction.source_account_number, transaction.destination_account_number)
        if key not in edge_map:
            edge_map[key] = {"amount": ZERO_MONEY, "count": 0}
        edge_map[key]["amount"] += transaction.amount
        edge_map[key]["count"] += 1

    nodes = [
        GraphNode(
            id=account_number,
            label=account_number,
            bank_code=account_number.split("-", 1)[0],
            risk=_max_risk(node_levels.get(account_number, [])),
            transaction_count=count,
        )
        for account_number, count in sorted(node_counts.items())
    ]
    edges = [
        GraphEdge(
            source=source,
            target=destination,
            amount=to_money(values["amount"]),
            count=int(values["count"]),
        )
        for (source, destination), values in sorted(edge_map.items())
    ]
    return GraphResponse(nodes=nodes, edges=edges)
