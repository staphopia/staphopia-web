"""
Useful functions associated with versions.

To use:
from version.tools import UTIL1, UTIL2, etc...
"""
import os

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from version.models import Version


def get_pipeline_version(version_file):
    tag = None
    version = None
    with open(version_file, 'r') as fh:
        tag = fh.readline().rstrip()

    try:
        version = Version.objects.get(tag=tag)
        print(f'Found a pipeline version with tag {tag} ({version.id})')
    except Version.DoesNotExist:
        raise CommandError(f'No version exists under the tag {tag}')

    return version
