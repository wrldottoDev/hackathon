from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.message import DirectMessage
from ..models.post import Post
from ..schemas.analysis import AnalysisResult, AnalysisSummary, FinstaAlertForAnalytics
from ..services.analyzer import AnalizadorFinsta
from ..services.analytics_bridge import build_alert_for_analytics, send_alerts_to_analytics

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/post/{post_id}", response_model=AnalysisResult)
def analyze_single_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    analyzer = AnalizadorFinsta(db)
    return analyzer.analyze_post(post)


@router.get("/message/{message_id}", response_model=AnalysisResult)
def analyze_single_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(DirectMessage).filter(DirectMessage.id == message_id).first()
    if not message:
        raise HTTPException(404, "Message not found")
    analyzer = AnalizadorFinsta(db)
    return analyzer.analyze_message(message)


@router.get("/scan", response_model=AnalysisSummary)
def full_scan(db: Session = Depends(get_db)):
    analyzer = AnalizadorFinsta(db)
    return analyzer.analyze_all()


@router.post("/send-to-analytics")
async def send_to_analytics(db: Session = Depends(get_db)):
    analyzer = AnalizadorFinsta(db)
    summary = analyzer.analyze_all()

    alerts_to_send: list[FinstaAlertForAnalytics] = []
    for result in summary.top_alerts:
        alerts_to_send.append(build_alert_for_analytics(result))

    if not alerts_to_send:
        return {"status": "no_alerts", "count": 0}

    response = await send_alerts_to_analytics(alerts_to_send)
    return response
