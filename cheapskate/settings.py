# Django settings for betheshoe project.

import os
PROJECT_ROOT = os.path.abspath(__file__).replace('\\','/').split('/')
SITE = PROJECT_ROOT[len(PROJECT_ROOT)-2]
PROJECT_ROOT = "/".join(PROJECT_ROOT[:-1])+"/"

# Special site configs

import sys
DEBUG = False
if 'runserver' in sys.argv:
    DEBUG = True
    TEMPLATE_DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Jason Goldstein', 'jason@betheshoe.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': SITE,                      # Or path to database file if using sqlite3.
        'USER': 'jason',                      # Not used with sqlite3.
        'PASSWORD': 'X.rvnos1',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

ALLOWED_HOSTS = [
    "cb.whatisjasongoldstein.com",
]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/admin/media/'

sys.path.append(PROJECT_ROOT+'/apps')
STATIC_ROOT = '%sstatic/' % PROJECT_ROOT
MEDIA_ROOT = '%smedia/' % PROJECT_ROOT


# Additional locations of static files
# STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
# )

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 's9v(^q-rbeu4@)5stkugdju9$lp=j0i+0=0t-eqnwan^b3eh5e'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    )
# if not LOCAL:
#     MIDDLEWARE_CLASSES += (
#         'johnny.middleware.LocalStoreClearMiddleware',
#         'johnny.middleware.QueryCacheMiddleware',
#     )

ROOT_URLCONF = '%s.urls' % SITE


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'cheapskate',
    'south',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


EMAIL_HOST=os.environ['BETHESHOE_EMAIL_HOST']
EMAIL_HOST_USER=os.environ['BETHESHOE_EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD=os.environ['BETHESHOE_EMAIL_HOST_PASSWORD']
EMAIL_PORT=587
DEFAULT_FROM_EMAIL = os.environ['BETHESHOE_DEFAULT_FROM_EMAIL']
SERVER_EMAIL = os.environ['BETHESHOE_SERVER_EMAIL']
EMAIL_USE_TLS=True

# # some johnny settings
# CACHES = {
#     'default' : dict(
#         BACKEND = 'johnny.backends.filebased.FileBasedCache',
#         # LOCATION = ['127.0.0.1:11211'],
#         LOCATION = '%s/cache' % ENV_DIR,
#         JOHNNY_CACHE = True,
#     )
# }
# JOHNNY_MIDDLEWARE_KEY_PREFIX='jc_%s' % SITE
