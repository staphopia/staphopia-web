#! /usr/bin/env python
import time
from scholar import ScholarQuerier, SearchScholarQuery

from django.db import transaction
from django.core.management.base import BaseCommand

from ena.models import Study, GoogleScholar


class Command(BaseCommand):
    help = 'Search Study accessions against Google Scholar.'

    def add_arguments(self, parser):
        parser.add_argument('--experiments', action='store_true',
                            help='Search experiment accessions.')
        parser.add_argument('--runs', action='store_true',
                            help='Search run accessions.')

    def handle(self, *args, **options):
        for study in Study.objects.all():
            print 'Working on: {0}'.format(study.study_accession)
            self.search(study.study_accession)
            print 'Working on: {0}'.format(study.secondary_study_accession)
            self.search(study.secondary_study_accession)

    @transaction.atomic
    def search(self, term):
        querier = ScholarQuerier()
        query = SearchScholarQuery()
        query.set_words(term)
        querier.send_query(query)
        for article in querier.articles:
            id, created = GoogleScholar.objects.get_or_create(
                accession=term,
                title=article.attrs['title'][0],
                url=article.attrs['url'][0],
                cluster_id=article.attrs['cluster_id'][0],
                url_citations=article.attrs['url_citations'][0],
            )
            print '{0} added to database'.format(term)
        print 'Sleeping for 10 seconds...'
        time.sleep(10)
