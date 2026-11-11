import os
from pathlib import Path
from urllib.parse import unquote, urlparse


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("ALLOWED_HOSTS", "*").split(",") if host.strip()]


def database_config():
    default_database = (INSTANCE_DIR / "business.db").as_posix()
    url = os.environ.get("DATABASE_URL", f"sqlite:///{default_database}")
    parsed = urlparse(url)
    if parsed.scheme in {"sqlite", "sqlite3"}:
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
            "PORT": parsed.port or "",
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
STATICFILES_DIRS = [BASE_DIR / "app" / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

PLATFORM_ADMIN_USERNAME = os.environ.get("PLATFORM_ADMIN_USERNAME", "")
PLATFORM_ADMIN_PASSWORD = os.environ.get("PLATFORM_ADMIN_PASSWORD", "")
