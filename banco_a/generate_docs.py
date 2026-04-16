"""
Genera la documentación técnica de FlowLens - Banco A en PDF.
Uso: python generate_docs.py
Requiere: fpdf2  (pip install fpdf2)
"""

from fpdf import FPDF, XPos, YPos
from datetime import date

OUTPUT = "FlowLens_BancoA_Documentacion.pdf"

# --- Paleta ------------------------------------------------------------------
BLUE   = (37,  99, 235)
LBLUE  = (219, 234, 254)
DARK   = (30,  41,  59)
MUTED  = (100, 116, 139)
WHITE  = (255, 255, 255)
LIGHT  = (248, 250, 252)
GREEN  = (22,  163,  74)
BORDER = (226, 232, 240)

# --- Clase principal ----------------------------------------------------------
class Doc(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*BLUE)
        self.rect(0, 0, 210, 10, "F")
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*WHITE)
        self.set_xy(0, 1)
        self.cell(0, 8, "FlowLens - Banco A - Documentación Técnica", align="C")
        self.set_text_color(*DARK)
        self.ln(6)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 10, f"Página {self.page_no()}  ·  FlowLens Platform  ·  {date.today().strftime('%d/%m/%Y')}", align="C")

    # -- Helpers --------------------------------------------------------------
    def h1(self, txt):
        self.ln(6)
        self.set_fill_color(*BLUE)
        self.rect(self.get_x(), self.get_y(), 190, 9, "F")
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*WHITE)
        self.set_x(12)
        self.cell(0, 9, f"  {txt}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*DARK)
        self.ln(4)

    def h2(self, txt):
        self.ln(4)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*BLUE)
        self.cell(0, 7, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*LBLUE)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.set_text_color(*DARK)
        self.ln(3)

    def h3(self, txt):
        self.ln(3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*DARK)
        self.cell(0, 6, txt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def body(self, txt):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5, txt)
        self.ln(2)

    def bullet(self, items):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DARK)
        for item in items:
            self.set_x(16)
            self.cell(5, 5, "-")
            self.set_x(21)
            self.multi_cell(169, 5, item)

    def code_block(self, lines):
        self.ln(2)
        self.set_fill_color(*LIGHT)
        self.set_draw_color(*BORDER)
        x = self.get_x()
        y = self.get_y()
        line_h = 4.5
        total_h = len(lines) * line_h + 6
        self.rect(10, y, 190, total_h, "FD")
        self.set_font("Courier", "", 8)
        self.set_text_color(30, 41, 59)
        for i, line in enumerate(lines):
            self.set_xy(14, y + 3 + i * line_h)
            self.cell(0, line_h, line)
        self.set_xy(x, y + total_h + 2)
        self.set_text_color(*DARK)
        self.ln(2)

    def table_row(self, cols, widths, bold=False, header=False):
        self.set_font("Helvetica", "B" if bold else "", 8.5)
        if header:
            self.set_fill_color(*LBLUE)
            self.set_text_color(*BLUE)
        else:
            self.set_fill_color(*WHITE)
            self.set_text_color(*DARK)
        for txt, w in zip(cols, widths):
            self.cell(w, 6, str(txt), border=1, fill=True)
        self.ln()

    def info_box(self, title, body_txt, color=None):
        c = color or LBLUE
        self.ln(3)
        self.set_fill_color(*c)
        self.set_draw_color(*BORDER)
        x, y = self.get_x(), self.get_y()
        self.rect(10, y, 190, 6, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*BLUE)
        self.set_xy(14, y + 0.5)
        self.cell(0, 5, title)
        self.ln(7)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DARK)
        self.set_fill_color(240, 245, 255)
        self.set_x(10)
        self.multi_cell(190, 5, body_txt, fill=True)
        self.ln(2)


# --- Contenido ----------------------------------------------------------------
def build(pdf: Doc):

    # ==========================================================
    # PORTADA
    # ==========================================================
    pdf.add_page()
    # fondo
    pdf.set_fill_color(*BLUE)
    pdf.rect(0, 0, 210, 120, "F")
    pdf.set_fill_color(*LBLUE)
    pdf.rect(0, 120, 210, 177, "F")

    pdf.set_font("Helvetica", "B", 38)
    pdf.set_text_color(*WHITE)
    pdf.set_y(38)
    pdf.cell(0, 14, "FlowLens", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 8, "Plataforma Distribuida de Simulación Bancaria", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 9, "Banco A - Documentación Técnica", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*LBLUE)
    pdf.ln(6)
    pdf.cell(0, 7, f"Versión 1.0  ·  {date.today().strftime('%d de %B de %Y')}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(140)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 8, "Contenido de este documento", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    toc = [
        ("1", "Descripción general del proyecto"),
        ("2", "Arquitectura y estructura de carpetas"),
        ("3", "Base de datos y configuración"),
        ("4", "Modelos de datos (SQLAlchemy)"),
        ("5", "Esquemas de validación (Pydantic)"),
        ("6", "Seguridad y autenticación JWT"),
        ("7", "Capa de servicios (lógica de negocio)"),
        ("8", "Rutas de la API (endpoints)"),
        ("9", "Aplicación principal (main.py)"),
        ("10", "Frontend React - estructura y páginas"),
        ("11", "Cómo ejecutar el proyecto"),
        ("12", "Referencia de endpoints"),
    ]
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*DARK)
    for num, title in toc:
        pdf.set_x(40)
        pdf.cell(15, 6.5, num + ".", align="R")
        pdf.cell(130, 6.5, title)
        pdf.ln()

    # ==========================================================
    # 1. DESCRIPCIÓN GENERAL
    # ==========================================================
    pdf.add_page()
    pdf.h1("1. Descripción general del proyecto")

    pdf.body(
        "FlowLens es una plataforma distribuida de simulación bancaria y análisis transaccional. "
        "Su objetivo es reproducir el funcionamiento de múltiples bancos independientes con backends, "
        "bases de datos y usuarios propios, permitiendo además comunicación interbancaria y análisis "
        "externo de patrones sospechosos mediante un módulo de analytics.\n\n"
        "Este documento cubre exclusivamente el Banco A (código BKA), que es la primera unidad "
        "funcional del sistema. Está construido con FastAPI, SQLAlchemy y SQLite, y expone una API "
        "REST completa para registro de usuarios, gestión de cuentas y transferencias internas."
    )

    pdf.h2("Alcance del Banco A")
    pdf.bullet([
        "Registro e inicio de sesión de usuarios con JWT y bcrypt.",
        "Creación de cuentas bancarias con número único generado automáticamente (formato BKA-XXXXXXXXXX).",
        "Consulta de saldo e historial de transacciones por usuario.",
        "Transferencias internas entre cuentas del mismo banco con validación de reglas de negocio.",
        "API documentada automáticamente en /docs (Swagger UI) y /redoc.",
    ])

    pdf.h2("Lo que NO incluye esta fase")
    pdf.bullet([
        "Transferencias interbancarias (fase futura).",
        "Motor de análisis de riesgo ni alertas (vive en el módulo analytics).",
        "Grafo de red transaccional.",
        "Despliegue en producción (diseñado para desarrollo local).",
    ])

    pdf.info_box(
        "Nota de seguridad",
        "FlowLens es una simulación técnica demostrativa. No usa dinero real, no se conecta a "
        "sistemas bancarios reales y trabaja exclusivamente con datos sintéticos o de prueba. "
        "El módulo analytics requiere autenticación separada."
    )

    # ==========================================================
    # 2. ARQUITECTURA
    # ==========================================================
    pdf.add_page()
    pdf.h1("2. Arquitectura y estructura de carpetas")

    pdf.body(
        "El Banco A sigue una arquitectura en capas limpia, donde cada directorio tiene una "
        "responsabilidad única. Esto facilita el mantenimiento, las pruebas y la extensión futura."
    )

    pdf.code_block([
        "banco_a/",
        "+-- app/",
        "|   +-- __init__.py",
        "|   +-- main.py          <- FastAPI app, CORS, registro de routers",
        "|   +-- settings.py      <- Configuración global (env vars, constantes)",
        "|   +-- database.py      <- Engine SQLAlchemy, Base, get_db, init_db",
        "|   +-- core/",
        "|   |   +-- security.py       <- JWT + bcrypt",
        "|   |   +-- dependencies.py   <- get_current_user (inyectable)",
        "|   +-- models/",
        "|   |   +-- user.py           <- Tabla users",
        "|   |   +-- account.py        <- Tabla accounts",
        "|   |   +-- transaction.py    <- Tabla transactions",
        "|   +-- schemas/",
        "|   |   +-- user.py           <- Pydantic: UserCreate, UserResponse, etc.",
        "|   |   +-- account.py        <- AccountCreate, AccountResponse",
        "|   |   +-- transaction.py    <- TransferRequest, TransactionResponse",
        "|   +-- services/",
        "|   |   +-- auth_service.py        <- Registro y autenticación",
        "|   |   +-- account_service.py     <- Creación y consulta de cuentas",
        "|   |   +-- transaction_service.py <- Transferencias y validaciones",
        "|   +-- routes/",
        "|       +-- auth.py         <- POST /auth/register, login; GET /auth/me",
        "|       +-- accounts.py     <- POST /accounts; GET /accounts/my, /{id}",
        "|       +-- transactions.py <- POST /transactions/internal; GET /transactions/my",
        "+-- frontend/            <- Portal React del cliente",
        "+-- requirements.txt",
        "+-- run.py               <- Lanza uvicorn en el puerto 8000",
    ])

    pdf.h2("Flujo de una solicitud HTTP")
    pdf.body(
        "Cuando un cliente realiza una petición, por ejemplo POST /transactions/internal, "
        "el flujo es el siguiente:"
    )
    pdf.bullet([
        "FastAPI (main.py) recibe la petición y la enruta a transactions.router.",
        "El endpoint en routes/transactions.py valida el body con Pydantic (TransferRequest).",
        "La dependencia get_current_user (core/dependencies.py) verifica el JWT del header.",
        "El endpoint llama a transaction_service.create_internal_transfer(db, data, user).",
        "El servicio aplica las reglas de negocio: monto > 0, cuentas distintas, saldo suficiente.",
        "Si todo es válido, actualiza los saldos y persiste la Transaction en SQLite.",
        "La respuesta se serializa con TransactionResponse (Pydantic) y se devuelve al cliente.",
    ])

    pdf.h2("Principio de separación de responsabilidades")
    pdf.ln(2)
    widths = [38, 55, 97]
    pdf.table_row(["Capa", "Archivo", "Responsabilidad"], widths, header=True)
    rows = [
        ("Config",    "settings.py",            "Centraliza todas las constantes y variables de entorno."),
        ("DB",        "database.py",             "Gestiona la conexión, Base y ciclo de vida de sesiones."),
        ("Seguridad", "core/security.py",        "Hash de contraseñas y generación/verificación de JWT."),
        ("Dep.",      "core/dependencies.py",    "Inyecta el usuario autenticado en los endpoints."),
        ("Modelos",   "models/*.py",             "Define las tablas SQL como clases Python (ORM)."),
        ("Esquemas",  "schemas/*.py",            "Valida y serializa datos de entrada/salida (Pydantic)."),
        ("Servicios", "services/*.py",           "Contiene la lógica de negocio, sin acoplarse a HTTP."),
        ("Rutas",     "routes/*.py",             "Declara los endpoints; delega lógica a servicios."),
    ]
    for r in rows:
        pdf.table_row(r, widths)

    # ==========================================================
    # 3. DATABASE.PY Y SETTINGS.PY
    # ==========================================================
    pdf.add_page()
    pdf.h1("3. Base de datos y configuración")

    pdf.h2("app/settings.py - Configuración global")
    pdf.body(
        "Centraliza todas las constantes del banco. Todas leen variables de entorno con "
        "un valor por defecto, facilitando el despliegue en distintos entornos sin tocar el código."
    )
    pdf.code_block([
        "BANK_ID    = os.getenv('BANK_ID',    'banco_a')",
        "BANK_NAME  = os.getenv('BANK_NAME',  'Banco A')",
        "BANK_CODE  = os.getenv('BANK_CODE',  'BKA')       # prefijo de números de cuenta",
        "SECRET_KEY = os.getenv('BANK_SECRET_KEY', '...')  # clave para firmar JWT",
        "ALGORITHM  = 'HS256'",
        "ACCESS_TOKEN_EXPIRE_MINUTES = 720               # 12 horas",
        "DATABASE_URL = f'sqlite:///{DATABASE_PATH}'",
    ])
    pdf.bullet([
        "BANK_CODE se usa al generar números de cuenta: BKA-XXXXXXXXXX.",
        "SECRET_KEY DEBE cambiarse en producción. El valor por defecto es solo para desarrollo.",
        "ALLOWED_ORIGINS define los orígenes CORS permitidos (puertos de desarrollo de Vite).",
    ])

    pdf.h2("app/database.py - Conexión y ciclo de vida")
    pdf.body(
        "Este archivo es el núcleo de la persistencia. Define tres piezas fundamentales:"
    )
    pdf.bullet([
        "engine: la conexión real a SQLite. Se crea una sola vez al importar el módulo.",
        "SessionLocal: fábrica de sesiones. Cada request HTTP abre una sesión nueva y la cierra al terminar.",
        "Base: clase padre de todos los modelos. Al heredar de Base, SQLAlchemy registra la clase en metadata.",
    ])
    pdf.code_block([
        "def get_db():                   # Dependencia inyectable en FastAPI",
        "    db = SessionLocal()         # Abre sesión",
        "    try:",
        "        yield db               # La cede al endpoint",
        "    finally:",
        "        db.close()             # La cierra siempre, haya error o no",
        "",
        "def init_db():                  # Llamada al arrancar la app",
        "    from . import models        # Importa los modelos (efecto de lado: los registra en Base)",
        "    Base.metadata.create_all(bind=engine)  # Crea las tablas físicas en SQLite",
    ])
    pdf.body(
        "El hook PRAGMA foreign_keys=ON activa la integridad referencial de SQLite, que por "
        "defecto está desactivada. Se dispara automáticamente en cada nueva conexión."
    )

    # ==========================================================
    # 4. MODELOS
    # ==========================================================
    pdf.add_page()
    pdf.h1("4. Modelos de datos (SQLAlchemy ORM)")

    pdf.body(
        "Los modelos son clases Python que representan tablas en la base de datos. "
        "SQLAlchemy los mapea automáticamente. Cada columna es un atributo de clase."
    )

    pdf.h2("models/user.py - Tabla users")
    pdf.code_block([
        "class User(Base):",
        "    __tablename__ = 'users'",
        "    id              = Column(Integer, primary_key=True)",
        "    full_name       = Column(String(255), nullable=False)",
        "    email           = Column(String(255), unique=True, index=True)",
        "    hashed_password = Column(String(255), nullable=False)",
        "    role            = Column(String(50), default='client')  # 'client' | 'admin'",
        "    created_at      = Column(DateTime, default=datetime.utcnow)",
        "    accounts        = relationship('Account', back_populates='owner', cascade='all, delete-orphan')",
    ])
    pdf.bullet([
        "email tiene un índice único - ningún usuario puede registrarse dos veces con el mismo correo.",
        "role está preparado para diferenciar clientes de administradores en fases futuras.",
        "La relación accounts permite acceder a User.accounts directamente desde Python.",
        "cascade='all, delete-orphan' borra las cuentas si el usuario es eliminado.",
    ])

    pdf.h2("models/account.py - Tabla accounts")
    pdf.code_block([
        "class Account(Base):",
        "    __tablename__ = 'accounts'",
        "    id             = Column(Integer, primary_key=True)",
        "    account_number = Column(String(20), unique=True, index=True)  # BKA-XXXXXXXXXX",
        "    user_id        = Column(Integer, ForeignKey('users.id'), index=True)",
        "    bank_code      = Column(String(10), default='BKA')",
        "    balance        = Column(Float, default=0.0)",
        "    currency       = Column(String(10), default='CRC')",
        "    status         = Column(String(20), default='active')  # 'active' | 'inactive'",
        "    created_at     = Column(DateTime, default=datetime.utcnow)",
        "    owner          = relationship('User', back_populates='accounts')",
    ])
    pdf.bullet([
        "account_number es único en toda la base de datos.",
        "bank_code='BKA' identifica a qué banco pertenece la cuenta. Clave para futuros interbancarios.",
        "currency='CRC' (Colón costarricense) es el valor por defecto.",
        "status permite desactivar cuentas sin eliminarlas.",
    ])

    pdf.h2("models/transaction.py - Tabla transactions")
    pdf.code_block([
        "class Transaction(Base):",
        "    __tablename__ = 'transactions'",
        "    id                         = Column(Integer, primary_key=True)",
        "    source_account_number      = Column(String(20), index=True)",
        "    destination_account_number = Column(String(20), index=True)",
        "    source_bank_code           = Column(String(10))",
        "    destination_bank_code      = Column(String(10))",
        "    amount                     = Column(Float)",
        "    currency                   = Column(String(10), default='CRC')",
        "    transaction_type           = Column(String(50), default='internal_transfer')",
        "    status                     = Column(String(20), default='completed')",
        "    channel                    = Column(String(50), default='web')",
        "    location                   = Column(String(255), nullable=True)",
        "    description                = Column(Text, nullable=True)",
        "    created_at                 = Column(DateTime, default=datetime.utcnow)",
    ])
    pdf.body(
        "Decisión de diseño clave: Transaction usa account_number (strings) en lugar de FKs "
        "enteras a la tabla accounts. Esto permite registrar transacciones con cuentas externas "
        "(de otros bancos) sin violar integridad referencial. Es esencial para soportar "
        "transferencias interbancarias en fases futuras."
    )

    # ==========================================================
    # 5. SCHEMAS
    # ==========================================================
    pdf.add_page()
    pdf.h1("5. Esquemas de validación (Pydantic)")

    pdf.body(
        "Los schemas son la capa de contrato entre el cliente HTTP y la aplicación. "
        "Pydantic valida automáticamente los tipos, formatos y restricciones antes de que el "
        "código de negocio siquiera se ejecute. Errores de formato retornan 422 Unprocessable Entity."
    )

    pdf.h2("schemas/user.py")
    pdf.code_block([
        "class UserCreate(BaseModel):    # Body del POST /auth/register",
        "    full_name: str",
        "    email:     EmailStr         # Valida que sea un email real",
        "    password:  str",
        "",
        "class UserResponse(BaseModel):  # Lo que devuelve la API (nunca expone hashed_password)",
        "    id: int  |  full_name: str  |  email: str  |  role: str  |  created_at: datetime",
        "    model_config = {'from_attributes': True}  # Permite leer desde objetos SQLAlchemy",
        "",
        "class LoginRequest(BaseModel):  # Body del POST /auth/login",
        "    email: EmailStr  |  password: str",
        "",
        "class TokenResponse(BaseModel): # Respuesta del login",
        "    access_token: str  |  token_type: str = 'bearer'  |  user: UserResponse",
    ])

    pdf.h2("schemas/account.py")
    pdf.code_block([
        "class AccountCreate(BaseModel): # Body del POST /accounts",
        "    initial_balance: float = 0.0",
        "",
        "class AccountResponse(BaseModel):",
        "    id, account_number, bank_code, balance, currency, status, created_at",
    ])

    pdf.h2("schemas/transaction.py")
    pdf.code_block([
        "class TransferRequest(BaseModel): # Body del POST /transactions/internal",
        "    source_account_number:      str",
        "    destination_account_number: str",
        "    amount:                     float",
        "    channel:     str = 'web'    # web | mobile | atm | api",
        "    location:    str = ''",
        "    description: str = ''",
        "",
        "class TransactionResponse(BaseModel):",
        "    id, source_account_number, destination_account_number,",
        "    source_bank_code, destination_bank_code, amount, currency,",
        "    transaction_type, status, channel, location, description, created_at",
    ])

    # ==========================================================
    # 6. SEGURIDAD
    # ==========================================================
    pdf.add_page()
    pdf.h1("6. Seguridad y autenticación JWT")

    pdf.h2("core/security.py - Hash y tokens")
    pdf.body(
        "Este módulo encapsula toda la criptografía. Usa dos librerías:"
    )
    pdf.bullet([
        "passlib[bcrypt]: para hashear y verificar contraseñas. bcrypt es el estándar de la industria "
        "para almacenamiento seguro de passwords. Jamás se guarda la contraseña en texto plano.",
        "python-jose: para generar y decodificar tokens JWT firmados con HS256.",
    ])
    pdf.code_block([
        "def hash_password(password: str) -> str:",
        "    return pwd_context.hash(password)            # Retorna '$2b$12$...' (bcrypt)",
        "",
        "def verify_password(plain: str, hashed: str) -> bool:",
        "    return pwd_context.verify(plain, hashed)     # Compara sin exponer el hash",
        "",
        "def create_access_token(data: dict) -> str:",
        "    payload = data.copy()",
        "    payload['exp'] = datetime.utcnow() + timedelta(minutes=720)  # 12 horas",
        "    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')",
        "",
        "def decode_access_token(token: str) -> dict | None:",
        "    try: return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])",
        "    except JWTError: return None  # Token inválido o expirado",
    ])

    pdf.h2("core/dependencies.py - get_current_user")
    pdf.body(
        "Esta es la dependencia de autenticación que se inyecta en todos los endpoints protegidos. "
        "FastAPI la llama automáticamente gracias al decorador Depends()."
    )
    pdf.code_block([
        "oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')",
        "",
        "def get_current_user(token = Depends(oauth2_scheme), db = Depends(get_db)) -> User:",
        "    payload = decode_access_token(token)",
        "    if payload is None:",
        "        raise HTTPException(401, 'Token inválido o expirado')",
        "    user = db.query(User).filter(User.id == int(payload['sub'])).first()",
        "    if user is None:",
        "        raise HTTPException(401, 'Usuario no encontrado')",
        "    return user    # FastAPI lo inyecta en el parámetro del endpoint",
    ])
    pdf.bullet([
        "El token llega en el header: Authorization: Bearer <token>",
        "payload['sub'] contiene el user_id como string (estándar JWT).",
        "Si el token expiró o es inválido, retorna HTTP 401 automáticamente.",
        "Los endpoints protegidos solo añaden: current_user: User = Depends(get_current_user)",
    ])

    # ==========================================================
    # 7. SERVICIOS
    # ==========================================================
    pdf.add_page()
    pdf.h1("7. Capa de servicios (lógica de negocio)")

    pdf.body(
        "Los servicios son el corazón de la aplicación. Contienen la lógica de negocio "
        "completamente desacoplada del protocolo HTTP. Esto significa que la misma lógica "
        "podría ser llamada desde una CLI, un test unitario o un worker sin cambiar nada."
    )

    pdf.h2("services/auth_service.py")
    pdf.bullet([
        "register_user(db, data): verifica que el email no exista, hashea la contraseña y crea el usuario.",
        "authenticate_user(db, email, password): busca al usuario, verifica la contraseña con bcrypt "
        "y devuelve (token, user). Si falla, lanza HTTP 401.",
    ])

    pdf.h2("services/account_service.py")
    pdf.bullet([
        "_generate_account_number(db): genera un número BKA-XXXXXXXXXX con dígitos aleatorios, "
        "verificando en la base de datos que no exista ya (loop hasta encontrar uno único).",
        "create_account(db, user, initial_balance): crea la cuenta con bank_code='BKA' y currency='CRC'.",
        "get_accounts_by_user(db, user): retorna todas las cuentas del usuario autenticado.",
        "get_account_by_id(db, account_id, user): retorna una cuenta específica, validando propiedad.",
    ])

    pdf.h2("services/transaction_service.py - Reglas de negocio")
    pdf.body(
        "Este es el servicio más importante. Implementa todas las validaciones antes de mover dinero:"
    )
    pdf.bullet([
        "Monto > 0: no se puede transferir 0 ni montos negativos.",
        "Cuenta origen - destino: no se puede transferir a sí mismo.",
        "Cuentas deben existir y estar activas (status='active').",
        "El usuario autenticado debe ser propietario de la cuenta origen.",
        "Ambas cuentas deben pertenecer al banco BKA (transferencias internas).",
        "Saldo suficiente: source.balance >= amount.",
    ])
    pdf.code_block([
        "# Si todas las validaciones pasan:",
        "source.balance      -= data.amount    # Débito",
        "destination.balance += data.amount    # Crédito",
        "txn = Transaction(...)                # Registro inmutable",
        "db.add(txn)",
        "db.commit()                           # Atómico: todo o nada",
    ])
    pdf.body(
        "El commit es atómico: si ocurre cualquier error después del débito pero antes del "
        "crédito, SQLAlchemy hace rollback automáticamente y ninguna cuenta queda descuadrada."
    )

    # ==========================================================
    # 8. RUTAS
    # ==========================================================
    pdf.add_page()
    pdf.h1("8. Rutas de la API (endpoints)")

    pdf.body(
        "Los routers de FastAPI definen los endpoints HTTP. Son deliberadamente delgados: "
        "validan la entrada con Pydantic, inyectan dependencias y delegan la lógica al servicio."
    )

    pdf.h2("routes/auth.py")
    pdf.code_block([
        "# POST /auth/register  -> 201 Created",
        "# Body: { full_name, email, password }",
        "# Retorna: UserResponse",
        "",
        "# POST /auth/login  -> 200 OK",
        "# Body: { email, password }",
        "# Retorna: { access_token, token_type, user }",
        "",
        "# GET /auth/me  -> 200 OK  [PROTEGIDO]",
        "# Header: Authorization: Bearer <token>",
        "# Retorna: UserResponse del usuario autenticado",
    ])

    pdf.h2("routes/accounts.py")
    pdf.code_block([
        "# POST /accounts  -> 201 Created  [PROTEGIDO]",
        "# Body: { initial_balance: 0.0 }",
        "# Retorna: AccountResponse con número de cuenta generado",
        "",
        "# GET /accounts/my  -> 200 OK  [PROTEGIDO]",
        "# Retorna: lista de AccountResponse del usuario autenticado",
        "",
        "# GET /accounts/{account_id}  -> 200 OK  [PROTEGIDO]",
        "# Retorna: AccountResponse (solo si pertenece al usuario autenticado)",
    ])

    pdf.h2("routes/transactions.py")
    pdf.code_block([
        "# POST /transactions/internal  -> 201 Created  [PROTEGIDO]",
        "# Body: { source_account_number, destination_account_number,",
        "#         amount, channel, location, description }",
        "# Retorna: TransactionResponse",
        "",
        "# GET /transactions/my  -> 200 OK  [PROTEGIDO]",
        "# Retorna: todas las transacciones donde el usuario es origen o destino",
        "#          ordenadas por fecha descendente",
    ])

    pdf.h2("app/main.py - Punto de entrada de FastAPI")
    pdf.code_block([
        "app = FastAPI(title='Banco A API', lifespan=lifespan)",
        "",
        "# lifespan llama a init_db() al arrancar -> crea tablas en SQLite",
        "",
        "app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, ...)",
        "",
        "app.include_router(auth.router)          # prefix='/auth'",
        "app.include_router(accounts.router)      # prefix='/accounts'",
        "app.include_router(transactions.router)  # prefix='/transactions'",
        "",
        "@app.get('/')  # Health check: { status: 'ok', bank: 'Banco A' }",
    ])

    # ==========================================================
    # 9. MAIN.PY (ya cubierto arriba, añadir nota)
    # ==========================================================
    pdf.add_page()
    pdf.h1("9. Aplicación principal (main.py)")

    pdf.body(
        "main.py es el archivo que FastAPI ejecuta. Tiene tres responsabilidades:"
    )
    pdf.bullet([
        "Declarar la aplicación con FastAPI() y sus metadatos (título, versión, descripción).",
        "Configurar el middleware CORS para que el frontend pueda hacer peticiones.",
        "Registrar los tres routers (auth, accounts, transactions) con sus prefijos.",
    ])

    pdf.h2("El patrón lifespan")
    pdf.body(
        "FastAPI moderno usa un context manager asíncrono (lifespan) para el ciclo de vida. "
        "Es más limpio que los viejos eventos @app.on_event('startup')."
    )
    pdf.code_block([
        "@asynccontextmanager",
        "async def lifespan(app: FastAPI):",
        "    init_db()   # <- Se ejecuta ANTES de recibir el primer request",
        "    yield       # <- La app corre aquí",
        "                # Después del yield: cleanup (si hubiera)",
    ])

    pdf.h2("CORS - Cross-Origin Resource Sharing")
    pdf.body(
        "CORS es el mecanismo que permite al navegador hacer peticiones desde un origen "
        "(http://localhost:5173 - Vite) a otro (http://127.0.0.1:8000 - FastAPI). "
        "Sin este middleware, el navegador bloquea todas las respuestas del backend. "
        "allow_credentials=True es necesario para enviar el header Authorization."
    )

    # ==========================================================
    # 10. FRONTEND
    # ==========================================================
    pdf.add_page()
    pdf.h1("10. Frontend React - estructura y páginas")

    pdf.body(
        "El frontend es una Single Page Application (SPA) construida con React 18 y Vite. "
        "Se comunica exclusivamente con el backend a través de la API REST. "
        "No tiene acceso directo a la base de datos."
    )

    pdf.h2("Archivos clave")
    pdf.bullet([
        "src/config.js: exporta constantes leídas de variables de entorno Vite (VITE_API_URL, etc.).",
        "src/api.js: función apiRequest() que envuelve fetch con manejo de tokens y errores. "
        "Incluye formatCurrency() (Colón costarricense) y formatDate() (locale es-CR).",
        "src/auth.jsx: AuthContext y AuthProvider. Gestiona token y usuario en localStorage. "
        "Valida el token contra /auth/me al montar la app.",
        "src/styles.css: tema azul profesional con variables CSS, layout de sidebar fijo + contenido.",
        "src/App.jsx: enrutamiento con react-router-dom. ProtectedRoute redirige a /login si no hay sesión.",
    ])

    pdf.h2("Páginas")
    widths2 = [40, 55, 95]
    pdf.table_row(["Página", "Ruta", "Descripción"], widths2, header=True)
    pages = [
        ("LoginPage",       "/login",        "Formulario email/password. Guarda token en localStorage."),
        ("RegisterPage",    "/register",     "Crea usuario y hace login automático al terminar."),
        ("DashboardPage",   "/",             "Resumen: saldo total, cuentas, enviado/recibido, últimas 8 txns."),
        ("AccountsPage",    "/accounts",     "Crea cuentas con saldo inicial. Tabla de todas las cuentas."),
        ("TransferPage",    "/transfer",     "Selecciona cuenta origen, ingresa destino y monto. Valida en tiempo real."),
        ("TransactionsPage","/transactions", "Historial completo. Verde=recibida, Rojo=enviada. Resumen de totales."),
    ]
    for p in pages:
        pdf.table_row(p, widths2)

    pdf.h2("Flujo de autenticación en el frontend")
    pdf.bullet([
        "Al iniciar sesión, el servidor retorna { access_token, user }.",
        "AuthProvider guarda ambos en localStorage (bka_token, bka_user).",
        "Al montar la app, llama GET /auth/me para verificar que el token siga válido.",
        "Si el token expiró o es inválido, limpia localStorage y redirige a /login.",
        "Todos los componentes acceden al contexto via el hook useAuth().",
    ])

    # ==========================================================
    # 11. CÓMO EJECUTAR
    # ==========================================================
    pdf.add_page()
    pdf.h1("11. Cómo ejecutar el proyecto")

    pdf.h2("Requisitos previos")
    pdf.bullet([
        "Python 3.10 o superior.",
        "Node.js 18 o superior + npm.",
        "Un entorno virtual Python (recomendado).",
    ])

    pdf.h2("Backend (Banco A)")
    pdf.code_block([
        "# 1. Ir al directorio del banco",
        "cd banco_a",
        "",
        "# 2. Crear y activar entorno virtual",
        "python -m venv .venv",
        "source .venv/bin/activate    # Mac/Linux",
        ".venv\\Scripts\\activate      # Windows",
        "",
        "# 3. Instalar dependencias",
        "pip install -r requirements.txt",
        "",
        "# 4. Levantar la API",
        "python run.py",
        "",
        "# La API queda disponible en:",
        "# http://127.0.0.1:8000",
        "# Swagger UI: http://127.0.0.1:8000/docs",
        "# ReDoc:      http://127.0.0.1:8000/redoc",
    ])

    pdf.h2("Frontend")
    pdf.code_block([
        "# 1. Ir al directorio del frontend",
        "cd banco_a/frontend",
        "",
        "# 2. Instalar dependencias",
        "npm install",
        "",
        "# 3. Levantar el servidor de desarrollo",
        "npm run dev",
        "",
        "# El portal queda en: http://localhost:5173",
    ])

    pdf.h2("Primera prueba rápida")
    pdf.bullet([
        "Abrir http://127.0.0.1:8000/docs",
        "Usar POST /auth/register para crear un usuario.",
        "Usar POST /auth/login para obtener el token. Copiar access_token.",
        "Hacer clic en 'Authorize' (candado) y pegar el token.",
        "Usar POST /accounts para crear una cuenta con saldo inicial.",
        "Crear una segunda cuenta.",
        "Usar POST /transactions/internal para transferir entre las dos cuentas.",
        "Verificar con GET /transactions/my que la transacción fue registrada.",
    ])

    pdf.h2("Variables de entorno opcionales")
    pdf.code_block([
        "BANK_ID=banco_a",
        "BANK_NAME='Banco A'",
        "BANK_CODE=BKA",
        "BANK_SECRET_KEY=mi-clave-super-secreta-2026",
        "BANK_DB_PATH=/ruta/absoluta/a/banco_a.db",
        "ACCESS_TOKEN_EXPIRE_MINUTES=720",
        "VITE_API_URL=http://127.0.0.1:8000   # frontend",
    ])

    # ==========================================================
    # 12. REFERENCIA DE ENDPOINTS
    # ==========================================================
    pdf.add_page()
    pdf.h1("12. Referencia completa de endpoints")

    widths3 = [12, 55, 28, 95]
    pdf.table_row(["Método", "Endpoint", "Auth", "Descripción"], widths3, header=True)
    endpoints = [
        ("GET",  "/",                           "No",  "Health check. Retorna status, banco y banco_id."),
        ("POST", "/auth/register",              "No",  "Registra un nuevo usuario. Body: {full_name, email, password}."),
        ("POST", "/auth/login",                 "No",  "Login. Body: {email, password}. Retorna access_token + user."),
        ("GET",  "/auth/me",                    "Sí",  "Retorna el usuario autenticado actualmente."),
        ("POST", "/accounts",                   "Sí",  "Crea una cuenta bancaria. Body: {initial_balance}."),
        ("GET",  "/accounts/my",                "Sí",  "Lista todas las cuentas del usuario autenticado."),
        ("GET",  "/accounts/{account_id}",      "Sí",  "Retorna una cuenta por ID (solo si es del usuario)."),
        ("POST", "/transactions/internal",      "Sí",  "Transferencia interna. Body: {source, dest, amount, ...}."),
        ("GET",  "/transactions/my",            "Sí",  "Historial de transacciones del usuario autenticado."),
    ]
    for ep in endpoints:
        pdf.table_row(ep, widths3)

    pdf.ln(6)
    pdf.h2("Códigos de error más comunes")
    widths4 = [20, 170]
    pdf.table_row(["Código HTTP", "Significado"], widths4, header=True)
    errors = [
        ("400 Bad Request",        "Datos inválidos: monto <= 0, misma cuenta origen/destino, etc."),
        ("401 Unauthorized",       "Token ausente, inválido o expirado. Credenciales incorrectas."),
        ("403 Forbidden",          "El usuario no es propietario de la cuenta origen."),
        ("404 Not Found",          "Cuenta no encontrada o inactiva."),
        ("422 Unprocessable",      "Error de validación Pydantic. El body no cumple el schema."),
    ]
    for e in errors:
        pdf.table_row(e, widths4)

    pdf.ln(8)
    pdf.info_box(
        "Próximas fases de FlowLens",
        "Fase 2: Transferencias interbancarias entre Banco A, Banco B y Banco C.\n"
        "Fase 3: Módulo externo de Analytics con motor de riesgo por reglas, alertas y grafo de red transaccional.\n"
        "Fase 4: Dashboard de analista con seguimiento profundo de cuentas sospechosas.\n"
        "Fase 5: Despliegue en contenedores con Docker Compose.",
        color=(220, 252, 231)
    )


# --- Main ---------------------------------------------------------------------
if __name__ == "__main__":
    pdf = Doc(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(10, 14, 10)
    build(pdf)
    pdf.output(OUTPUT)
    print(f"OK PDF generado: {OUTPUT}")
