import datetime

from django.db.models import Count, F, Prefetch, Q, Window
from django.db.models.functions import RowNumber
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, View
from django.views.generic.list import MultipleObjectMixin

from daiseihai.archive import models


class VideoViewMixin():
    def get_context_data(self, **kwargs):
        """Include `videos` in context."""
        context = super().get_context_data(**kwargs)
        context['videos'] = self.get_videos()
        return context

    def get_videos(self):
        """Return all visible videos with their associated matchups and teams."""
        matchups = models.Matchup.objects.select_related('home', 'away').all()
        matchup_prefetch = Prefetch('matchups', queryset=matchups)
        return models.Video.objects.prefetch_related(matchup_prefetch)\
                                   .filter(is_visible=True)


class TeamDetailView(VideoViewMixin, DetailView):
    model = models.Team

    def get_videos(self):
        queryset = super().get_videos()
        team_filter = Q(matchups__home=self.object) | Q(matchups__away=self.object)
        return queryset.select_related('tournament')\
                       .filter(team_filter).reverse().distinct()


class TeamListView(ListView):
    model = models.Team

    def get_queryset(self):
        video_count = Count('home_games') + Count('away_games')
        return self.model.objects.annotate(video_count=video_count)\
                                 .filter(video_count__gt=0)


class TournamentDetailView(VideoViewMixin, DetailView):
    model = models.Tournament

    def get_videos(self):
        queryset = super().get_videos()
        part = Window(expression=RowNumber(), partition_by=F('date'),
                      order_by=('date', 'order'))
        part_count = Window(expression=Count('*'), partition_by=F('date'))
        return queryset.filter(tournament=self.object)\
                       .annotate(part=part, part_count=part_count)


class TournamentListView(ListView):
    model = models.Tournament

    def get_queryset(self):
        """Return all visible tournaments."""
        video_count = Count('videos', filter=Q(videos__is_visible=True))
        return self.model.objects.annotate(video_count=video_count)\
                                 .filter(video_count__gt=0)


class LegacyVideoRedirectView(RedirectView):
    """Conversion view for old video page URLs."""

    query_string = True
    pattern_name = "video_detail"

    def get_redirect_url(self, *args, **kwargs):
        video = get_object_or_404(
            models.Video.objects.select_related("tournament"), pk=kwargs.pop("pk")
        )
        kwargs.update(slug=video.tournament.slug, date=video.date.isoformat())
        same_day_videos = models.Video.objects.filter(
            tournament=video.tournament, date=video.date
        )
        if video.order != 1 or same_day_videos.count() > 1:
            kwargs["order"] = video.order
            self.pattern_name = "video_detail_order"
        return super().get_redirect_url(*args, **kwargs)


class VideoView(DetailView):
    model = models.Video

    def get_object(self, queryset=None):
        date = datetime.date.fromisoformat(self.kwargs["date"])
        order = int(self.kwargs.get("order", 1))
        return get_object_or_404(
            self.model, date=date, order=order, tournament__slug=self.kwargs["slug"]
        )
