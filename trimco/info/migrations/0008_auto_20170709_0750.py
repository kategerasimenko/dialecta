# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-09 07:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0007_auto_20160617_1229'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='speaker',
            options={'ordering': ['string_id']},
        ),
    ]
