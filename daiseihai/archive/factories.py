import datetime
import factory

from daiseihai.archive import models


class TournamentFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: '4chan Summer Cup {0}'.format(n + 2000))
    slug = factory.Sequence(lambda n: 'summer-cup-{0}'.format(n + 2000))
    start_date = factory.Sequence(lambda n: datetime.date(n + 2000, 7, 27))
    end_date = factory.Sequence(lambda n: datetime.date(n + 2000, 8, 12))
    logo = factory.django.ImageField(filename='tournament.png')

    class Meta:
        model = models.Tournament


class TeamFactory(factory.DjangoModelFactory):
    name = '/ck/'
    slug = factory.Sequence(lambda n: 'ck-{0}'.format(n))
    main_color = '#000000'
    secondary_color = '#ffffff'
    long_name = False

    class Meta:
        model = models.Team


class VideoFactory(factory.DjangoModelFactory):
    tournament = factory.SubFactory(TournamentFactory)
    date = factory.Sequence(
        lambda n: datetime.date(2018, 7, 27) + datetime.timedelta(days=n)
    )
    order = factory.Sequence(lambda n: n)
    filename = factory.Sequence(lambda n: '4cc20180727-{0}.mp4'.format(n))
    is_visible = True

    class Meta:
        model = models.Video


class MatchupFactory(factory.DjangoModelFactory):
    video = factory.SubFactory(VideoFactory)
    home = factory.SubFactory(TeamFactory)
    away = factory.SubFactory(TeamFactory)
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = models.Matchup


class VideoBookmarkFactory(factory.DjangoModelFactory):
    video = factory.SubFactory(VideoFactory)
    position = '0'
    name = '/a/ - /ck/'

    class Meta:
        model = models.VideoBookmark
