# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0010_searchlog_foodie'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchlog',
            name='search_origin',
            field=models.CharField(max_length=300, null=True, blank=True),
        ),
    ]
