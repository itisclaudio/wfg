# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0005_auto_20181211_1421'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('search', models.TextField(max_length=99, blank=True)),
                ('foodie', models.CharField(max_length=30, null=True, blank=True)),
            ],
        ),
    ]
