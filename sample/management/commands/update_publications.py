"""
update_publications.

For each sample make sure their is_published is the same in sample and
metadata tables.
"""
import datetime

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from sample.models import Sample, Metadata


class Command(BaseCommand):
    """Reflect is_published in Sample to Metadata."""

    help = 'Reflect is_published in Sample to Metadata.'

    def handle(self, *args, **options):
        """Reflect is_published in Sample to Metadata."""
        count = 1
        for sample in Sample.objects.filter(is_public=True):
            self.update_metadata(sample)
            if count % 1000 == 0:
                print(count)
            count += 1

    @transaction.atomic
    def update_metadata(self, sample):
        try:
            # Update the metadata
            metadata = Metadata.objects.get(sample=sample)
            if not metadata.history:
                metadata.history = []

            if 'is_published' in metadata.metadata:
                metadata.history.append({
                    'user_id': sample.user.id,
                    'user_name': sample.user.username,
                    'field': 'is_published',
                    'value': metadata.metadata['is_published'],
                    'date': str(datetime.datetime.now())
                })
            else:
                metadata.history.append({
                    'user_id': sample.user.id,
                    'user_name': sample.user.username,
                    'field': 'is_published',
                    'value': 'CREATED_FIELD',
                    'date': str(datetime.datetime.now())
                })
            metadata.metadata['is_published'] = sample.is_published
            metadata.save()
        except IntegrityError as e:
            raise CommandError(f'Sample {sample.name} error updating tag, {e}')
