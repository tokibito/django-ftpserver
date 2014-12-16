# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FTPUserAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('last_login', models.DateTimeField(editable=False, verbose_name='Last login', null=True)),
                ('home_dir', models.CharField(max_length=1024, verbose_name='Home directory', blank=True, null=True)),
            ],
            options={
                'verbose_name': 'FTP user account',
                'verbose_name_plural': 'FTP user accounts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FTPUserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=30, verbose_name='Group name')),
                ('permission', models.CharField(default='elradfmw', max_length=8, verbose_name='Permission')),
                ('home_dir', models.CharField(max_length=1024, verbose_name='Home directory', blank=True, null=True)),
            ],
            options={
                'verbose_name': 'FTP user group',
                'verbose_name_plural': 'FTP user groups',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ftpuseraccount',
            name='group',
            field=models.ForeignKey(to='django_ftpserver.FTPUserGroup', verbose_name='FTP user group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ftpuseraccount',
            name='user',
            field=models.OneToOneField(verbose_name='User', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
