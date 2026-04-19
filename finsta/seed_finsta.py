"""
Seeder para Finsta — genera datos sintéticos de demostración.

Crea usuarios legítimos, reclutadores (bots), landing pages,
publicaciones con links sospechosos, y mensajes directos masivos.

Uso:
    python -m finsta.seed_finsta
"""

import random
from datetime import datetime, timedelta, timezone

from finsta.app.database import Base, SessionLocal, engine
from finsta.app.models.follower import Follower
from finsta.app.models.landing_page import LandingPage
from finsta.app.models.message import DirectMessage
from finsta.app.models.post import Post
from finsta.app.models.report import Report
from finsta.app.models.user import User

random.seed(42)

# ---------------------------------------------------------------------------
# Landing Pages
# ---------------------------------------------------------------------------
LANDING_PAGES = [
    {
        "url": "https://elite-models-intl.example.com/apply",
        "domain": "elite-models-intl.example.com",
        "title": "Elite Models International — ¡Viaja con nosotros!",
        "description": (
            "Agencia de modelaje internacional que promete viajes pagos, "
            "hospedaje de lujo y sesiones fotográficas en Europa. "
            "Pide fotos personales y datos de pasaporte."
        ),
        "is_malicious": True,
        "category": "fake_modeling_agency",
        "days_since_creation": 12,
    },
    {
        "url": "https://trabajo-global-ya.example.com/registro",
        "domain": "trabajo-global-ya.example.com",
        "title": "Trabajo Global YA — Gana $5,000/mes sin experiencia",
        "description": (
            "Oferta de empleo en el extranjero 'sin experiencia necesaria' "
            "con 'alta paga inmediata'. Solicita depósito de seguridad "
            "y copia de documentos de identidad."
        ),
        "is_malicious": True,
        "category": "fake_job_offer",
        "days_since_creation": 5,
    },
    {
        "url": "https://empleos.gobierno.example.com/buscar",
        "domain": "empleos.gobierno.example.com",
        "title": "Portal Nacional de Empleo — Gobierno",
        "description": (
            "Portal oficial del gobierno para búsqueda de empleo verificado. "
            "Ofertas laborales revisadas y certificadas."
        ),
        "is_malicious": False,
        "category": "government_portal",
        "days_since_creation": 2190,
    },
]

# ---------------------------------------------------------------------------
# Usuarios legítimos
# ---------------------------------------------------------------------------
LEGITIMATE_USERS = [
    {"username": "maria_cr23", "display_name": "María López", "bio": "Estudiante de diseño gráfico 🎨 San José"},
    {"username": "carlos_foto", "display_name": "Carlos Herrera", "bio": "Fotógrafo | Naturaleza y paisajes"},
    {"username": "ana_fitness", "display_name": "Ana Mora", "bio": "Entrenadora personal 💪"},
    {"username": "luis_dev", "display_name": "Luis Quesada", "bio": "Software developer | Python & React"},
    {"username": "sofia_music", "display_name": "Sofía Arias", "bio": "Cantautora independiente 🎵"},
    {"username": "pedro_viajes", "display_name": "Pedro Jiménez", "bio": "Viajero | 15 países visitados"},
    {"username": "valentina_art", "display_name": "Valentina Rojas", "bio": "Ilustradora digital"},
    {"username": "diego_gamer", "display_name": "Diego Vargas", "bio": "Streamer | Valorant & LoL"},
    {"username": "camila_cook", "display_name": "Camila Solano", "bio": "Chef en formación 🍳"},
    {"username": "andres_surf", "display_name": "Andrés Gutiérrez", "bio": "Surf life 🏄 Jacó Beach"},
    {"username": "laura_read", "display_name": "Laura Fernández", "bio": "Bookstagram | +200 libros este año"},
    {"username": "gabriel_run", "display_name": "Gabriel Chaves", "bio": "Maratonista amateur 🏃"},
    {"username": "isabella_eco", "display_name": "Isabella Montero", "bio": "Activista ambiental 🌿"},
    {"username": "mateo_skate", "display_name": "Mateo Calderón", "bio": "Skateboarding & street art"},
    {"username": "daniela_yoga", "display_name": "Daniela Núñez", "bio": "Instructora de yoga certificada 🧘"},
    {"username": "santiago_dj", "display_name": "Santiago Mora", "bio": "DJ electrónica | Eventos privados"},
    {"username": "luciana_pet", "display_name": "Luciana Vindas", "bio": "Rescate animal 🐾"},
    {"username": "nicolas_code", "display_name": "Nicolás Brenes", "bio": "Full-stack dev | Open source"},
    {"username": "renata_dance", "display_name": "Renata Trejos", "bio": "Bailarina profesional 💃"},
    {"username": "emilia_photo", "display_name": "Emilia Castro", "bio": "Fotografía de retrato y moda"},
]

# ---------------------------------------------------------------------------
# Usuarios reclutadores (bots)
# ---------------------------------------------------------------------------
RECRUITER_USERS = [
    {
        "username": "talent_scout_intl",
        "display_name": "Talent Scout International",
        "bio": "🌟 Buscamos modelos para campañas internacionales. DM para info.",
        "profile_picture_url": "https://picsum.photos/id/64/300/300",
    },
    {
        "username": "jobs_global_now",
        "display_name": "Empleos Globales",
        "bio": "💼 Oportunidades de trabajo en el extranjero. Alta paga inmediata. Sin experiencia.",
        "profile_picture_url": "https://picsum.photos/id/75/300/300",
    },
    {
        "username": "luxury_agency_eu",
        "display_name": "Luxury Models Europe",
        "bio": "✈️ Viajes pagados a Europa para modelos. Casting exclusivo.",
        "profile_picture_url": "https://picsum.photos/id/91/300/300",
    },
]

# ---------------------------------------------------------------------------
# Publicaciones de reclutadores
# ---------------------------------------------------------------------------
RECRUITER_POSTS = [
    {
        "recruiter_index": 0,
        "image_url": "https://picsum.photos/id/1011/600/600",
        "caption": (
            "🌟 ¡CASTING EXCLUSIVO en Europa! 🌟\n\n"
            "Buscamos jóvenes con talento para una campaña internacional de moda.\n"
            "✈️ Viaje todo pagado + hospedaje de lujo.\n"
            "📸 Envía fotos de cuerpo completo.\n\n"
            "Aplica aquí 👉 https://elite-models-intl.example.com/apply\n\n"
            "#modelaje #casting #viajeGratis #oportunidad"
        ),
    },
    {
        "recruiter_index": 0,
        "image_url": "https://picsum.photos/id/1025/600/600",
        "caption": (
            "📸 ¿Sueñas con ser modelo internacional?\n\n"
            "No necesitas experiencia. Nosotros te entrenamos.\n"
            "Viaje todo pagado al extranjero.\n\n"
            "Más info: https://elite-models-intl.example.com/apply\n\n"
            "#modelo #sinExperiencia #oportunidadUnica"
        ),
    },
    {
        "recruiter_index": 1,
        "image_url": "https://picsum.photos/id/1027/600/600",
        "caption": (
            "💼 TRABAJA EN EL EXTRANJERO 💼\n\n"
            "Sin experiencia necesaria.\n"
            "Ingresos inmediatos desde $3,000/mes.\n"
            "Alta paga inmediata + alojamiento incluido.\n\n"
            "Regístrate: https://trabajo-global-ya.example.com/registro\n\n"
            "#trabajo #empleo #sinExperiencia #ingresosInmediatos"
        ),
    },
    {
        "recruiter_index": 1,
        "image_url": "https://picsum.photos/id/1035/600/600",
        "caption": (
            "🚀 ¡Oportunidad única!\n\n"
            "Trabaja desde casa o en el extranjero.\n"
            "Gana $5,000 mensuales.\n"
            "Sin experiencia requerida.\n\n"
            "👉 https://trabajo-global-ya.example.com/registro\n\n"
            "#trabajoRemoto #altaPaga #oportunidad"
        ),
    },
    {
        "recruiter_index": 2,
        "image_url": "https://picsum.photos/id/1040/600/600",
        "caption": (
            "✨ LUXURY MODELS EUROPE busca talento nuevo ✨\n\n"
            "Casting exclusivo en el extranjero para jóvenes entre 18-25.\n"
            "Viaje todo pagado + sesión profesional.\n\n"
            "Envía fotos y contacto aquí:\n"
            "https://elite-models-intl.example.com/apply\n\n"
            "#casting #modeloInternacional #lujo"
        ),
    },
]

# ---------------------------------------------------------------------------
# Publicaciones legítimas
# ---------------------------------------------------------------------------
LEGIT_POSTS = [
    {"user_index": 0, "caption": "Nuevo proyecto de diseño para una cafetería local ☕ Me encantó el resultado.", "image_url": "https://picsum.photos/id/225/600/600"},
    {"user_index": 1, "caption": "Atardecer en Manuel Antonio. La naturaleza nunca decepciona. 🌅", "image_url": "https://picsum.photos/id/235/600/600"},
    {"user_index": 2, "caption": "Rutina de hoy: 40 min cardio + 20 min core. ¡A darle! 💪", "image_url": "https://picsum.photos/id/245/600/600"},
    {"user_index": 3, "caption": "Acabo de deployear mi primer API en producción. Se siente bien. 🚀", "image_url": "https://picsum.photos/id/255/600/600"},
    {"user_index": 4, "caption": "Nueva canción disponible en Spotify. Link en bio. 🎵", "image_url": "https://picsum.photos/id/265/600/600"},
    {"user_index": 5, "caption": "País #16: Portugal. Lisboa me robó el corazón. 🇵🇹", "image_url": "https://picsum.photos/id/275/600/600"},
    {"user_index": 8, "caption": "Hoy aprendí a hacer pasta fresca desde cero. Nivel: desbloqueado. 🍝", "image_url": "https://picsum.photos/id/292/600/600"},
    {"user_index": 10, "caption": "Reseña: 'Cien años de soledad'. Obra maestra absoluta. 📚", "image_url": "https://picsum.photos/id/315/600/600"},
    {
        "user_index": 12,
        "caption": (
            "Si buscas empleo legítimo revisa el portal oficial: "
            "https://empleos.gobierno.example.com/buscar ✅"
        ),
        "image_url": "https://picsum.photos/id/325/600/600",
    },
    {"user_index": 14, "caption": "Clase de yoga al amanecer en Montezuma. Paz total. 🧘", "image_url": "https://picsum.photos/id/335/600/600"},
]

# ---------------------------------------------------------------------------
# Plantilla de DM de reclutamiento masivo
# ---------------------------------------------------------------------------
DM_TEMPLATES = [
    (
        "¡Hola! 👋 Vi tu perfil y tienes mucho talento. "
        "Estamos buscando modelos para un casting exclusivo en el extranjero. "
        "Viaje todo pagado. Escríbeme a este link para más info: "
        "https://elite-models-intl.example.com/apply"
    ),
    (
        "Hey! 😊 ¿Te gustaría trabajar en el extranjero? "
        "Sin experiencia necesaria. Ingresos inmediatos desde $3,000/mes. "
        "Aplica aquí: https://trabajo-global-ya.example.com/registro"
    ),
    (
        "Hola! Me encanta tu perfil. Tenemos una oportunidad única de modelaje "
        "internacional con viaje todo pagado. Envía fotos de cuerpo completo "
        "aquí: https://elite-models-intl.example.com/apply"
    ),
]


def _random_time(base: datetime, max_offset_hours: int = 72) -> datetime:
    offset = timedelta(
        hours=random.randint(0, max_offset_hours),
        minutes=random.randint(0, 59),
    )
    return base - offset


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    now = datetime.now(timezone.utc)

    try:
        # --- Landing Pages ---
        landing_pages = []
        for lp_data in LANDING_PAGES:
            lp = LandingPage(**lp_data)
            db.add(lp)
            landing_pages.append(lp)
        db.flush()

        # --- Legitimate Users ---
        legit_users: list[User] = []
        for u_data in LEGITIMATE_USERS:
            user = User(
                **u_data,
                is_recruiter=False,
                is_verified=False,
                profile_picture_url=f"https://picsum.photos/id/{random.randint(100, 500)}/300/300",
                created_at=_random_time(now, max_offset_hours=720),
            )
            db.add(user)
            legit_users.append(user)
        db.flush()

        # --- Recruiter Users ---
        recruiter_users: list[User] = []
        for r_data in RECRUITER_USERS:
            user = User(
                **r_data,
                is_recruiter=True,
                is_verified=False,
                created_at=_random_time(now, max_offset_hours=48),
            )
            db.add(user)
            recruiter_users.append(user)
        db.flush()

        # --- Followers: legit users follow each other organically ---
        for i, user in enumerate(legit_users):
            follow_count = random.randint(3, min(8, len(legit_users) - 1))
            targets = random.sample(
                [u for u in legit_users if u.id != user.id],
                k=follow_count,
            )
            for target in targets:
                existing = (
                    db.query(Follower)
                    .filter(Follower.follower_id == user.id, Follower.following_id == target.id)
                    .first()
                )
                if not existing:
                    db.add(Follower(follower_id=user.id, following_id=target.id))

        # --- Recruiters follow MANY legitimate users (anomalous ratio) ---
        for recruiter in recruiter_users:
            for legit in legit_users:
                db.add(Follower(follower_id=recruiter.id, following_id=legit.id))
        db.flush()

        # --- Legit posts ---
        for p_data in LEGIT_POSTS:
            author = legit_users[p_data["user_index"]]
            post = Post(
                author_id=author.id,
                caption=p_data["caption"],
                image_url=p_data["image_url"],
                likes_count=random.randint(5, 150),
                created_at=_random_time(now, max_offset_hours=168),
            )
            db.add(post)

        # --- Recruiter posts ---
        recruiter_posts: list[Post] = []
        for p_data in RECRUITER_POSTS:
            author = recruiter_users[p_data["recruiter_index"]]
            post = Post(
                author_id=author.id,
                caption=p_data["caption"],
                image_url=p_data["image_url"],
                likes_count=random.randint(0, 10),
                created_at=_random_time(now, max_offset_hours=24),
            )
            db.add(post)
            recruiter_posts.append(post)
        db.flush()

        # --- Mass DMs from recruiters to legit users ---
        dm_base_time = now - timedelta(hours=2)
        for recruiter in recruiter_users:
            template = random.choice(DM_TEMPLATES)
            for i, target in enumerate(legit_users):
                variation = template
                if random.random() < 0.1:
                    variation = variation.replace("👋", "🌟").replace("😊", "✨")
                dm = DirectMessage(
                    sender_id=recruiter.id,
                    recipient_id=target.id,
                    body=variation,
                    created_at=dm_base_time + timedelta(minutes=i * 2),
                )
                db.add(dm)
        db.flush()

        # --- Reports from legit users on recruiter posts ---
        reporting_users = random.sample(legit_users, k=min(6, len(legit_users)))
        for rp in recruiter_posts[:3]:
            reporters = random.sample(reporting_users, k=random.randint(2, 4))
            for reporter in reporters:
                report = Report(
                    reporter_id=reporter.id,
                    reported_user_id=rp.author_id,
                    post_id=rp.id,
                    reason="sospecha_captacion",
                    description="Esta publicación parece ser un intento de reclutamiento fraudulento.",
                    created_at=_random_time(now, max_offset_hours=12),
                )
                db.add(report)

        # --- Reports on DMs ---
        all_dms = db.query(DirectMessage).all()
        reported_dms = random.sample(all_dms, k=min(8, len(all_dms)))
        for dm in reported_dms:
            reporter = random.choice(legit_users)
            if reporter.id != dm.sender_id:
                report = Report(
                    reporter_id=reporter.id,
                    reported_user_id=dm.sender_id,
                    message_id=dm.id,
                    reason="mensaje_sospechoso",
                    description="Recibí un mensaje de reclutamiento sospechoso de alguien que no conozco.",
                    created_at=_random_time(now, max_offset_hours=6),
                )
                db.add(report)

        db.commit()
        print("=== Finsta Seeder Completado ===")
        print(f"  Usuarios legítimos: {len(legit_users)}")
        print(f"  Usuarios reclutadores: {len(recruiter_users)}")
        print(f"  Landing pages: {len(landing_pages)}")
        print(f"  Publicaciones legítimas: {len(LEGIT_POSTS)}")
        print(f"  Publicaciones de reclutadores: {len(recruiter_posts)}")
        print(f"  DMs masivos enviados: {len(recruiter_users) * len(legit_users)}")
        print(f"  Reportes generados: {len(reporting_users) + len(reported_dms)} aprox")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
