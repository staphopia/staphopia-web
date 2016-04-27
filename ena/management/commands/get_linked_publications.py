#! /usr/bin/env python
"""Find links between SRA and Pubmed."""
from __future__ import print_function
import urllib2
import sys
import time
from bs4 import BeautifulSoup

from django.db import transaction
from django.core.management.base import BaseCommand

from ena.models import Experiment, Publication

EUTILS = 'http://www.ncbi.nlm.nih.gov/entrez/eutils'
ESEARCH = EUTILS + '/esearch.fcgi?db=sra&term'
ESUMMARY = EUTILS + '/esummary.fcgi?db=pubmed&id'
ELINK = EUTILS + '/elink.fcgi?dbfrom=sra&db=pubmed&id'


class Command(BaseCommand):
    """Find links between SRA and Pubmed."""

    help = 'Find links between SRA and Pubmed.'

    def handle(self, *args, **options):
        """Find links between SRA and Pubmed."""
        experiments = Experiment.objects.all()
        i = 0
        total = experiments.count()
        for experiment in experiments.iterator():
            sra_uid = self.get_sra_uid(experiment.experiment_accession)
            pmids = self.get_pubmed_link(sra_uid)
            if pmids:
                for pmid in pmids:
                    self.insert_publication(experiment, pmid)
            time.sleep(1)

            i += 1
            print("{0} of {1} ({2:.2f}%)".format(i, total, i / total * 100),
                  end='\r')
            sys.stdout.flush()

    @transaction.atomic
    def insert_publication(self, experiment, pmid):
        """Insert publication into the database."""
        publication, created = Publication.objects.get_or_create(
            experiment_accession=experiment,
            pmid=pmid
        )
        print('{0}\t{1}\t{2}'.format(
            experiment.experiment_accession, pmid, created
        ))

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
