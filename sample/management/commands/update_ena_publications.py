"""
update_ena_metadata.

Reads ena related tables and aggregates metadata into a single table.
"""
from django.db import transaction
from django.core.management.base import BaseCommand

from ena.models import ToPublication as EnaPubs
from sample.models import Sample, Publication, ToPublication


class Command(BaseCommand):
    """Update database with latest ENA publicly available data."""

    help = 'Update database with latest ENA publicly available data.'

    @transaction.atomic
    def handle(self, *args, **options):
        """Query ENA and retrieve latest results."""
        ena_pubs = EnaPubs.objects.all()
        samples = {}
        count = 0
        total = ena_pubs.count()
        for pub in ena_pubs:
            count += 1
            sample_tag = pub.experiment_accession.pk
            sample = None
            if sample_tag in samples:
                sample = samples[sample_tag]
            else:
                print sample_tag
                try:
                    sample = Sample.objects.get(
                        sample_tag=sample_tag
                    )
                except Sample.DoesNotExist:
                    print(
                        "#### {0} NOT FOUND IN DB. ####".format(sample_tag)
                    )
                    continue

            # Add the pub
            to_pubs, created = ToPublication.objects.get_or_create(
                sample=sample,
                publication=pub.publication
            )

            # Make sure sample is set to published
            sample.is_public = True
            sample.is_published = True
            sample.save()

            if created:
                print("Linked {0} to PMID {1}".format(
                    sample_tag, pub.publication.pmid
                ))
