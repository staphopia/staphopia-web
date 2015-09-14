#! /usr/bin/env python
# Check if there are any new entries on SRA, if so retrieve them.
# Cron: 0 0 1 * * /data1/home/rpetit/staphopia/bin/UpdateMLST.py
import urllib2
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
    help = 'Insert experiments without a sample id into the queue.'

    def handle(self, *args, **options):
        experiments = Experiment.objects.all()
        i = 0
        total = experiments.count()
        print 'Completed {0} of {1} experiments.'.format(i, total)
        for experiment in experiments.iterator():
            sra_uid = self.get_sra_uid(experiment.experiment_accession)
            pmids = self.get_pubmed_link(sra_uid)
            if pmids:
                for pmid in pmids:
                    self.insert_publication(experiment, pmid)
            time.sleep(1)

            i += 1
            if i % 1000 == 0:
                print 'Completed {0} of {1} experiments.'.format(i, total)

    @transaction.atomic
    def insert_publication(self, experiment, pmid):
        publication, created = Publication.objects.get_or_create(
            experiment_accession=experiment,
            pmid=pmid
        )
        print '{0}\t{1}\t{2}'.format(
            experiment.experiment_accession,
            pmid,
            created
        )

    def cook_soup(self, url):
        request = urllib2.Request(url)
        xml = urllib2.urlopen(request).read()
        return BeautifulSoup(xml, 'lxml')

    def get_sra_uid(self, term):
        url = '{0}={1}'.format(ESEARCH, term)
        soup = self.cook_soup(url)
        return soup.findAll('id')[0].get_text()

    def get_pubmed_link(self, uid):
        url = '{0}={1}'.format(ELINK, uid)
        soup = self.cook_soup(url)
        pmids = [i.get_text() for i in soup.findAll('id')]
        pmids.remove(uid)
        return pmids
