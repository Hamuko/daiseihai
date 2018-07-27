from urllib.parse import urljoin
import os.path

from django.conf import settings
from django.db import models

from daiseihai.fields import ColorField


def _get_tournament_logo_path(instance, filename):
    """Save tournament logos in `MEDIA_ROOT/logos/slug.ext`."""
    _, extension = os.path.splitext(filename)
    return f'logos/{instance.slug}{extension}'


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    logo = models.ImageField(upload_to=_get_tournament_logo_path)

    def __str__(self):
        return f'{self.name} ({self.slug})'

    class Meta:
        ordering = ('-start_date', )


class Team(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    main_color = ColorField(default='#000000')
    secondary_color = ColorField(default='#ffffff')
    long_name = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def style(self) -> str:
        """Returns the team colors as CSS style string."""
        return f'background-color: {self.main_color}; color: {self.secondary_color};'

    class Meta:
        ordering = ('slug', )


class Video(models.Model):
    tournament = models.ForeignKey(Tournament, related_name='videos',
                                   on_delete=models.PROTECT)
    date = models.DateField()
    order = models.PositiveSmallIntegerField(default=1)
    filename = models.CharField(null=True, blank=True, max_length=200)
    url = models.CharField(null=True, blank=True, max_length=200)
    duration = models.PositiveIntegerField(null=True, blank=True)
    is_visible = models.BooleanField(default=True)

    @property
    def link(self) -> str:
        """Return download link for the video."""
        if self.url:
            return self.url
        return urljoin(settings.VIDEO_URL, self.filename)

    class Meta:
        ordering = ('date', 'order')
        unique_together = ('date', 'order')


class Matchup(models.Model):
    video = models.ForeignKey(Video, related_name='matchups', on_delete=models.CASCADE)
    home = models.ForeignKey(Team, related_name='home_games', on_delete=models.CASCADE)
    away = models.ForeignKey(Team, related_name='away_games', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ('order', )
        unique_together = [('video', 'home', 'away'), ('video', 'order')]


class VideoBookmark(models.Model):
    video = models.ForeignKey(Video, related_name='bookmarks', on_delete=models.CASCADE)
    position = models.DurationField()
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ('position', )
