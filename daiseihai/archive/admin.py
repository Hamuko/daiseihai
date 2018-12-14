from django.contrib import admin

from daiseihai.archive import models


class MatchupInline(admin.TabularInline):
    model = models.Matchup


class VideoBookmarkInline(admin.TabularInline):
    model = models.VideoBookmark


class VideoAdmin(admin.ModelAdmin):
    inlines = [MatchupInline, VideoBookmarkInline]
    exclude = ('duration', )


admin.site.register(models.Chat)
admin.site.register(models.League)
admin.site.register(models.Team)
admin.site.register(models.Tournament)
admin.site.register(models.Video, VideoAdmin)
