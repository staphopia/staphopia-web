#! /usr/bin/env python
import datetime

import scholarly

from django.core.mail import EmailMessage
from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils import timezone

from ena.models import Study, Run, GoogleScholar, GoogleScholarStatus


class Command(BaseCommand):
    help = 'Search Study accessions against Google Scholar.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('--days', dest='days', type=int, default=10,
                            help='Ignore samples checked in last X days.')

    def handle(self, *args, **options):
        accessions = self.get_accessions()
        total = len(accessions)
        checked = 0
        links = 0
        skipped = 0
        i = 0
        for accession in accessions:
            i += 1
            obj, skip = self.get_accession_status(accession, options['days'])
            if skip:
                skipped += 1
            else:
                checked += 1
                links += self.search(accession)
                obj.is_queried = True
                obj.save()

            print("{0} -- {1} of {2} ({3:.2f}%) -- Skipped: {4}".format(
                accession,
                i,
                total,
                i / float(total) * 100,
                skip
            ))

        self.email_stats(total, checked, skipped, links)

    def email_stats(self, total, checked, skipped, links):
        """Email admin with update."""
        labrat = "Staphopia's Friendly Robot <usa300@staphopia.com>"
        subject = '[Staphopia ENA Update] - GetLinkedPubs Info.'
        message = (
            "A total of {0} samples out of {1} ({2} skipped), were tested for "
            "links between SRA and PubMed.\n\n"
            "{3} hits were made against google scholar.\n"
        ).format(checked, total, skipped, links)
        recipients = ['admin@staphopia.com', 'robert.petit@emory.edu']
        email = EmailMessage(subject, message, labrat, recipients)
        email.send(fail_silently=False)

    def get_accession_status(self, accession, days):
        skip = None
        try:
            obj = GoogleScholarStatus.objects.get(
                accession=accession
            )
            elapsed = timezone.now() - obj.last_checked
            if elapsed > datetime.timedelta(days=days) or not obj.is_queried:
                skip = False
            else:
                skip = True
        except GoogleScholarStatus.DoesNotExist:
            skip = False
            with transaction.atomic():
                obj = GoogleScholarStatus.objects.create(accession=accession)

        return [obj, skip]

    def get_accessions(self):
        accessions = []
        for row in Study.objects.values_list('study_accession',
                                             'secondary_study_accession'):
            accessions.append(row[0])
            accessions.append(row[1])

        for row in Run.objects.values_list('run_accession',
                                           'experiment_accession'):
            accessions.append(row[0])
            accessions.append(row[1])

        return accessions

    @transaction.atomic
    def search(self, accession):
        links = 0
        search_query = scholarly.search_pubs_query(accession)
        for result in search_query:
            links += 1

            id, created = GoogleScholar.objects.get_or_create(
                accession=accession,
                title=result.bib['title'],
                url=result.bib['url']
            )

            print('{0} -- {1} added to database'.format(
                accession, result.bib['title']
            ))

        return links
