# Generated by Django 2.0.7 on 2019-01-12 19:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0005_matchup_spoiler'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='matchup',
            unique_together={('video', 'order')},
        ),
    ]