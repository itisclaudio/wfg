# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0002_auto_20180501_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='othernames',
            field=models.CharField(max_length=200, verbose_name=b'Other names', blank=True),
        ),
        migrations.AlterField(
            model_name='list',
            name='name',
            field=models.CharField(max_length=92, verbose_name=b'List title'),
        ),
    ]
