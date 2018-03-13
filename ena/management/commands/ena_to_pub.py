#! /usr/bin/env python
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from ena.models import ToPublication
from publication.models import ToSample
from sample.models import Sample


class Command(BaseCommand):
    help = 'Link ENA publications and Sample Publications'

    @transaction.atomic
    def handle(self, *args, **options):
        # Go through the ENAToPublication Table
        user = User.objects.get(username='ena')
        skipped = 0
        updated = 0

        for ena in ToPublication.objects.all():
            name = ena.experiment_accession.experiment_accession
            try:
                sample = Sample.objects.get(name=name, user=user)
                try:
                    ToSample.objects.get(sample=sample,
                                         publication=ena.publication)
                except ToSample.DoesNotExist:
                    ToSample.objects.create(
                        sample=sample, publication=ena.publication
                    )
                sample.is_published = True
                updated += 1
                sample.save()
            except Sample.DoesNotExist:
                skipped += 1

        print(f'Updated: {updated}, Skipped: {skipped}')
