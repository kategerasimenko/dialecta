# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-07 09:39
from __future__ import unicode_literals

import corpora.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corpora', '0006_recording_to_dialect'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recording',
            name='data',
            field=models.FileField(blank=True, null=True, storage=corpora.models.OverwriteStorage(), upload_to='', verbose_name='Transcription'),
        ),
    ]
