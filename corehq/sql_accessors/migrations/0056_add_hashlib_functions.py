# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-04 08:36
from __future__ import absolute_import, unicode_literals

from django.db import migrations
from django.conf import settings

from corehq.sql_db.operations import noop_migration


class Migration(migrations.Migration):

    dependencies = [
        ('sql_accessors', '0055_set_form_modified_on'),
    ]

    operations = [
        # this originally installed the hashlib extension in production as well
        # but commcare-cloud does that where possible already
        # and Amazon RDS doesn't allow it
        # Todo: Move this to testing harness, doesn't really belong here.
        # See https://github.com/dimagi/commcare-hq/pull/21627#pullrequestreview-149807976
        migrations.RunSQL(
            'CREATE EXTENSION IF NOT EXISTS hashlib',
            'DROP EXTENSION hashlib'
        )
        if settings.UNIT_TESTING else noop_migration()
    ]
