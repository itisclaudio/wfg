# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0007_remove_searchlog_search'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchlog',
            name='searchwords',
            field=models.TextField(max_length=99, blank=True),
        ),
    ]
