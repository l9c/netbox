import logging
import os
import socket

from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured

try:
    from netbox import configuration
except ImportError:
    raise ImproperlyConfigured(
        "Configuration file is not present. Please define netbox/netbox/configuration.py per the documentation."
    )


VERSION = '2.0.4'

# Import local configuration
ALLOWED_HOSTS = DATABASE = SECRET_KEY = None
for setting in ['ALLOWED_HOSTS', 'DATABASE', 'SECRET_KEY']:
    try:
        globals()[setting] = getattr(configuration, setting)
    except AttributeError:
        raise ImproperlyConfigured(
            "Mandatory setting {} is missing from configuration.py.".format(setting)
        )

# Default configurations
ADMINS = getattr(configuration, 'ADMINS', [])
DEBUG = getattr(configuration, 'DEBUG', False)
EMAIL = getattr(configuration, 'EMAIL', {})
LOGIN_REQUIRED = getattr(configuration, 'LOGIN_REQUIRED', False)
BASE_PATH = getattr(configuration, 'BASE_PATH', '')
if BASE_PATH:
    BASE_PATH = BASE_PATH.strip('/') + '/'  # Enforce trailing slash only
MAINTENANCE_MODE = getattr(configuration, 'MAINTENANCE_MODE', False)
PAGINATE_COUNT = getattr(configuration, 'PAGINATE_COUNT', 50)
NETBOX_USERNAME = getattr(configuration, 'NETBOX_USERNAME', '')
NETBOX_PASSWORD = getattr(configuration, 'NETBOX_PASSWORD', '')
TIME_ZONE = getattr(configuration, 'TIME_ZONE', 'UTC')
DATE_FORMAT = getattr(configuration, 'DATE_FORMAT', 'N j, Y')
SHORT_DATE_FORMAT = getattr(configuration, 'SHORT_DATE_FORMAT', 'Y-m-d')
TIME_FORMAT = getattr(configuration, 'TIME_FORMAT', 'g:i a')
SHORT_TIME_FORMAT = getattr(configuration, 'SHORT_TIME_FORMAT', 'H:i:s')
DATETIME_FORMAT = getattr(configuration, 'DATETIME_FORMAT', 'N j, Y g:i a')
SHORT_DATETIME_FORMAT = getattr(configuration, 'SHORT_DATETIME_FORMAT', 'Y-m-d H:i')
BANNER_TOP = getattr(configuration, 'BANNER_TOP', False)
BANNER_BOTTOM = getattr(configuration, 'BANNER_BOTTOM', False)
PREFER_IPV4 = getattr(configuration, 'PREFER_IPV4', False)
ENFORCE_GLOBAL_UNIQUE = getattr(configuration, 'ENFORCE_GLOBAL_UNIQUE', False)
CORS_ORIGIN_ALLOW_ALL = getattr(configuration, 'CORS_ORIGIN_ALLOW_ALL', False)
CORS_ORIGIN_WHITELIST = getattr(configuration, 'CORS_ORIGIN_WHITELIST', [])
CORS_ORIGIN_REGEX_WHITELIST = getattr(configuration, 'CORS_ORIGIN_REGEX_WHITELIST', [])
CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS

# Attempt to import LDAP configuration if it has been defined
LDAP_IGNORE_CERT_ERRORS = False
try:
    from netbox.ldap_config import *
    LDAP_CONFIGURED = True
except ImportError:
    LDAP_CONFIGURED = False

# LDAP configuration (optional)
if LDAP_CONFIGURED:
    try:
        import ldap
        import django_auth_ldap
        # Prepend LDAPBackend to the default ModelBackend
        AUTHENTICATION_BACKENDS = [
            'django_auth_ldap.backend.LDAPBackend',
            'django.contrib.auth.backends.ModelBackend',
        ]
        # Optionally disable strict certificate checking
        if LDAP_IGNORE_CERT_ERRORS:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        # Enable logging for django_auth_ldap
        logger = logging.getLogger('django_auth_ldap')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)
    except ImportError:
        raise ImproperlyConfigured(
            "LDAP authentication has been configured, but django-auth-ldap is not installed. You can remove "
            "netbox/ldap_config.py to disable LDAP."
        )

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database
configuration.DATABASE.update({'ENGINE': 'django.db.backends.postgresql'})
DATABASES = {
    'default': configuration.DATABASE,
}

# Email
EMAIL_HOST = EMAIL.get('SERVER')
EMAIL_PORT = EMAIL.get('PORT', 25)
EMAIL_HOST_USER = EMAIL.get('USERNAME')
EMAIL_HOST_PASSWORD = EMAIL.get('PASSWORD')
EMAIL_TIMEOUT = EMAIL.get('TIMEOUT', 10)
SERVER_EMAIL = EMAIL.get('FROM_EMAIL')
EMAIL_SUBJECT_PREFIX = '[NetBox] '

# Installed applications
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'corsheaders',
    'debug_toolbar',
    'django_filters',
    'django_tables2',
    'mptt',
    'rest_framework',
    'rest_framework_swagger',
    'circuits',
    'dcim',
    'ipam',
    'extras',
    'secrets',
    'tenancy',
    'users',
    'utilities',
)

# Middleware
MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'utilities.middleware.LoginRequiredMiddleware',
    'utilities.middleware.APIVersionMiddleware',
)

ROOT_URLCONF = 'netbox.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'utilities.context_processors.settings',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'netbox.wsgi.application'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Internationalization
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR + '/static/'
STATIC_URL = '/{}static/'.format(BASE_PATH)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "project-static"),
)

# Media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/{}media/'.format(BASE_PATH)

# Disable default limit of 1000 fields per request. Needed for bulk deletion of objects. (Added in Django 1.10.)
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# Authentication URLs
LOGIN_URL = '/{}login/'.format(BASE_PATH)

# Secrets
SECRETS_MIN_PUBKEY_SIZE = 2048

# Django REST framework (API)
REST_FRAMEWORK_VERSION = VERSION[0:3]  # Use major.minor as API version
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'utilities.api.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'utilities.api.TokenPermissions',
    ),
    'DEFAULT_VERSION': REST_FRAMEWORK_VERSION,
    'ALLOWED_VERSIONS': [REST_FRAMEWORK_VERSION],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'PAGE_SIZE': PAGINATE_COUNT,
}

# Django debug toolbar
# Disable the templates panel by default due to a performance issue in Django 1.11; see
# https://github.com/jazzband/django-debug-toolbar/issues/910
DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
    ],
}
INTERNAL_IPS = (
    '127.0.0.1',
    '::1',
)


try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'
