# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0009_remove_searchlog_foodie'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchlog',
            name='foodie',
            field=models.ForeignKey(blank=True, to='files.userProfile', null=True),
        ),
    ]
