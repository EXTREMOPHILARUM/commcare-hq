# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-02 15:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('couchforms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='unfinishedsubmissionstub',
            name='attempts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='unfinishedsubmissionstub',
            name='date_queued',
            field=models.DateTimeField(db_index=True, null=True),
        ),
    ]
