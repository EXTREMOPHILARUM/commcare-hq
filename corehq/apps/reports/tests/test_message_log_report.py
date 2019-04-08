from __future__ import absolute_import, unicode_literals

import uuid
from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import RequestFactory

from dimagi.utils.dates import DateSpan

from corehq.apps.domain.shortcuts import create_domain
from corehq.apps.reports.standard.sms import MessageLogReport
from corehq.apps.sms.models import SMS, MessagingEvent
from corehq.apps.users.models import WebUser


class MessageLogReportTest(TestCase):
    domain = uuid.uuid4().hex

    def test_basic_functionality(self):
        self.make_simple_sms('message 1')
        self.make_simple_sms('message 2')
        self.assertEqual(
            self.get_report_column('Message'),
            ['message 1', 'message 2'],
        )

    @classmethod
    def setUpClass(cls):
        super(MessageLogReportTest, cls).setUpClass()
        cls.domain_obj = create_domain(cls.domain)
        cls.factory = RequestFactory()
        cls.couch_user = WebUser.create(None, "phone_report_test", "foobar")
        cls.couch_user.add_domain_membership(cls.domain, is_admin=True)
        cls.couch_user.save()

    @classmethod
    def tearDownClass(cls):
        super(MessageLogReportTest, cls).tearDownClass()
        cls.couch_user.delete()
        cls.domain_obj.delete()

    def get_report_column(self, column_header):
        return [row[column_header] for row in self.get_report_rows()]

    def get_report_rows(self):
        request = self.factory.get('/')
        request.couch_user = self.couch_user
        request.datespan = DateSpan(
            startdate=datetime.utcnow() - timedelta(days=30),
            enddate=datetime.utcnow(),
        )
        report = MessageLogReport(request, domain=self.domain)
        headers = [h.html for h in report.headers.header]
        for row in report.rows:
            yield dict(zip(headers, row))

    def make_simple_sms(self, message):
        sms = SMS.objects.create(
            domain=self.domain,
            date=datetime.utcnow(),
            text=message,
        )
        self.addCleanup(sms.delete)
