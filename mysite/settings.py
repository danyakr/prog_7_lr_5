import os
from pathlib import Path

# ======================================================================
# Основные настройки проекта
# ======================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-9-p99l$$2-=-29qm&7hmbu20ukkvpb(uzn0g0e7h56+ub9g2z_'
DEBUG = True
ALLOWED_HOSTS = []

# ======================================================================
# Приложения
# ======================================================================

INSTALLED_APPS = [
    # Приложения проекта
    "polls.apps.PollsConfig",
    "analytics.apps.AnalyticsConfig",  # ✅ добавляем analytics

    # Django стандартные приложения
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Формы
    "crispy_forms",
    "crispy_bootstrap5",

    # Авторизация через соцсети
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # API (если нужно для аналитики)
    "rest_framework",
]

# ======================================================================
# Middleware
# ======================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # обязательно!
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

# ======================================================================
# Шаблоны
# ======================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # важно для allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# ======================================================================
# База данных
# ======================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ======================================================================
# Проверка паролей
# ======================================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ======================================================================
# Интернационализация
# ======================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# ======================================================================
# Статика
# ======================================================================

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ======================================================================
# Дополнительные настройки
# ======================================================================

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Сайт (для allauth)
SITE_ID = 1

# Email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ======================================================================
# Авторизация и вход через Google (OAuth 2.0)
# ======================================================================

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # стандартный вход
    "allauth.account.auth_backends.AuthenticationBackend",  # allauth
)

# После входа / выхода
LOGIN_REDIRECT_URL = "/polls/"
LOGOUT_REDIRECT_URL = "/polls/"

# Настройки django-allauth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_SESSION_REMEMBER = True

# Провайдер Google
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        # Можно добавить client_id и secret вручную (если не через админку)
        # "APP": {
        #     "client_id": "ВАШ_CLIENT_ID",
        #     "secret": "ВАШ_CLIENT_SECRET",
        #     "key": ""
        # },
    }
}

# ======================================================================
# Адаптер для мягкого сопоставления email (Google OAuth)
# ======================================================================

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_ADAPTER = "mysite.adapters.MySocialAccountAdapter"

# ======================================================================
# Django REST Framework (если analytics использует API)
# ======================================================================

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}

# ======================================================================
# Логирование
# ======================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
