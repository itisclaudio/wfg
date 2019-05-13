# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0006_searchlog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='searchlog',
            name='search',
        ),
    ]
