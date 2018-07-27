from django.db.models import Count, F, Prefetch, Q, Window
from django.db.models.functions import RowNumber
from django.http import Http404, JsonResponse
from django.views.generic import DetailView, ListView, View
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
        return queryset.select_related('tournament').filter(team_filter).reverse()


class TeamListView(ListView):
    model = models.Team

    def get_queryset(self):
        video_count = Count('home_games') + Count('away_games')
        return self.model.objects.annotate(video_count=video_count).filter(video_count__gt=-1)


class TournamentDetailView(VideoViewMixin, DetailView):
    model = models.Tournament

    def get_videos(self):
        queryset = super().get_videos()
        part = Window(expression=RowNumber(), partition_by=F('date'), order_by=('date', ))
        part_count = Window(expression=Count('*'), partition_by=F('date'))
        return queryset.filter(tournament=self.object)\
                       .annotate(part=part, part_count=part_count)


class TournamentListView(ListView):
    model = models.Tournament

    def get_queryset(self):
        """Return all visible tournaments."""
        return self.model.objects.annotate(video_count=Count('videos'))\
                                 .filter(video_count__gt=0)


class VideoBookmarkView(MultipleObjectMixin, View):
    model = models.VideoBookmark

    def get(self, request, *args, **kwargs):
        values = list(map(self.get_bookmark_dict, self.get_queryset()))
        return JsonResponse(list(values), safe=False)

    @staticmethod
    def get_bookmark_dict(bookmark):
        return {'position': bookmark.position.total_seconds(), 'name': bookmark.name}

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return self.model.objects.filter(video_id=pk)
