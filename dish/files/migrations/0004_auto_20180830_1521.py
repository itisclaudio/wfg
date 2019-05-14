# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0003_auto_20180510_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=9500, blank=True)),
                ('icon', models.CharField(max_length=30, blank=True)),
                ('count', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='dish',
            name='features',
            field=models.ManyToManyField(to='files.Feature', blank=True),
        ),
    ]
