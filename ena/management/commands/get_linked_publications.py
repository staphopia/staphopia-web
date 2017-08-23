#! /usr/bin/env python
"""Find links between SRA and Pubmed."""
from __future__ import print_function
import datetime
import requests
import time
import sys

from bs4 import BeautifulSoup

from django.db import IntegrityError, transaction
from django.core.management.base import BaseCommand
from django.utils import timezone

from ena.models import Experiment, ToPublication, SraLink
from sample.models import Publication

EUTILS = 'http://www.ncbi.nlm.nih.gov/entrez/eutils'
ESEARCH = EUTILS + '/esearch.fcgi?db=sra&term'
ESUMMARY = EUTILS + '/esummary.fcgi?db=pubmed&id'
EFETCH = EUTILS + '/efetch.fcgi?db=pubmed&retmode=xml&id'
ELINK = EUTILS + '/elink.fcgi?dbfrom=sra&db=pubmed&id'

reload(sys)
sys.setdefaultencoding('utf-8')


class Command(BaseCommand):
    """Find links between SRA and Pubmed."""

    help = 'Find links between SRA and Pubmed.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('--days', dest='days', type=int, default=10,
                            help='Ignore samples checked in last X days.')

    def handle(self, *args, **options):
        """Find links between SRA and Pubmed."""
        experiments = Experiment.objects.all()
        i = 0
        total = float(experiments.count())
        pubmed = {}
        for experiment in experiments.iterator():
            sra_uid, skip = self.get_sra_uid(experiment, days=options['days'])
            if not skip:
                pmids = self.get_pubmed_link(sra_uid)
                if pmids:
                    for pmid in pmids:
                        if pmid not in pubmed:
                            pubmed_info = self.get_pubmed_info(pmid)
                            pubmed[pmid] = {
                                'obj': self.insert_publication(pmid,
                                                               pubmed_info)
                            }
                        self.insert_ena_to_pub(experiment, pubmed[pmid]['obj'])

                time.sleep(0.33)

            i += 1
            print("{0} -- {1} of {2} ({3:.2f}%) -- Skipped: {4}".format(
                experiment.experiment_accession,
                i,
                total,
                i / total * 100,
                skip
            ))
            break

    @transaction.atomic
    def insert_publication(self, pmid, pubmed_info):
        """Insert publication into the database."""
        created = False
        try:
            with transaction.atomic():
                publication = Publication.objects.create(
                    pmid=pmid,
                    **pubmed_info
                )
                created = True
        except IntegrityError:
            publication = Publication.objects.get(pmid=pmid)

        print('{0} ({1})\t{2}'.format(
            pmid, created, pubmed_info['title']
        ))

        return publication

    def insert_ena_to_pub(self, experiment, publication):
        """Insert link to ToPublication table."""
        created = False
        try:
            with transaction.atomic():
                topub = ToPublication.objects.create(
                    experiment_accession=experiment,
                    publication=publication
                )
                created = True
        except IntegrityError:
            topub = ToPublication.objects.get(
                experiment_accession=experiment,
                publication=publication
            )

        print('{0} ({1})\t{2}'.format(
            experiment.experiment_accession, created, publication.pmid
        ))

        return topub

    def cook_soup(self, url):
        """Query NCBI."""
        xml = None
        while not xml:
            try:
                r = requests.get(url, timeout=60)
                xml = r.text
            except (requests.ConnectionError, requests.exceptions.Timeout):
                continue
        return BeautifulSoup(xml, 'lxml')

    def get_sra_uid(self, experiment, days=10):
        """Get the SRA UID."""
        uid = None
        skip = False
        try:
            obj = SraLink.objects.get(
                experiment_accession=experiment
            )
            elapsed = timezone.now() - obj.last_checked
            if elapsed > datetime.timedelta(days=days):
                skip = False
                obj.save()
            else:
                skip = True

            uid = obj.uid
        except SraLink.DoesNotExist:
            url = '{0}={1}'.format(ESEARCH, experiment.experiment_accession)
            soup = self.cook_soup(url)
            uid = soup.findAll('id')[0].get_text()
            with transaction.atomic():
                SraLink.objects.create(experiment_accession=experiment,
                                       uid=uid)

        return [uid, skip]

    def get_pubmed_link(self, uid):
        """Get PubMed Links."""
        url = '{0}={1}'.format(ELINK, uid)
        soup = self.cook_soup(url)
        pmids = []
        is_sra_uid = True
        for i in soup.findAll('id'):
            # First ID in list is the SRA UID of the query, remaining (if any)
            # are PubMed IDs
            if is_sra_uid:
                is_sra_uid = False
            else:
                pmids.append(i.get_text())

        return pmids

    def get_author_name(self, author):
        """Parse out author names."""
        try:
            lastname = author.lastname.get_text()
        except:
            lastname = ''

        try:
            firstname = author.forename.get_text()
        except:
            firstname = ''

        try:
            suffix = author.suffix.get_text().replace('3rd', 'III')
        except:
            suffix = ''

        try:
            initial = author.initials.get_text()
        except:
            initial = ''

        name = '{0} {1} {2} ({3})'.format(firstname, lastname, suffix, initial)
        return name.replace('  ', ' ')

    def get_article_id(self, article):
        """Parse out article ids."""
        return '{0}={1}'.format(article['idtype'], article.get_text())

    def get_pubmed_info(self, pmid):
        """Fetch info (abstract, authors, etc...) related to pubmed id."""
        url = '{0}={1}'.format(EFETCH, pmid)
        soup = self.cook_soup(url)

        authors = [self.get_author_name(a) for a in soup.findAll('author')]
        ids = [self.get_article_id(a) for a in soup.find_all('articleid')]
        keyword_items = ['keyword', 'descriptorname', 'qualifiername']
        keywords = set([i.get_text() for i in soup.find_all(keyword_items)])
        return {
            'authors': ';'.join(authors),
            'title': soup.find('articletitle').get_text(),
            'abstract': soup.find('abstracttext').get_text(),
            'reference_ids': ';'.join(ids),
            'keywords': ';'.join(list(keywords))
        }
