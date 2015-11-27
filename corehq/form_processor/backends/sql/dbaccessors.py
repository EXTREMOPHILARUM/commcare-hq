from datetime import datetime
from itertools import groupby

from django.db import transaction
from django.db.models import Prefetch
from corehq.form_processor.exceptions import XFormNotFound, CaseNotFound, AttachmentNotFound
from corehq.form_processor.interfaces.dbaccessors import AbstractCaseAccessor, AbstractFormAccessor
from corehq.form_processor.models import (
    XFormInstanceSQL, CommCareCaseIndexSQL, CaseAttachmentSQL, CaseTransaction,
    CommCareCaseSQL, XFormAttachmentSQL, XFormOperationSQL
)

doc_type_to_state = {
    "XFormInstance": XFormInstanceSQL.NORMAL,
    "XFormError": XFormInstanceSQL.ERROR,
    "XFormDuplicate": XFormInstanceSQL.DUPLICATE,
    "XFormDeprecated": XFormInstanceSQL.DEPRECATED,
    "XFormArchived": XFormInstanceSQL.ARCHIVED,
    "SubmissionErrorLog": XFormInstanceSQL.SUBMISSION_ERROR_LOG
}


class FormAccessorSQL(AbstractFormAccessor):

    @staticmethod
    def get_form(form_id):
        try:
            return XFormInstanceSQL.objects.raw('SELECT * from get_form_by_id(%s)', [form_id])[0]
        except IndexError:
            raise XFormNotFound

    @staticmethod
    def get_forms(form_ids, ordered=False):
        forms = list(XFormInstanceSQL.objects.raw('SELECT * from get_forms_by_id(%s)', [form_ids]))
        if ordered:
            forms = _order_list(form_ids, forms, 'form_id')

        return forms

    @staticmethod
    def get_attachments(form_id):
        return list(XFormAttachmentSQL.objects.raw('SELECT * from get_form_attachments(%s)', [form_id]))

    @staticmethod
    def get_with_attachments(form_id):
        form = FormAccessorSQL.get_form(form_id)
        attachments = FormAccessorSQL.get_attachments(form_id)
        form.cached_attachments = attachments
        return form

    @staticmethod
    def get_attachment_by_name(form_id, attachment_name):
        try:
            return XFormAttachmentSQL.objects.raw(
                'select * from get_form_attachment_by_name(%s, %s)',
                [form_id, attachment_name]
            )[0]
        except IndexError:
            raise AttachmentNotFound(attachment_name)

    @staticmethod
    def get_form_operations(form_id):
        return list(XFormOperationSQL.objects.raw('SELECT * from get_form_operations(%s)', [form_id]))

    @staticmethod
    def get_forms_with_attachments_meta(form_ids, ordered=False):
        forms = FormAccessorSQL.get_forms(form_ids)

        # attachments are already sorted by form_id in SQL
        attachments = XFormAttachmentSQL.objects.raw(
            'SELECT * from get_mulitple_forms_attachments(%s)',
            [form_ids]
        )

        forms_by_id = {form.form_id: form for form in forms}
        grouped_attachments = groupby(attachments, lambda x: x.form_id)
        for form_id, attachments_group in grouped_attachments:
            form = forms_by_id[form_id]
            form.cached_attachments = list(attachments_group)

        if ordered:
            _order_list(form_ids, forms, 'form_id')

        return forms

    @staticmethod
    def get_forms_by_type(domain, type_, limit, recent_first=False):
        state = doc_type_to_state[type_]
        assert limit is not None

        order = 'received_on'
        if recent_first:
            order = '-{}'.format(order)

        return XFormInstanceSQL.objects.filter(
            domain=domain,
            state=state
        ).order_by(order)[0:limit]

    @staticmethod
    def form_with_id_exists(form_id, domain=None):
        query = XFormInstanceSQL.objects.filter(form_id=form_id)
        if domain:
            query = query.filter(domain=domain)
        return query.exists()

    @staticmethod
    def hard_delete_forms(form_ids):
        with transaction.atomic():
            XFormAttachmentSQL.objects.filter(form_id__in=form_ids).delete()
            XFormOperationSQL.objects.filter(form_id__in=form_ids).delete()
            XFormInstanceSQL.objects.filter(form_id__in=form_ids).delete()

    @staticmethod
    def archive_form(form_id, user_id=None):
        with transaction.atomic():
            operation = XFormOperationSQL(
                user_id=user_id,
                operation=XFormOperationSQL.ARCHIVE,
                date=datetime.utcnow(),
                form_id=form_id
            )
            operation.save()
            XFormInstanceSQL.objects.filter(form_id=form_id).update(state=XFormInstanceSQL.ARCHIVED)
            CaseTransaction.objects.filter(form_id=form_id).update(revoked=True)

    @staticmethod
    def unarchive_form(form_id, user_id=None):
        with transaction.atomic():
            operation = XFormOperationSQL(
                user_id=user_id,
                operation=XFormOperationSQL.UNARCHIVE,
                date=datetime.utcnow(),
                form_id=form_id
            )
            operation.save()
            XFormInstanceSQL.objects.filter(form_id=form_id).update(state=XFormInstanceSQL.NORMAL)
            CaseTransaction.objects.filter(form_id=form_id).update(revoked=False)


class CaseAccessorSQL(AbstractCaseAccessor):

    @staticmethod
    def get_case(case_id):
        try:
            return CommCareCaseSQL.objects.get(case_id=case_id)
        except CommCareCaseSQL.DoesNotExist:
            raise CaseNotFound

    @staticmethod
    def get_cases(case_ids, ordered=False):
        cases = list(CommCareCaseSQL.objects.filter(case_id__in=list(case_ids)).all())
        if ordered:
            cases = _order_list(case_ids, cases, 'case_id')

        return cases

    @staticmethod
    def case_modified_since(case_id, server_modified_on):
        """
        Return True if a case has been modified since the given modification date.
        Assumes that the case exists in the DB.
        """
        return not CommCareCaseSQL.objects.filter(
            case_id=case_id,
            server_modified_on=server_modified_on
        ).exists()

    @staticmethod
    def get_case_xform_ids(case_id):
        return list(CaseTransaction.objects.filter(
            case_id=case_id,
            revoked=False,
            form_id__isnull=False,
            type=CaseTransaction.TYPE_FORM
        ).values_list('form_id', flat=True))

    @staticmethod
    def get_indices(case_id):
        return list(CommCareCaseIndexSQL.objects.filter(case_id=case_id).all())

    @staticmethod
    def get_reverse_indices(case_id):
        return list(CommCareCaseIndexSQL.objects.filter(referenced_id=case_id).all())

    @staticmethod
    def get_reverse_indexed_cases(domain, case_ids):
        return CommCareCaseSQL.objects.filter(
            domain=domain, index__referenced_id__in=case_ids
        ).defer("case_json").prefetch_related('indices')

    @staticmethod
    def hard_delete_case(case_id):
        with transaction.atomic():
            CommCareCaseIndexSQL.objects.filter(case_id=case_id).delete()
            CaseAttachmentSQL.objects.filter(case_id=case_id).delete()
            CaseTransaction.objects.filter(case_id=case_id).delete()
            CommCareCaseSQL.objects.filter(case_id=case_id).delete()

    @staticmethod
    def get_attachment(case_id, attachment_name):
        try:
            return CaseAttachmentSQL.objects.filter(case_id=case_id, name=attachment_name)[0]
        except IndexError:
            raise AttachmentNotFound(attachment_name)

    @staticmethod
    def get_attachments(case_id):
        return list(CaseAttachmentSQL.objects.filter(case_id=case_id).all())

    @staticmethod
    def get_transactions_for_case_rebuild(case_id):
        return list(CaseTransaction.objects.filter(
            case_id=case_id,
            revoked=False,
            type__in=CaseTransaction.TYPES_TO_PROCESS
        ).all())

    @staticmethod
    def get_case_by_location(domain, location_id):
        try:
            return CommCareCaseSQL.objects.filter(
                domain=domain,
                type='supply-point',
                location_id=location_id
            ).get()
        except CommCareCaseSQL.DoesNotExist:
            return None

    @staticmethod
    def get_case_ids_in_domain(domain, type=None):
        query = CommCareCaseSQL.objects.filter(domain=domain)
        if type:
            query.filter(type=type)
        return list(query.values_list('case_id', flat=True))


def _order_list(id_list, object_list, id_property):
    # SQL won't return the rows in any particular order so we need to order them ourselves
    index_map = {id_: index for index, id_ in enumerate(id_list)}
    ordered_list = [None] * len(id_list)
    for obj in object_list:
        ordered_list[index_map[getattr(obj, id_property)]] = obj

    return ordered_list
