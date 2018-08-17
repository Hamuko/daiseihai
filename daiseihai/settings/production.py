from daiseihai.settings.shared import *

DEBUG = False

ALLOWED_HOSTS = ['bootleg.hamuko.moe']

RAVEN_CONFIG['dsn'] = secrets.RAVEN_DSN

STATIC_ROOT = '/srv/www/bootleg.hamuko.moe/html/static/'
MEDIA_ROOT = '/srv/www/bootleg.hamuko.moe/html/media/'

VIDEO_URL = 'https://bootleg.hamuko.moe/videos/'
