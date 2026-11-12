import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
load_dotenv(BASE_DIR / ".env")

IS_VERCEL = os.environ.get("VERCEL", "").lower() in {"1", "true", "yes"}
DEBUG = os.environ.get("DJANGO_DEBUG", "false" if IS_VERCEL else "true").lower() in {"1", "true", "yes"}
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("Set SECRET_KEY to a private value when DJANGO_DEBUG is disabled.")
    SECRET_KEY = "local-development-only-secret-key"

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL and not DEBUG:
    raise ImproperlyConfigured("Set DATABASE_URL to a persistent database for production deployments.")
if not DATABASE_URL:
    INSTANCE_DIR.mkdir(exist_ok=True)

allowed_hosts = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]
for variable in ("VERCEL_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
    host = os.environ.get(variable, "").strip()
    if host:
        allowed_hosts.append(host.removeprefix("https://").removeprefix("http://").rstrip("/"))

if DEBUG:
    ALLOWED_HOSTS = allowed_hosts or ["*"]
elif not allowed_hosts:
    raise ImproperlyConfigured(
        "Set ALLOWED_HOSTS to a comma-separated list of deployment hostnames."
    )
else:
    ALLOWED_HOSTS = list(dict.fromkeys(allowed_hosts))


def database_config():
    default_database = (INSTANCE_DIR / "business.db").as_posix()
    url = DATABASE_URL or f"sqlite:///{default_database}"
    parsed = urlparse(url)
    if parsed.scheme in {"sqlite", "sqlite3"}:
        if not DEBUG:
            raise ImproperlyConfigured("SQLite is not supported for production deployments.")
        database_name = unquote(parsed.path)
        if database_name in {"", "/:memory:"}:
            database_name = ":memory:"
        elif os.name == "nt" and database_name.startswith("/") and len(database_name) > 3 and database_name[2] == ":":
            database_name = database_name[1:]
        elif database_name.startswith("//"):
            database_name = database_name[1:]
        elif database_name.startswith("/") and not url.startswith("sqlite:////"):
            database_name = str(INSTANCE_DIR / database_name.lstrip("/"))
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": database_name}
    if parsed.scheme in {"postgres", "postgresql", "postgresql+psycopg"}:
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(parsed.path.lstrip("/")),
            "USER": unquote(parsed.username or ""),
            "PASSWORD": unquote(parsed.password or ""),
            "HOST": parsed.hostname or "",
            "PORT": parsed.port or 5432,
            "OPTIONS": {
                "sslmode": "require",
            },
        }
    if parsed.scheme in {"mysql", "mysql+mysqldb"}:
        return {
            "ENGINE": "django.db.backends.mysql",
            "NAME": unquote(parsed.path.lstrip("/")),
            "USER": unquote(parsed.username or ""),
            "PASSWORD": unquote(parsed.password or ""),
            "HOST": parsed.hostname or "",
            "PORT": parsed.port or "",
        }
    raise ValueError(f"Unsupported DATABASE_URL scheme: {parsed.scheme}")


DATABASES = {"default": database_config()}

CSRF_TRUSTED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
CSRF_TRUSTED_ORIGINS.extend(
    f"https://{host}" for host in ALLOWED_HOSTS if host != "*" and "://" not in host
)
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app.apps.FieldnoteConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "fieldnote.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "fieldnote.wsgi.application"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = False

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

PLATFORM_ADMIN_USERNAME = os.environ.get("PLATFORM_ADMIN_USERNAME", "")
PLATFORM_ADMIN_PASSWORD = os.environ.get("PLATFORM_ADMIN_PASSWORD", "")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-4-hydrogen")
