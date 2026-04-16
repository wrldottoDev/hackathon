import random
from collections import Counter
from datetime import datetime
from typing import Iterable

from sqlalchemy.orm import Session, joinedload

from . import models, schemas
from .risk_engine import evaluate_transaction_risk


def generate_account_number() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(12))


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        return None

    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


def create_account(db: Session, user: models.User, initial_balance: float = 0.0):
    account_number = generate_account_number()
    while db.query(models.Account).filter(models.Account.account_number == account_number).first():
        account_number = generate_account_number()

    db_account = models.Account(
        account_number=account_number,
        balance=round(initial_balance, 2),
        user_id=user.id,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def get_accounts(db: Session):
    return db.query(models.Account).order_by(models.Account.created_at.desc()).all()


def get_account_by_id(db: Session, account_id: int):
    return (
        db.query(models.Account)
        .options(joinedload(models.Account.user))
        .filter(models.Account.id == account_id)
        .first()
    )


def get_accounts_by_user(db: Session, user_id: int):
    return (
        db.query(models.Account)
        .filter(models.Account.user_id == user_id)
        .order_by(models.Account.created_at.desc())
        .all()
    )


def create_transaction(db: Session, tx: schemas.TransactionCreate, actor: models.User):
    source = get_account_by_id(db, tx.source_account_id)
    destination = get_account_by_id(db, tx.destination_account_id)

    if not source or not destination:
        raise LookupError("La cuenta origen o destino no existe")

    if source.user_id != actor.id:
        raise PermissionError("Solo puedes transferir desde tus propias cuentas")

    if source.id == destination.id:
        raise ValueError("No se puede transferir a la misma cuenta")

    if tx.amount <= 0:
        raise ValueError("El monto debe ser mayor a cero")

    if source.balance < tx.amount:
        raise ValueError("Fondos insuficientes")

    source.balance = round(source.balance - tx.amount, 2)
    destination.balance = round(destination.balance + tx.amount, 2)

    db_tx = models.Transaction(
        source_account_id=source.id,
        destination_account_id=destination.id,
        amount=round(tx.amount, 2),
        transaction_type="transfer",
        status="completed",
        channel=tx.channel,
        location=tx.location,
    )
    db.add(db_tx)
    db.flush()
    evaluate_transaction_risk(db, db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx


def get_transactions(db: Session):
    return db.query(models.Transaction).order_by(models.Transaction.created_at.desc()).all()


def get_transaction_by_id(db: Session, transaction_id: int):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id)
        .first()
    )


def get_transactions_by_user(db: Session, user_id: int):
    account_ids = [account.id for account in get_accounts_by_user(db, user_id)]
    if not account_ids:
        return []

    return (
        db.query(models.Transaction)
        .filter(
            (models.Transaction.source_account_id.in_(account_ids))
            | (models.Transaction.destination_account_id.in_(account_ids))
        )
        .order_by(models.Transaction.created_at.desc())
        .all()
    )


def _serialize_alert(alert: models.RiskAlert) -> schemas.RiskAlertResponse:
    transaction_amount = alert.transaction.amount if alert.transaction else None
    account_number = None
    if alert.account:
        account_number = alert.account.account_number
    elif alert.transaction and alert.transaction.source_account:
        account_number = alert.transaction.source_account.account_number

    return schemas.RiskAlertResponse(
        id=alert.id,
        transaction_id=alert.transaction_id,
        account_id=alert.account_id,
        score=alert.score,
        level=alert.level,
        reason=alert.reason,
        created_at=alert.created_at,
        transaction_amount=transaction_amount,
        account_number=account_number,
    )


def list_risk_alerts(db: Session, limit: int = 50):
    alerts = (
        db.query(models.RiskAlert)
        .options(
            joinedload(models.RiskAlert.transaction).joinedload(models.Transaction.source_account),
            joinedload(models.RiskAlert.account),
        )
        .order_by(models.RiskAlert.created_at.desc())
        .limit(limit)
        .all()
    )
    return [_serialize_alert(alert) for alert in alerts]


def get_risk_summary(db: Session):
    alerts = db.query(models.RiskAlert).order_by(models.RiskAlert.created_at.desc()).all()
    counts = Counter(alert.level for alert in alerts)
    latest_alerts = list_risk_alerts(db, limit=10)
    return schemas.RiskSummaryResponse(
        total_alerts=len(alerts),
        low=counts.get("low", 0),
        medium=counts.get("medium", 0),
        high=counts.get("high", 0),
        latest_alerts=latest_alerts,
    )


def _max_risk_level(levels: Iterable[str]) -> str:
    rank = {"low": 1, "medium": 2, "high": 3}
    current = "low"
    for level in levels:
        if rank.get(level, 0) > rank[current]:
            current = level
    return current


VALID_NETWORK_RISK_LEVELS = {"all", "low", "medium", "high"}


def _validate_network_risk_level(risk_level: str) -> str:
    if risk_level not in VALID_NETWORK_RISK_LEVELS:
        raise ValueError("Filtro de riesgo inválido")
    return risk_level


def _transaction_risk_level(tx_levels: dict[int, list[str]], transaction_id: int) -> str:
    return _max_risk_level(tx_levels.get(transaction_id, []))


def _load_network_alert_maps(db: Session):
    alerts = db.query(models.RiskAlert).options(joinedload(models.RiskAlert.transaction)).all()
    tx_levels: dict[int, list[str]] = {}
    account_alert_levels: dict[int, list[str]] = {}

    for alert in alerts:
        if alert.account_id:
            account_alert_levels.setdefault(alert.account_id, []).append(alert.level)
        if alert.transaction_id:
            tx_levels.setdefault(alert.transaction_id, []).append(alert.level)

    return tx_levels, account_alert_levels


def _network_transactions_query(db: Session):
    return (
        db.query(models.Transaction)
        .options(
            joinedload(models.Transaction.source_account).joinedload(models.Account.user),
            joinedload(models.Transaction.destination_account).joinedload(models.Account.user),
        )
        .order_by(models.Transaction.created_at.desc())
    )


def get_network_graph(db: Session, risk_level: str = "all", user_id: int | None = None):
    risk_level = _validate_network_risk_level(risk_level)
    accounts = db.query(models.Account).options(joinedload(models.Account.user)).all()
    accounts_by_id = {account.id: account for account in accounts}

    focus_user = None
    focus_account_ids: set[int] = set()
    if user_id is not None:
        focus_user = get_user_by_id(db, user_id)
        if not focus_user:
            raise LookupError("Cliente no encontrado")
        focus_accounts = get_accounts_by_user(db, user_id)
        focus_account_ids = {account.id for account in focus_accounts}

    transactions_query = _network_transactions_query(db)
    if focus_account_ids:
        transactions_query = transactions_query.filter(
            (models.Transaction.source_account_id.in_(focus_account_ids))
            | (models.Transaction.destination_account_id.in_(focus_account_ids))
        )
    transactions = transactions_query.limit(250).all()
    tx_levels, account_alert_levels = _load_network_alert_maps(db)

    filtered_transactions = []
    for transaction in transactions:
        tx_risk = _transaction_risk_level(tx_levels, transaction.id)
        if risk_level != "all" and tx_risk != risk_level:
            continue
        filtered_transactions.append(transaction)

    visible_account_ids = set()
    node_levels: dict[int, list[str]] = {}
    for account_id, levels in account_alert_levels.items():
        for level in levels:
            if risk_level == "all" or level == risk_level:
                node_levels.setdefault(account_id, []).append(level)

    for transaction in filtered_transactions:
        tx_risk = _transaction_risk_level(tx_levels, transaction.id)
        visible_account_ids.add(transaction.source_account_id)
        visible_account_ids.add(transaction.destination_account_id)
        node_levels.setdefault(transaction.source_account_id, []).append(tx_risk)
        node_levels.setdefault(transaction.destination_account_id, []).append(tx_risk)

    if focus_account_ids:
        visible_account_ids.update(focus_account_ids)

    visible_accounts = [
        accounts_by_id[account_id]
        for account_id in sorted(visible_account_ids)
        if account_id in accounts_by_id
    ]

    nodes = []
    for account in visible_accounts:
        transaction_count = sum(
            1
            for transaction in filtered_transactions
            if transaction.source_account_id == account.id or transaction.destination_account_id == account.id
        )
        nodes.append(
            schemas.GraphNode(
                id=str(account.id),
                label=f"{account.user.full_name} · {account.account_number[-4:]}",
                risk=_max_risk_level(node_levels.get(account.id, [])),
                balance=round(account.balance, 2),
                user_id=account.user_id,
                owner_name=account.user.full_name,
                account_number=account.account_number,
                is_focus=bool(focus_user and account.user_id == focus_user.id),
                transaction_count=transaction_count,
            )
        )

    edges = [
        schemas.GraphEdge(
            id=f"tx-{transaction.id}",
            transaction_id=transaction.id,
            source=str(transaction.source_account_id),
            target=str(transaction.destination_account_id),
            amount=round(transaction.amount, 2),
            risk=_transaction_risk_level(tx_levels, transaction.id),
            channel=transaction.channel,
            location=transaction.location,
            created_at=transaction.created_at,
        )
        for transaction in filtered_transactions
    ]

    return schemas.GraphResponse(nodes=nodes, edges=edges)


def get_network_report(db: Session, user_id: int, risk_level: str = "all"):
    risk_level = _validate_network_risk_level(risk_level)
    user = get_user_by_id(db, user_id)
    if not user:
        raise LookupError("Cliente no encontrado")

    accounts = get_accounts_by_user(db, user_id)
    account_ids = {account.id for account in accounts}
    tx_levels, _ = _load_network_alert_maps(db)
    transactions = (
        _network_transactions_query(db)
        .filter(
            (models.Transaction.source_account_id.in_(account_ids))
            | (models.Transaction.destination_account_id.in_(account_ids))
        )
        .all()
    )

    filtered_transactions = []
    for transaction in transactions:
        tx_risk = _transaction_risk_level(tx_levels, transaction.id)
        if risk_level != "all" and tx_risk != risk_level:
            continue
        filtered_transactions.append((transaction, tx_risk))

    risk_counts = Counter(tx_risk for _, tx_risk in filtered_transactions)
    total_sent = round(
        sum(transaction.amount for transaction, _ in filtered_transactions if transaction.source_account_id in account_ids),
        2,
    )
    total_received = round(
        sum(
            transaction.amount
            for transaction, _ in filtered_transactions
            if transaction.destination_account_id in account_ids
        ),
        2,
    )
    flagged_transactions = sum(1 for _, tx_risk in filtered_transactions if tx_risk != "low")

    counterparties: dict[int, dict] = {}
    for transaction, _ in filtered_transactions:
        if transaction.source_account_id in account_ids:
            counterparty_account = transaction.destination_account
        else:
            counterparty_account = transaction.source_account

        if not counterparty_account or not counterparty_account.user:
            continue

        user_entry = counterparties.setdefault(
            counterparty_account.user.id,
            {
                "user": counterparty_account.user,
                "transaction_count": 0,
                "total_amount": 0.0,
            },
        )
        user_entry["transaction_count"] += 1
        user_entry["total_amount"] += transaction.amount

    top_counterparties = [
        schemas.NetworkReportCounterparty(
            user_id=entry["user"].id,
            full_name=entry["user"].full_name,
            email=entry["user"].email,
            transaction_count=entry["transaction_count"],
            total_amount=round(entry["total_amount"], 2),
        )
        for entry in sorted(
            counterparties.values(),
            key=lambda item: (-item["total_amount"], -item["transaction_count"], item["user"].full_name),
        )[:8]
    ]

    recent_transactions = [
        schemas.NetworkReportTransaction(
            transaction_id=transaction.id,
            source_account_id=transaction.source_account_id,
            destination_account_id=transaction.destination_account_id,
            source_label=(
                f"{transaction.source_account.user.full_name} · {transaction.source_account.account_number}"
                if transaction.source_account and transaction.source_account.user
                else str(transaction.source_account_id)
            ),
            destination_label=(
                f"{transaction.destination_account.user.full_name} · {transaction.destination_account.account_number}"
                if transaction.destination_account and transaction.destination_account.user
                else str(transaction.destination_account_id)
            ),
            amount=round(transaction.amount, 2),
            risk=tx_risk,
            channel=transaction.channel,
            location=transaction.location,
            created_at=transaction.created_at,
        )
        for transaction, tx_risk in filtered_transactions[:25]
    ]

    return schemas.NetworkReportResponse(
        generated_at=datetime.utcnow(),
        risk_filter=risk_level,
        user=schemas.UserResponse.model_validate(user),
        accounts=[schemas.AccountResponse.model_validate(account) for account in accounts],
        total_transactions=len(filtered_transactions),
        total_sent=total_sent,
        total_received=total_received,
        distinct_counterparties=len(counterparties),
        flagged_transactions=flagged_transactions,
        low=risk_counts.get("low", 0),
        medium=risk_counts.get("medium", 0),
        high=risk_counts.get("high", 0),
        top_counterparties=top_counterparties,
        recent_transactions=recent_transactions,
    )
