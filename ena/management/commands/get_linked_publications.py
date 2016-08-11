#! /usr/bin/env python
"""Find links between SRA and Pubmed."""
from __future__ import print_function
import urllib2
import time
import sys

from bs4 import BeautifulSoup

from django.db import transaction
from django.core.management.base import BaseCommand

from ena.models import Experiment, ToPublication
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

    def handle(self, *args, **options):
        """Find links between SRA and Pubmed."""
        experiments = Experiment.objects.all()
        i = 0
        total = float(experiments.count())
        pubmed = {}
        for experiment in experiments.iterator():
            sra_uid = self.get_sra_uid(experiment.experiment_accession)
            pmids = self.get_pubmed_link(sra_uid)
            if pmids:
                for pmid in pmids:
                    if pmid not in pubmed:
                        pubmed_info = self.get_pubmed_info(pmid)
                        pubmed[pmid] = {
                            'obj': self.insert_publication(pmid, pubmed_info)
                        }
                    self.insert_ena_to_pub(experiment, pubmed[pmid]['obj'])

            time.sleep(1)

            i += 1
            print("{0} of {1} ({2:.2f}%)".format(i, total, i / total * 100))

    @transaction.atomic
    def insert_publication(self, pmid, pubmed_info):
        """Insert publication into the database."""
        publication, created = Publication.objects.get_or_create(
            pmid=pmid,
            **pubmed_info
        )
        print('{0} ({1})\t{2}'.format(
            pmid, created, pubmed_info['title']
        ))

        return publication

    def insert_ena_to_pub(self, experiment, publication):
        """Insert link to ToPublication table."""
        topub, created = ToPublication.objects.get_or_create(
            experiment_accession=experiment,
            publication=publication
        )
        print('{0} ({1})\t{2}'.format(
            experiment.experiment_accession, created, publication.pmid
        ))

        return topub

    def cook_soup(self, url):
        """Query NCBI."""
        request = urllib2.Request(url)
        xml = None
        while not xml:
            try:
                xml = urllib2.urlopen(request).read()
            except urllib2.URLError:
                continue
        return BeautifulSoup(xml, 'lxml')

    def get_sra_uid(self, term):
        """Get the SRA UID."""
        url = '{0}={1}'.format(ESEARCH, term)
        soup = self.cook_soup(url)
        return soup.findAll('id')[0].get_text()

    def get_pubmed_link(self, uid):
        """Get PubMed Links."""
        url = '{0}={1}'.format(ELINK, uid)
        soup = self.cook_soup(url)
        pmids = [i.get_text() for i in soup.findAll('id')]
        try:
            pmids.remove(uid)
        except ValueError:
            pass
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
