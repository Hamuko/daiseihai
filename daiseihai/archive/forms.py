from django import forms

from daiseihai.archive import models


class VideoForm(forms.ModelForm):
    sync_help_chat_timestamp = forms.IntegerField(
        required=False,
        localize=True,
        label='Chat timestamp'
    )
    sync_help_video_timestamp = forms.DurationField(
        required=False,
        label='Video timestamp'
    )

    def clean(self):
        cleaned_data = super().clean()

        # Set the chat start timestamp from sync helper values.
        if cleaned_data.get('chat_start', None) is None:
            sync_chat_timestamp = cleaned_data.get('sync_help_chat_timestamp')
            sync_video_timestamp = cleaned_data.get('sync_help_video_timestamp')
            if sync_chat_timestamp and sync_video_timestamp:
                chat_start_offset = int(sync_video_timestamp.total_seconds() * 1000)
                cleaned_data['chat_start'] = sync_chat_timestamp - chat_start_offset

        return cleaned_data

    class Meta:
        model = models.Video
        exclude = ('duration', )
        labels = {
            'url': 'URL',
        }
