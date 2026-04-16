from datetime import datetime

from pydantic import BaseModel


class FetchTransactionsResponse(BaseModel):
    banks_processed: int
    transactions_seen: int
    transactions_created: int
    transactions_updated: int
    alerts_generated: int
    fetched_at: datetime

