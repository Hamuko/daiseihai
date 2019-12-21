from django.contrib import admin

from daiseihai.archive import forms, models


class MatchupInline(admin.TabularInline):
    model = models.Matchup


class VideoBookmarkInline(admin.TabularInline):
    model = models.VideoBookmark


class VideoAdmin(admin.ModelAdmin):
    inlines = [MatchupInline, VideoBookmarkInline]  
    form = forms.VideoForm
    fieldsets = (
        (None, {
            'fields': (
                'type',
                'tournament',
                ('date', 'order'),
                ('filename', 'url', 'intro_url'),
                'is_visible',
                'chat',
                ('chat_start', 'sync_help_video_timestamp', 'sync_help_chat_timestamp'),
            )
        }),
    )


admin.site.register(models.Chat)
admin.site.register(models.League)
admin.site.register(models.Team)
admin.site.register(models.Tournament)
admin.site.register(models.Video, VideoAdmin)
