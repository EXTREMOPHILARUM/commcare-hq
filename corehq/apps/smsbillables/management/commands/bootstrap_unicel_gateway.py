import logging
from django.core.management.base import LabelCommand

from corehq.apps.accounting.models import Currency
from corehq.apps.sms.models import INCOMING, OUTGOING
from corehq.apps.smsbillables.models import SmsGatewayFee
from corehq.apps.unicel.api import UnicelBackend

logger = logging.getLogger('accounting')


class Command(LabelCommand):
    help = "bootstrap Unicel gateway fees"
    args = ""
    label = ""

    def handle(self, *labels, **options):
        SmsGatewayFee.create_new(UnicelBackend.get_api_id(), INCOMING, 0.50,
                                 currency=Currency.objects.get(code="USD"))
        SmsGatewayFee.create_new(UnicelBackend.get_api_id(), OUTGOING, 0.50,
                                 currency=Currency.objects.get(code="USD"))
        logger.info("Updated Unicel gateway fees.")
