from django.urls import path, re_path

from daiseihai.archive import views

urlpatterns = [
    path('',
         views.TournamentListView.as_view(), name='index'),
    path('team/<slug>/',
         views.TeamDetailView.as_view(), name='team_detail'),
    path('teams/',
         views.TeamListView.as_view(), name='team_list'),
    path('<slug>/',
         views.TournamentDetailView.as_view(), name='tournament'),
    path('video/<int:pk>/',
         views.LegacyVideoRedirectView.as_view(), name='legacy_video_detail'),
    re_path(r'video/(?P<slug>[\w-]+)/(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<order>[0-9]+)/',
         views.VideoView.as_view(), name='video_detail_order'),
    re_path(r'video/(?P<slug>[\w-]+)/(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})/',
         views.VideoView.as_view(), name='video_detail'),
]
