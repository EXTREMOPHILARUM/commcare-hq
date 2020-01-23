# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-01-23 07:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports', '0163_update_agg_awc_monthly_view'),
    ]

    operations = [
        migrations.AddField(
            model_name='agggovernancedashboard',
            name='cbe_conducted_1',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='agggovernancedashboard',
            name='cbe_conducted_2',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='agggovernancedashboard',
            name='cbe_date_1',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='agggovernancedashboard',
            name='cbe_date_2',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='agggovernancedashboard',
            name='cbe_type_1',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='agggovernancedashboard',
            name='cbe_type_2',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='agggovernancedashboard',
            name='num_other_beneficiaries_1',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='agggovernancedashboard',
            name='num_other_beneficiaries_2',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='agggovernancedashboard',
            name='num_target_beneficiaries_1',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='agggovernancedashboard',
            name='num_target_beneficiaries_2',
            field=models.IntegerField(null=True),
        )
    ]
