# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-09-19 15:48
from __future__ import unicode_literals

from django.db import migrations
from corehq.sql_db.operations import HqRunSQL


class Migration(migrations.Migration):

    dependencies = [
        ('sql_accessors', '0054_drop_reindexa_accessor_functions'),
    ]

    operations = [
        HqRunSQL("DROP FUNCTION IF EXISTS get_cases_by_id(TEXT[])"),
        HqRunSQL("DROP FUNCTION IF EXISTS get_forms_by_id(TEXT[])"),
    ]
