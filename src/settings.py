
from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
     # Our Apps
    'users',
    'products',
    'categories',
    'cart',
    'wishlist',
    'orders',
    'payments',
    'reviews',

    # Third Party
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_spectacular',
    'corsheaders',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'src.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Settings

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# REST Framework Authentication Settings

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    # OpenAPI / Swagger
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

}
# API Documentation Settings

SPECTACULAR_SETTINGS = {
    'TITLE': 'CommerceHub API',
    'DESCRIPTION': 'Production-ready E-Commerce REST API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    'COMPONENT_SPLIT_REQUEST': True,

    'ENUM_NAME_OVERRIDES': {
        'OrderStatusEnum': [
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('PROCESSING', 'Processing'),
            ('SHIPPED', 'Shipped'),
            ('DELIVERED', 'Delivered'),
            ('CANCELLED', 'Cancelled'),
        ],
        'PaymentStatusEnum': [
            ('PENDING', 'Pending'),
            ('SUCCESS', 'Success'),
            ('FAILED', 'Failed'),
            ('REFUNDED', 'Refunded'),
        ],
    },

    'TAGS': [
        {
            'name': 'Authentication & Users',
            'description': 'User registration, authentication, email verification, profile and password management.',
        },
        {
            'name': 'Categories',
            'description': 'Product category management.',
        },
        {
            'name': 'Products',
            'description': 'Product management and product discovery.',
        },
        {
            'name': 'Wishlist',
            'description': 'Customer wishlist management.',
        },
        {
            'name': 'Cart',
            'description': 'Shopping cart management.',
        },
        {
            'name': 'Orders',
            'description': 'Order creation, management and order history.',
        },
        {
            'name': 'Payments',
            'description': 'Payment processing and payment management.',
        },
        {
            'name': 'Reviews',
            'description': 'Product reviews and ratings.',
        },
    ],
}
# JWT Settings

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# Media Settings

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

AUTH_USER_MODEL = 'users.CustomUser'

CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:6381/0"
)

CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6381/0"
)

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Dhaka"