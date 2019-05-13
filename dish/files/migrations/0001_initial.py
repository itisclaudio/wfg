# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dish.files.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuisine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('othernames', models.CharField(max_length=100, verbose_name=b'Other names', blank=True)),
                ('territory', models.TextField(max_length=100, blank=True)),
                ('description', models.TextField(max_length=9500, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('urlname', models.CharField(max_length=80, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=75)),
                ('urlname', models.CharField(max_length=80)),
                ('othernames', models.CharField(max_length=100, verbose_name=b'Other names', blank=True)),
                ('ingredients', models.CharField(max_length=300, blank=True)),
                ('description', models.TextField(max_length=9500, blank=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('likestot', models.IntegerField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('cuisines', models.ManyToManyField(to='files.Cuisine', blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='DishSimilar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, null=True, blank=True)),
                ('dish1', models.ForeignKey(related_name='dish_origin', to='files.Dish')),
                ('dish2', models.ForeignKey(related_name='dish_similar', to='files.Dish')),
            ],
        ),
        migrations.CreateModel(
            name='EmailQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('username', models.CharField(max_length=30, null=True, blank=True)),
                ('action', models.CharField(max_length=30, null=True, blank=True)),
                ('object', models.CharField(max_length=30, null=True, blank=True)),
                ('url_plus', models.CharField(max_length=300, null=True, blank=True)),
                ('sent_flag', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='LikeDish',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('likes', models.BooleanField(default=True)),
                ('dish', models.ForeignKey(to='files.Dish')),
            ],
            options={
                'ordering': ('dish',),
            },
        ),
        migrations.CreateModel(
            name='LikeList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, null=True, blank=True)),
            ],
            options={
                'ordering': ('list',),
            },
        ),
        migrations.CreateModel(
            name='LikePicture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('likes', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=92, verbose_name=b'List name')),
                ('urlname', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=9500, blank=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('type', models.CharField(default=b'1', max_length=1, choices=[(b'1', b'Personal: Only owner can add dishes'), (b'2', b'Public: Users can add dishes'), (b'3', b'Private: Only owner can see it')])),
                ('private', models.BooleanField(default=False)),
                ('likestot', models.IntegerField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('-modified',),
            },
        ),
        migrations.CreateModel(
            name='ListDish',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(max_length=1990, blank=True)),
                ('index', models.IntegerField(null=True, blank=True)),
                ('dish', models.ForeignKey(to='files.Dish')),
                ('list', models.ForeignKey(to='files.List')),
            ],
            options={
                'ordering': ('list', 'index'),
            },
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('urlname', models.CharField(max_length=80, null=True, blank=True)),
                ('location', models.ImageField(upload_to=dish.files.models.picture_url)),
                ('comments', models.CharField(max_length=400, null=True, blank=True)),
                ('likestot', models.IntegerField(null=True, blank=True)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('ownit', models.BooleanField(default=True)),
                ('creditsname', models.CharField(max_length=100, null=True, blank=True)),
                ('creditsurl', models.CharField(max_length=2000, null=True, blank=True)),
                ('dish', models.ForeignKey(to='files.Dish')),
            ],
            options={
                'ordering': ('dish__name',),
            },
        ),
        migrations.CreateModel(
            name='userProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('photo', models.ImageField(null=True, upload_to=dish.files.models.generate_url, blank=True)),
                ('telefono', models.CharField(max_length=30, null=True, blank=True)),
                ('about', models.TextField(max_length=4000, null=True, blank=True)),
                ('pass_backup', models.CharField(max_length=30, null=True, blank=True)),
                ('uploads', models.IntegerField(null=True, blank=True)),
                ('names_show', models.BooleanField(default=True)),
                ('email_show', models.BooleanField(default=True)),
                ('only_social', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user__username',),
            },
        ),
        migrations.AddField(
            model_name='picture',
            name='owner',
            field=models.ForeignKey(to='files.userProfile'),
        ),
        migrations.AddField(
            model_name='picture',
            name='piclikes',
            field=models.ManyToManyField(related_name='piclikes', through='files.LikePicture', to='files.userProfile', blank=True),
        ),
        migrations.AddField(
            model_name='listdish',
            name='owner',
            field=models.ForeignKey(blank=True, to='files.userProfile', null=True),
        ),
        migrations.AddField(
            model_name='list',
            name='dishes',
            field=models.ManyToManyField(related_name='dishlist', through='files.ListDish', to='files.Dish', blank=True),
        ),
        migrations.AddField(
            model_name='list',
            name='listlikes',
            field=models.ManyToManyField(related_name='listlikes', through='files.LikeList', to='files.userProfile', blank=True),
        ),
        migrations.AddField(
            model_name='list',
            name='owner',
            field=models.ForeignKey(to='files.userProfile'),
        ),
        migrations.AddField(
            model_name='likepicture',
            name='picture',
            field=models.ForeignKey(to='files.Picture'),
        ),
        migrations.AddField(
            model_name='likepicture',
            name='profile',
            field=models.ForeignKey(to='files.userProfile'),
        ),
        migrations.AddField(
            model_name='likelist',
            name='list',
            field=models.ForeignKey(to='files.List'),
        ),
        migrations.AddField(
            model_name='likelist',
            name='profile',
            field=models.ForeignKey(to='files.userProfile'),
        ),
        migrations.AddField(
            model_name='likedish',
            name='profile',
            field=models.ForeignKey(to='files.userProfile'),
        ),
        migrations.AddField(
            model_name='dishsimilar',
            name='profile',
            field=models.ForeignKey(to='files.userProfile'),
        ),
        migrations.AddField(
            model_name='dish',
            name='dishlikes',
            field=models.ManyToManyField(related_name='dishlikes', through='files.LikeDish', to='files.userProfile', blank=True),
        ),
        migrations.AddField(
            model_name='dish',
            name='similar',
            field=models.ManyToManyField(related_name='similar_to', through='files.DishSimilar', to='files.Dish', blank=True),
        ),
        migrations.AddField(
            model_name='dish',
            name='similars',
            field=models.ManyToManyField(related_name='similars_rel_+', to='files.Dish', blank=True),
        ),
        migrations.AddField(
            model_name='dish',
            name='userprofile',
            field=models.ForeignKey(to='files.userProfile'),
        ),
        migrations.AddField(
            model_name='cuisine',
            name='owner',
            field=models.ForeignKey(to='files.userProfile', null=True),
        ),
    ]
