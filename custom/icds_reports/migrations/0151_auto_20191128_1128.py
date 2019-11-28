# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-11-28 11:28
from __future__ import unicode_literals

import custom.icds_reports.models.aggregate
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports', '0150_update_agg_awc_monthly_view'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardUserActivityReport',
            fields=[
                ('username', models.TextField(primary_key=True, serialize=False)),
                ('state_id', models.TextField(null=True)),
                ('district_id', models.TextField(null=True)),
                ('block_id', models.TextField(null=True)),
                ('user_level', models.IntegerField(null=True)),
                ('location_launched', models.NullBooleanField()),
                ('last_activity', models.DateTimeField(help_text='The latest time dashboard user used dashboard', null=True)),
                ('date', models.DateField(null=True)),
            ],
            options={
                'db_table': 'dashboard_user_activity',
            },
            bases=(models.Model, custom.icds_reports.models.aggregate.AggregateMixin),
        ),
        migrations.AlterUniqueTogether(
            name='dashboarduseractivityreport',
            unique_together=set([('username', 'date')]),
        ),
    ]
