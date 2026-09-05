"""
Django settings for o site da Corretora de Milhões.

Stack: Python + Django (escolhido por trazer admin, auth e ORM prontos,
ideal para o painel de autoatendimento da corretora).

Variáveis sensíveis (SECRET_KEY, DEBUG, banco de dados em produção) vêm
de um arquivo .env (veja .env.example) via django-environ.
"""

from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
)
environ.Env.read_env(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-)w&mim13&d%b^c=^_5@_tati5%gg!tu*rdwfsp9d-d#3$ah1*k",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# O Render injeta essa variável sozinho (não precisa configurar no
# dashboard) com a URL pública do serviço, ex: https://corretora-de-milhoes.
# onrender.com. Adicionamos automaticamente aos CSRF_TRUSTED_ORIGINS pra não
# depender de lembrar de preencher CSRF_TRUSTED_ORIGINS na mão — sem isso o
# Django rejeita os POSTs do painel (login, cadastro de imóvel etc.) com
# "Verificação CSRF falhou".
RENDER_EXTERNAL_URL = env("RENDER_EXTERNAL_URL", default="")
if RENDER_EXTERNAL_URL and RENDER_EXTERNAL_URL not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(RENDER_EXTERNAL_URL)

if not DEBUG:
    # O Render fica atrás de um proxy que termina o HTTPS antes da aplicação —
    # sem isso o Django acha que a conexão é HTTP e quebra o redirect/CSRF.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # HSTS: começa em 1 semana (não 1 ano) porque, uma vez que o navegador
    # guarda essa política, ele passa a recusar HTTP para o domínio até o
    # prazo expirar — 1 semana dá margem pra reverter caso precise trocar
    # de domínio/certificado sem trancar visitantes fora do site.
    SECURE_HSTS_SECONDS = 604800


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # apps do projeto
    "core",
    "perfil",
    "imoveis",
    "depoimentos",
    "leads",
    "painel",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.perfil_corretora",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# Em dev usa SQLite (zero configuração). Em produção, defina DATABASE_URL
# no .env (ex: postgres://usuario:senha@host:5432/banco) para trocar para
# Postgres automaticamente.

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Recife"

USE_I18N = True
USE_THOUSAND_SEPARATOR = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Arquivos de mídia (fotos de imóveis, foto da corretora, posts de realização)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Em dev, mídia fica em MEDIA_ROOT (disco local) sem precisar configurar nada.
# Em produção, o disco do Render é temporário — definir as variáveis
# SUPABASE_STORAGE_* (veja .env.example) muda o armazenamento das fotos para
# o Supabase Storage (compatível com S3), que é persistente.
SUPABASE_STORAGE_BUCKET = env("SUPABASE_STORAGE_BUCKET", default="")

if SUPABASE_STORAGE_BUCKET:
    _supabase_endpoint = env("SUPABASE_STORAGE_ENDPOINT_URL")
    # O endpoint S3 (https://<ref>.storage.supabase.co/storage/v1/s3) exige
    # requisição assinada mesmo pra bucket público — o navegador recebe
    # "AccessDenied: Missing signature" ao tentar carregar a foto direto.
    # As fotos precisam ser servidas pela URL pública de objeto da Supabase
    # (https://<ref>.supabase.co/storage/v1/object/public/<bucket>/<arquivo>),
    # que não exige assinatura. custom_domain faz o django-storages montar
    # a .url() das fotos nesse formato em vez do endpoint S3.
    _supabase_ref = _supabase_endpoint.split("//")[1].split(".")[0]
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": SUPABASE_STORAGE_BUCKET,
                "endpoint_url": _supabase_endpoint,
                "access_key": env("SUPABASE_STORAGE_ACCESS_KEY"),
                "secret_key": env("SUPABASE_STORAGE_SECRET_KEY"),
                "region_name": env("SUPABASE_STORAGE_REGION", default="us-east-1"),
                "default_acl": "public-read",
                "querystring_auth": False,
                "custom_domain": f"{_supabase_ref}.supabase.co/storage/v1/object/public/{SUPABASE_STORAGE_BUCKET}",
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login (usuário ou e-mail) sem diferenciar maiúsculas de minúsculas —
# só existe a conta única da corretora, então não faz sentido tratar
# "Renata" e "renata" como contas diferentes.
AUTHENTICATION_BACKENDS = ["painel.backends.CaseInsensitiveModelBackend"]

LOGIN_URL = "painel:login"
LOGIN_REDIRECT_URL = "painel:dashboard"
LOGOUT_REDIRECT_URL = "home"

# A corretora precisa fazer login de novo sempre que fechar o navegador —
# a sessão não sobrevive ao fechamento (não depende do "lembrar de mim").
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# E-mail: avisa a corretora por e-mail a cada novo contato do formulário do
# site (veja leads/views.py). Em dev, sem configurar nada, os e-mails só
# aparecem no terminal (console backend) — em produção usa Gmail via SMTP,
# com uma "senha de app" gerada na conta Google (veja .env.example).
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default=(
        "django.core.mail.backends.console.EmailBackend"
        if DEBUG
        else "django.core.mail.backends.smtp.EmailBackend"
    ),
)
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
