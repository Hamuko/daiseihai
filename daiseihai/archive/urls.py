from django.urls import path

from daiseihai.archive import views

urlpatterns = [
    path('',
         views.TournamentListView.as_view(), name='index'),
    path('team/<slug>',
         views.TeamDetailView.as_view(), name='team_detail'),
    path('teams/',
         views.TeamListView.as_view(), name='team_list'),
    path('<slug>/',
         views.TournamentDetailView.as_view(), name='tournament'),
    path('video/<int:pk>/bookmarks/',
         views.VideoBookmarkView.as_view(), name='video_bookmarks'),
]
