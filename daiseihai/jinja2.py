from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils.formats import date_format
from jinja2 import Environment


def dateformat(value) -> str:
    return date_format(value, format='DATE_FORMAT')


def url(viewname: str, *args, **kwargs) -> str:
    """Wrapper for Django's built-in reverse function."""
    return reverse(viewname, args=args, kwargs=kwargs)


def environment(**options) -> Environment:
    """Generate an environment for Jinja2."""
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': url,
        'daiseihai': {
            'release': settings.RAVEN_CONFIG['release'] or ''
        }
    })
    env.filters['dateformat'] = dateformat
    return env
