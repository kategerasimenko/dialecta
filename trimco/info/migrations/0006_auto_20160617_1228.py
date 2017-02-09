# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-17 10:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0005_auto_20160616_1952'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dialect',
            name='to_language',
        ),
        migrations.RemoveField(
            model_name='languagerelation',
            name='to_language',
        ),
        migrations.RemoveField(
            model_name='languagerelation',
            name='to_speaker',
        ),
        migrations.RemoveField(
            model_name='speaker',
            name='languages',
        ),
        migrations.DeleteModel(
            name='Dialect',
        ),
        migrations.DeleteModel(
            name='Language',
        ),
        migrations.DeleteModel(
            name='LanguageRelation',
        ),
    ]