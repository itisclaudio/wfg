# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0004_auto_20180830_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='dish',
            name='photo_main',
            field=models.CharField(max_length=80, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='dish',
            name='likestot',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='feature',
            name='count',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='list',
            name='likestot',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='picture',
            name='likestot',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
    ]
