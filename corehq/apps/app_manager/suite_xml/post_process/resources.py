from collections import Counter
from django.db import models

from corehq.apps.app_manager.exceptions import ResourceOverrideError
from corehq.apps.app_manager.suite_xml.contributors import PostProcessor
from corehq.apps.app_manager.suite_xml.sections.resources import FormResourceContributor
from corehq.apps.app_manager.suite_xml.xml_models import XFormResource
from corehq.util.quickcache import quickcache


class ResourceOverride(models.Model):
    domain = models.CharField(max_length=255, null=False)
    app_id = models.CharField(max_length=255, null=False)
    # Type of resource, e.g., xform. Populated by the root_name of the relevant suite_xml.xml_models class.
    root_name = models.CharField(max_length=32, null=False)
    pre_id = models.CharField(max_length=255, null=False)
    post_id = models.CharField(max_length=255, null=False)

    class Meta(object):
        unique_together = ('domain', 'app_id', 'root_name', 'pre_id')


def add_xform_resource_overrides(domain, app_id, pre_to_post_map):
    overrides_by_pre_id = get_xform_resource_overrides(domain, app_id)
    dirty = False
    for pre, post in pre_to_post_map.items():
        if pre in overrides_by_pre_id:
            if post != overrides_by_pre_id[pre].post_id:
                raise ResourceOverrideError("Cannot change override of {}".format(pre))
        else:
            dirty = True
            override = ResourceOverride.objects.create(
                domain=domain,
                app_id=app_id,
                root_name=XFormResource.ROOT_NAME,
                pre_id=pre,
                post_id=post,
            )
            override.save()
    if dirty:
        get_xform_resource_overrides.clear(domain, app_id)


@quickcache(['domain', 'app_id'], timeout=1 * 60 * 60)
def get_xform_resource_overrides(domain, app_id):
    return {
        override.pre_id: override
        for override in ResourceOverride.objects.filter(
            domain=domain,
            app_id=app_id,
            root_name=XFormResource.ROOT_NAME,
        )
    }


class ResourceOverrideHelper(PostProcessor):

    def update_suite(self):
        """
        Applies manual overrides of resource ids.
        """
        overrides_by_pre_id = get_xform_resource_overrides(self.app.domain, self.app.master_id)
        resources = getattr(self.suite, FormResourceContributor.section_name)
        for resource in resources:
            if resource.id in overrides_by_pre_id:
                resource.id = overrides_by_pre_id[resource.id].post_id

        id_counts = Counter(resource.id for resource in resources)
        duplicates = [key for key, count in id_counts.items() if count > 1]
        if duplicates:
            raise ResourceOverrideError("Duplicate resource ids found: {}".format(", ".join(duplicates)))