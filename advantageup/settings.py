"""
Django settings for advantage project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
#new comment
import os
import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (os.environ.get('DEBUG_VALUE') == 'True')


DEBUG_PROPAGATE_EXCEPTIONS = (os.environ.get('DEBUG_PROPAGATE_EXCEPTIONS') == 'True')

ALLOWED_HOSTS = ['app.advantageup.com', 'staging.advantageup.com']

DJANGO_TWILIO_FORGERY_PROTECTION = (os.environ.get('DJANGO_TWILIO_FORGERY_PROTECTION') == 'True')

PHONE_TYPE_LOOKUP = (os.environ.get('PHONE_TYPE_LOOKUP') == 'True')

REBRANDLY_API_KEY = os.environ.get('REBRANDLY_API_KEY')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'companies.apps.CompaniesConfig',
    'memberships.apps.MembershipsConfig',
    'stores.apps.StoresConfig',
    'shops.apps.ShopsConfig',
    'accounts.apps.AccountsConfig',
    'findphonenum.apps.FindphonenumConfig',
    'smsapp.apps.SmsappConfig',
    'sendreview.apps.SendreviewConfig',
    'dashboard.apps.DashboardConfig',
    'support.apps.SupportConfig',
    'audiences.apps.AudiencesConfig',
    'campaigns.apps.CampaignsConfig',
    'links.apps.LinksConfig',

    'tz_detect',
    'crispy_forms',
    'django_twilio',
    'import_export',
    'storages',
    'django_celery_beat',
    'sendgrid',
    'captcha',
]

AUTH_USER_MODEL = 'accounts.User' #changes the built-in user model to ours

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tz_detect.middleware.TimezoneMiddleware',  
]



ROOT_URLCONF = 'advantageup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'advantageup.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nnew_advup_dev',
        'USER': 'postgres',
        'PASSWORD': os.environ.get('DEV_DB_PASS'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
VENV_PATH = os.path.dirname(BASE_DIR)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


CRISPY_TEMPLATE_PACK = 'bootstrap4'

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
VOICE_SID = os.environ.get('VOICE_SID')

STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

LOGIN_URL = '/login/'

# SendGrid Settings
SEND_GRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

VONAGE_API_KEY = os.environ.get('VONAGE_API_KEY')
VONAGE_SECRET_KEY = os.environ.get('VONAGE_SECRET_KEY')

GOOGLE_PLACES_KEY = os.environ.get('GOOGLE_PLACES_KEY')

MAIN_URL = os.environ.get('MAIN_URL')
PHONE_PURCHASING_ON = (os.environ.get('PHONE_PURCHASING_ON') == 'True')

ENCODED_GOOGLE_JSON = os.environ.get('ENCODED_GOOGLE_JSON')

NEW_REG_EMAIL_AND_SHEET = (os.environ.get('NEW_REG_EMAIL_AND_SHEET') == 'True')

SECURE_SSL_REDIRECT = (os.environ.get('SECURE_SSL_REDIRECT') == 'True')

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CELERY_IGNORE_RESULT=True


CELERY_BROKER_POOL_LIMIT = None # Will decrease connection usage
CELERY_BROKER_HEARTBEAT = None # We're using TCP keep-alive instead
CELERY_BROKER_CONNECTION_TIMEOUT = 30 # May require a long timeout due to Linux DNS timeouts etc
CELERY_RESULT_BACKEND = None # AMQP is not recommended as result backend as it creates thousands of queues
CELERY_EVENT_QUEUE_EXPIRES = 60 # Will delete all celeryev. queues without consumers after 1 minute.
CELERY_WORKER_PREFETCH_MULTIPLIER = 1 # Disable prefetching, it's causes problems and doesn't help performance
CELERY_WORKER_CONCURRENCY = 50 # If you tasks are CPU bound, then limit to the number of cores, otherwise increase substainally

#Redis settings
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
 

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_REGION_NAME = 'us-east-2' #change to your region
AWS_S3_SIGNATURE_VERSION = 's3v4'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

django_heroku.settings(locals())

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'