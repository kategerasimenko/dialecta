# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-07 10:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('normalization', '0003_remove_model_recordings'),
        ('corpora', '0007_auto_20170707_0939'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='model_to_normalize',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='normalization.Model'),
        ),
    ]
