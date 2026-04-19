from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from ..models.follower import Follower
from ..models.landing_page import LandingPage
from ..models.message import DirectMessage
from ..models.post import Post
from ..models.report import Report
from ..models.user import User
from ..schemas.analysis import AnalysisResult, AnalysisSummary, RuleResult


URL_PATTERN = re.compile(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+")

SUSPICIOUS_KEYWORD_SETS: list[tuple[list[str], str]] = [
    (
        ["viaje", "pagado"],
        "Oferta de viaje con gastos cubiertos — táctica de captación.",
    ),
    (
        ["todo pagado"],
        "Promesa de gastos totalmente cubiertos.",
    ),
    (
        ["sin experiencia", "ingreso"],
        "Empleo sin requisitos con ingresos prometidos.",
    ),
    (
        ["sin experiencia", "paga"],
        "Empleo sin requisitos con alta paga.",
    ),
    (
        ["ingresos inmediatos"],
        "Promesa de dinero rápido.",
    ),
    (
        ["casting", "exclusivo"],
        "Casting exclusivo — señal de enganche de modelaje fraudulento.",
    ),
    (
        ["casting", "extranjero"],
        "Casting en el extranjero — riesgo de trata.",
    ),
    (
        ["envía fotos"],
        "Solicitud de fotos personales a desconocidos.",
    ),
    (
        ["envia fotos"],
        "Solicitud de fotos personales a desconocidos.",
    ),
    (
        ["modelo", "internacional"],
        "Oferta de modelaje internacional — gancho frecuente.",
    ),
    (
        ["oportunidad única", "extranjero"],
        "Oportunidad única en el extranjero.",
    ),
    (
        ["trabaja desde casa", "gana"],
        "Esquema de trabajo desde casa con ganancias prometidas.",
    ),
    (
        ["alta paga", "inmediata"],
        "Promesa de alta paga inmediata.",
    ),
    (
        ["contacta", "whatsapp"],
        "Redirección a canal privado fuera de la plataforma.",
    ),
    (
        ["escríbeme", "privado"],
        "Intento de mover la conversación a un canal privado.",
    ),
    (
        ["talento", "perfil"],
        "Halago genérico a perfil — táctica de reclutamiento masivo.",
    ),
]


@dataclass(slots=True)
class _UserProfile:
    user_id: int
    username: str
    is_recruiter: bool
    is_verified: bool
    posts_count: int
    followers_count: int
    following_count: int
    reports_received: int


@dataclass(slots=True)
class _MessageBurst:
    sender_id: int
    messages: list[DirectMessage] = field(default_factory=list)


def _score_to_level(score: int) -> str:
    if score <= 30:
        return "low"
    if score <= 60:
        return "medium"
    if score <= 80:
        return "high"
    return "critical"


class AnalizadorFinsta:
    def __init__(
        self,
        db: Session,
        *,
        blacklist_score: int = 40,
        keyword_score: int = 30,
        profile_anomaly_score: int = 15,
        spam_dm_score: int = 25,
        report_multiplier: float = 1.5,
        danger_threshold: int = 60,
        spam_similarity_threshold: float = 0.90,
        spam_unique_recipients_min: int = 5,
        spam_window: timedelta = timedelta(hours=1),
        follower_ratio_threshold: float = 10.0,
    ) -> None:
        self.db = db
        self.blacklist_score = blacklist_score
        self.keyword_score = keyword_score
        self.profile_anomaly_score = profile_anomaly_score
        self.spam_dm_score = spam_dm_score
        self.report_multiplier = report_multiplier
        self.danger_threshold = danger_threshold
        self.spam_similarity_threshold = spam_similarity_threshold
        self.spam_unique_recipients_min = spam_unique_recipients_min
        self.spam_window = spam_window
        self.follower_ratio_threshold = follower_ratio_threshold

        self._blacklisted_domains: set[str] | None = None
        self._user_profiles: dict[int, _UserProfile] | None = None
        self._follower_sets: dict[int, set[int]] | None = None

    def _load_blacklisted_domains(self) -> set[str]:
        if self._blacklisted_domains is None:
            pages = (
                self.db.query(LandingPage)
                .filter(LandingPage.is_malicious.is_(True))
                .all()
            )
            self._blacklisted_domains = {page.domain.lower() for page in pages}
        return self._blacklisted_domains

    def _load_user_profile(self, user_id: int) -> _UserProfile | None:
        if self._user_profiles is None:
            self._user_profiles = {}

        if user_id in self._user_profiles:
            return self._user_profiles[user_id]

        user = self.db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None

        followers_count = (
            self.db.query(Follower)
            .filter(Follower.following_id == user_id)
            .count()
        )
        following_count = (
            self.db.query(Follower)
            .filter(Follower.follower_id == user_id)
            .count()
        )
        posts_count = (
            self.db.query(Post)
            .filter(Post.author_id == user_id)
            .count()
        )
        reports_received = (
            self.db.query(Report)
            .filter(Report.reported_user_id == user_id)
            .count()
        )

        profile = _UserProfile(
            user_id=user_id,
            username=user.username,
            is_recruiter=user.is_recruiter,
            is_verified=user.is_verified,
            posts_count=posts_count,
            followers_count=followers_count,
            following_count=following_count,
            reports_received=reports_received,
        )
        self._user_profiles[user_id] = profile
        return profile

    def _load_follower_set(self, user_id: int) -> set[int]:
        if self._follower_sets is None:
            self._follower_sets = {}

        if user_id not in self._follower_sets:
            rows = (
                self.db.query(Follower.follower_id)
                .filter(Follower.following_id == user_id)
                .all()
            )
            self._follower_sets[user_id] = {row[0] for row in rows}

        return self._follower_sets[user_id]

    def _extract_domains(self, text: str) -> list[str]:
        urls = URL_PATTERN.findall(text)
        domains = []
        for url in urls:
            if not url.startswith("http"):
                url = "http://" + url
            try:
                parsed = urlparse(url)
                if parsed.hostname:
                    domains.append(parsed.hostname.lower())
            except Exception:
                continue
        return domains

    def rule_blacklist(self, text: str) -> RuleResult | None:
        blacklisted = self._load_blacklisted_domains()
        domains = self._extract_domains(text)
        matched = [d for d in domains if d in blacklisted]
        if not matched:
            return None
        return RuleResult(
            rule_name="enlace_sospechoso",
            score=self.blacklist_score,
            detail=f"Enlace a dominio de alto riesgo: {', '.join(matched)}",
        )

    def rule_keywords(self, text: str) -> RuleResult | None:
        lower_text = text.lower()
        triggered: list[str] = []
        for keywords, description in SUSPICIOUS_KEYWORD_SETS:
            if all(kw in lower_text for kw in keywords):
                triggered.append(description)
        if not triggered:
            return None
        return RuleResult(
            rule_name="analisis_semantico",
            score=self.keyword_score,
            detail="; ".join(triggered),
        )

    def rule_profile_anomaly(self, user_id: int) -> RuleResult | None:
        profile = self._load_user_profile(user_id)
        if profile is None:
            return None

        if profile.followers_count > 0:
            ratio = profile.following_count / profile.followers_count
        elif profile.following_count > 0:
            ratio = float(profile.following_count)
        else:
            return None

        if ratio < self.follower_ratio_threshold:
            return None

        return RuleResult(
            rule_name="anomalia_perfil",
            score=self.profile_anomaly_score,
            detail=(
                f"Proporción seguidos/seguidores anómala: "
                f"{profile.following_count}/{max(profile.followers_count, 1)} "
                f"= {ratio:.1f}:1 (umbral: {self.follower_ratio_threshold}:1). "
                f"Solo {profile.posts_count} publicaciones."
            ),
        )

    def rule_spam_dms(self, user_id: int) -> RuleResult | None:
        messages = (
            self.db.query(DirectMessage)
            .filter(DirectMessage.sender_id == user_id)
            .order_by(DirectMessage.created_at.asc())
            .all()
        )
        if len(messages) < self.spam_unique_recipients_min:
            return None

        followers_of_sender = self._load_follower_set(user_id)

        for i, pivot in enumerate(messages):
            window_end = pivot.created_at + self.spam_window
            window_msgs = [
                m for m in messages[i:]
                if m.created_at <= window_end
                and m.recipient_id not in followers_of_sender
            ]

            if len(window_msgs) < self.spam_unique_recipients_min:
                continue

            unique_recipients: set[int] = set()
            similar_count = 0
            for msg in window_msgs:
                unique_recipients.add(msg.recipient_id)
                similarity = SequenceMatcher(None, pivot.body, msg.body).ratio()
                if similarity >= self.spam_similarity_threshold:
                    similar_count += 1

            if (
                len(unique_recipients) >= self.spam_unique_recipients_min
                and similar_count >= self.spam_unique_recipients_min
            ):
                return RuleResult(
                    rule_name="spam_mensajes_directos",
                    score=self.spam_dm_score,
                    detail=(
                        f"Envío masivo: {similar_count} mensajes similares (>90%) a "
                        f"{len(unique_recipients)} usuarios distintos que no lo siguen, "
                        f"en menos de 1 hora."
                    ),
                )
        return None

    def rule_community_reports(self, user_id: int) -> float:
        profile = self._load_user_profile(user_id)
        if profile is None or profile.reports_received == 0:
            return 1.0
        return 1.0 + (profile.reports_received * (self.report_multiplier - 1.0))

    def analyze_post(self, post: Post) -> AnalysisResult:
        rules: list[RuleResult] = []

        blacklist = self.rule_blacklist(post.caption)
        if blacklist:
            rules.append(blacklist)

        keywords = self.rule_keywords(post.caption)
        if keywords:
            rules.append(keywords)

        profile = self.rule_profile_anomaly(post.author_id)
        if profile:
            rules.append(profile)

        spam = self.rule_spam_dms(post.author_id)
        if spam:
            rules.append(spam)

        base_score = sum(r.score for r in rules)
        report_multiplier = self.rule_community_reports(post.author_id)
        total_score = min(100, int(base_score * report_multiplier))

        user_profile = self._load_user_profile(post.author_id)
        username = user_profile.username if user_profile else "unknown"

        return AnalysisResult(
            target_type="post",
            target_id=post.id,
            user_id=post.author_id,
            username=username,
            total_score=total_score,
            is_dangerous=total_score >= self.danger_threshold,
            risk_level=_score_to_level(total_score),
            rules_triggered=rules,
            analyzed_at=datetime.now(timezone.utc),
        )

    def analyze_message(self, message: DirectMessage) -> AnalysisResult:
        rules: list[RuleResult] = []

        blacklist = self.rule_blacklist(message.body)
        if blacklist:
            rules.append(blacklist)

        keywords = self.rule_keywords(message.body)
        if keywords:
            rules.append(keywords)

        profile = self.rule_profile_anomaly(message.sender_id)
        if profile:
            rules.append(profile)

        spam = self.rule_spam_dms(message.sender_id)
        if spam:
            rules.append(spam)

        base_score = sum(r.score for r in rules)
        report_multiplier = self.rule_community_reports(message.sender_id)
        total_score = min(100, int(base_score * report_multiplier))

        user_profile = self._load_user_profile(message.sender_id)
        username = user_profile.username if user_profile else "unknown"

        return AnalysisResult(
            target_type="message",
            target_id=message.id,
            user_id=message.sender_id,
            username=username,
            total_score=total_score,
            is_dangerous=total_score >= self.danger_threshold,
            risk_level=_score_to_level(total_score),
            rules_triggered=rules,
            analyzed_at=datetime.now(timezone.utc),
        )

    def analyze_all(self) -> AnalysisSummary:
        posts = self.db.query(Post).all()
        messages = self.db.query(DirectMessage).all()

        post_results = [self.analyze_post(p) for p in posts]
        message_results = [self.analyze_message(m) for m in messages]

        dangerous_posts = [r for r in post_results if r.is_dangerous]
        dangerous_messages = [r for r in message_results if r.is_dangerous]

        dangerous_users = sorted(
            {r.username for r in [*dangerous_posts, *dangerous_messages]}
        )

        all_dangerous = sorted(
            [*dangerous_posts, *dangerous_messages],
            key=lambda r: r.total_score,
            reverse=True,
        )

        return AnalysisSummary(
            total_analyzed_posts=len(posts),
            total_analyzed_messages=len(messages),
            total_dangerous_posts=len(dangerous_posts),
            total_dangerous_messages=len(dangerous_messages),
            dangerous_users=dangerous_users,
            top_alerts=all_dangerous[:20],
        )
