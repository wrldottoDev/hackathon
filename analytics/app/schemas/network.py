from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    bank_code: str
    risk: str
    transaction_count: int = 0


class GraphEdge(BaseModel):
    source: str
    target: str
    amount: float
    count: int


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]

