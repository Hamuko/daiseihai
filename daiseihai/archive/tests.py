from datetime import date

from django.test import TestCase

from daiseihai.archive import constants, factories


class TournamentTestCase(TestCase):
    def create_videos(self, count, *args, **kwargs):
        """Create a `count` amount of videos and return the instances as a list."""
        videos = []
        for _ in range(count):
            video = factories.VideoFactory(*args, **kwargs)
            videos.append(video)
        return videos

    def test_team_detail(self):
        """Test that team detail pages contain home and away matches for that team and
        that team alone.
        """
        team1 = factories.TeamFactory(name='/a/', slug='a')
        team2 = factories.TeamFactory(name='/u/', slug='u')
        team3 = factories.TeamFactory(name='/gd/', slug='gd')
        video1 = factories.VideoFactory(date=date(2018, 7, 27))
        video2 = factories.VideoFactory(date=date(2018, 7, 28))
        video3 = factories.VideoFactory(date=date(2018, 7, 29))
        factories.MatchupFactory(video=video1, home=team1, away=team2)
        factories.MatchupFactory(video=video2, home=team3, away=team1)
        factories.MatchupFactory(video=video3, home=team2, away=team3)

        response = self.client.get('/team/%s/' % team1.slug)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'July 27, 2018')
        self.assertContains(response, 'July 28, 2018')
        self.assertNotContains(response, 'July 29, 2018')

    def test_team_list(self):
        """Test that only teams with videos are visible in the team listing."""
        team1 = factories.TeamFactory(name='/a/', slug='a')
        team2 = factories.TeamFactory(name='/u/', slug='u')
        team3 = factories.TeamFactory(name='/gd/', slug='gd')
        factories.MatchupFactory(home=team1)
        factories.MatchupFactory(away=team2)

        response = self.client.get('/teams/')
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, team1.name)
        self.assertContains(response, team2.name)
        self.assertNotContains(response, team3.name)

    def test_tournament_detail(self):
        """Test that tournament detail pages load and contain properly formatted dates."""
        tournament = factories.TournamentFactory()
        factories.VideoFactory(tournament=tournament, date=date(2018, 7, 27), order=1)
        factories.VideoFactory(tournament=tournament, date=date(2018, 7, 28), order=1)
        factories.VideoFactory(tournament=tournament, date=date(2018, 7, 28), order=2)
        factories.VideoFactory(tournament=tournament, date=date(2018, 7, 29),
                               order=1, is_visible=False)

        response = self.client.get('/%s/' % tournament.slug)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'July 27, 2018', html=True)
        self.assertNotContains(response, 'July 27, 2018 (', html=True)
        self.assertContains(response, 'July 28, 2018 (1/2)', html=True)
        self.assertContains(response, 'July 28, 2018 (2/2)', html=True)
        self.assertNotContains(response, 'July 29, 2018', html=True)

    def test_tournament_detail_singles(self):
        """Test that tournament detail pages with single videos loads properly."""
        team1 = factories.TeamFactory(name='/llsifg/', slug='llsifg')
        team2 = factories.TeamFactory(name='/vitagen/', slug='vitagen')
        team3 = factories.TeamFactory(name='/drg/', slug='drg')
        team4 = factories.TeamFactory(name='/feg/', slug='feg')
        tournament = factories.TournamentFactory()
        video1 = factories.VideoFactory(tournament=tournament,
                                        type=constants.VIDEO_TYPE_SINGLE,
                                        date=date(2018, 7, 27), order=1)
        video2 = factories.VideoFactory(tournament=tournament,
                                        type=constants.VIDEO_TYPE_SINGLE,
                                        date=date(2018, 7, 28), order=1)
        factories.MatchupFactory(video=video1, home=team1, away=team2)
        factories.MatchupFactory(video=video2, home=team3, away=team4)

        response = self.client.get('/%s/' % tournament.slug)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, '/llsifg/ – /vitagen/')
        self.assertContains(response, '/drg/ – /feg/')
        self.assertContains(response, 'implyingrigged', 4)

    def test_tournament_list(self):
        """Test that only tournaments with visible videos are shown in the listing."""
        tournament1 = factories.TournamentFactory()
        self.create_videos(3, tournament=tournament1)
        tournament2 = factories.TournamentFactory()
        self.create_videos(1, tournament=tournament2)
        tournament3 = factories.TournamentFactory()
        self.create_videos(2, tournament=tournament2, is_visible=False)
        tournament4 = factories.TournamentFactory()

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, tournament1.name)
        self.assertContains(response, '3 videos')
        self.assertContains(response, tournament2.name)
        self.assertContains(response, '1 video')
        self.assertNotContains(response, tournament3.name)
        self.assertNotContains(response, tournament4.name)

    def test_video_bookmark(self):
        """Test that video bookmarks contain correct timestamps and in correct position
        order.
        """
        video = factories.VideoFactory()
        factories.VideoBookmarkFactory(video=video, name='/a/ - /u/',
                                       position='00:13:29.132')
        factories.VideoBookmarkFactory(video=video, name='Draw',
                                       position='05:06:34.948')
        factories.VideoBookmarkFactory(video=video, name='/ck/ - /gd/',
                                       position='01:38:12.160')

        response = self.client.get('/video/%d/bookmarks/' % video.pk)
        self.assertEqual(response.status_code, 200)

        content = response.json()
        self.assertEqual(len(content), 3)
        self.assertEqual(content[0]['name'], '/a/ - /u/')
        self.assertEqual(content[0]['position'], 13 * 60 + 29.132)
        self.assertEqual(content[1]['name'], '/ck/ - /gd/')
        self.assertEqual(content[1]['position'], (1 * 60 + 38) * 60 + 12.160)
        self.assertEqual(content[2]['name'], 'Draw')
        self.assertEqual(content[2]['position'], (5 * 60 + 6) * 60 + 34.948)

    def test_video_bookmark_empty(self):
        """Test bookmarks when the video has none."""
        video = factories.VideoFactory()

        response = self.client.get('/video/%d/bookmarks/' % video.pk)
        self.assertEqual(response.status_code, 200)

        content = response.json()
        self.assertEqual(len(content), 0)

    def test_video_bookmark_404(self):
        """Test bookmarks when the video does not exist."""
        response = self.client.get('/video/%d/bookmarks/' % 9183)
        self.assertEqual(response.status_code, 200)

        content = response.json()
        self.assertEqual(len(content), 0)
