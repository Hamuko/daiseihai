from urllib.parse import urljoin
import os.path
import uuid

from django.conf import settings
from django.db import models

from daiseihai.archive import constants
from daiseihai.fields import ColorField
from daiseihai.storage import OverwriteStorage


def _get_chat_file_path(instance, filename):
    """Save chat files in `MEDIA_ROOT/chats/UUID4.ext`."""
    _, extension = os.path.splitext(filename)
    return f'chats/{instance.id}{extension}'


def _get_tournament_logo_path(instance, filename):
    """Save tournament logos in `MEDIA_ROOT/logos/slug.ext`."""
    _, extension = os.path.splitext(filename)
    return f'logos/{instance.slug}{extension}'


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    file = models.FileField(storage=OverwriteStorage(),
                            upload_to=_get_chat_file_path)

    def __str__(self):
        return f'{self.date} ({self.id})'

    @property
    def url(self):
        return self.file.url

    class Meta:
        ordering = ('-date', )


class League(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    @property
    def metadata_url(self):
        print(settings.MEDIA_URL)
        return urljoin(settings.MEDIA_URL, f'metadata/{self.slug}.json')

    def __str__(self):
        return self.name


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    logo = models.ImageField(storage=OverwriteStorage(),
                             upload_to=_get_tournament_logo_path)
    league = models.ForeignKey(League, related_name='tournaments',
                               on_delete=models.PROTECT, null=True)

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
    def logo_image(self) -> str:
        """Returns the URL for the team's current logo on the wiki."""
        name = self.name.replace('/', '')
        return f'https://implyingrigged.info/wiki/Special:Redirect/file/{name}_logo.png'

    @property
    def style(self) -> str:
        """Returns the team colors as CSS style string."""
        return f'background-color: {self.main_color}; color: {self.secondary_color};'

    class Meta:
        ordering = ('slug', )


class Video(models.Model):
    type = models.IntegerField(choices=constants.VIDEO_TYPE_CHOICES,
                               default=constants.VIDEO_TYPE_NORMAL)
    tournament = models.ForeignKey(Tournament, related_name='videos',
                                   on_delete=models.PROTECT)
    date = models.DateField()
    order = models.PositiveSmallIntegerField(default=1)
    filename = models.CharField(null=True, blank=True, max_length=200)
    url = models.CharField(null=True, blank=True, max_length=200)
    intro_url = models.CharField(null=True, blank=True, max_length=200)
    duration = models.PositiveIntegerField(null=True, blank=True)
    is_visible = models.BooleanField(default=True)

    chat = models.ForeignKey(Chat, related_name='+', on_delete=models.PROTECT,
                             null=True, blank=True)
    chat_start = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.tournament.slug}, {self.date} ({self.order})'

    @property
    def has_chat(self) -> bool:
        """Video has an usable chat attached to it."""
        return self.chat and (self.chat_start or 0) > 0

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
