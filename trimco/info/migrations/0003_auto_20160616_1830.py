# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-16 16:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0002_auto_20160615_2254'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='languagerelation',
            options={'verbose_name_plural': 'Linguistic Biography'},
        ),
        migrations.AlterModelOptions(
            name='locationrelation',
            options={'verbose_name_plural': 'Geography of Life'},
        ),
        migrations.AlterField(
            model_name='speaker',
            name='sex',
            field=models.CharField(choices=[('m', 'Male'), ('f', 'Female'), ('u', 'Unspecified')], max_length=1),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='string_id',
            field=models.CharField(max_length=10, verbose_name='Speaker ID'),
        ),
    ]
