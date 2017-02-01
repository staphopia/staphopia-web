#! /usr/bin/env python
from __future__ import print_function
import urllib2
import time
import sys

from bs4 import BeautifulSoup

from django.db import transaction
from django.core.management.base import BaseCommand

from ena.models import Study, Experiment, ToPublication
from sample.models import Sample, Publication

EUTILS = 'http://www.ncbi.nlm.nih.gov/entrez/eutils'
ESEARCH = EUTILS + '/esearch.fcgi?db=sra&term'
ESUMMARY = EUTILS + '/esummary.fcgi?db=pubmed&id'
EFETCH = EUTILS + '/efetch.fcgi?db=pubmed&retmode=xml&id'
ELINK = EUTILS + '/elink.fcgi?dbfrom=sra&db=pubmed&id'

class Command(BaseCommand):
    help = 'Link Study accessions to PubMed IDs.'

    def add_arguments(self, parser):
        parser.add_argument('pmid', help='PubMed ID to link ENA entries to.')
        parser.add_argument('study', help='Study accession for ENA entry.')
        parser.add_argument('--output', help='Print output info.')

    def handle(self, *args, **options):
        stats = {}
        try:
            study = Study.objects.get(pk=options['study'])
        except Study.DoesNotExist:
            try:
                study = Study.objects.get(
                    secondary_study_accession=options['study']
                )
            except Study.DoesNotExist:
                print("Study {0} not in the database.".format(
                    options['study']
                ), file=sys.stderr)
                sys.exit()

        created = False
        try:
            publication = Publication.objects.get(pmid=options['pmid'])
        except Publication.DoesNotExist:
            pubmed_info = self.get_pubmed_info(options['pmid'])
            publication = self.insert_publication(options['pmid'], pubmed_info)
            created = True

        total = 0
        for experiment in Experiment.objects.filter(study_accession=study):
            to_pub, created = ToPublication.objects.get_or_create(
                experiment_accession=experiment,
                publication=publication
            )
            total += 1
            '''try:
                sample = Sample.objects.get(sample_tag=experiment.pk)
                sample.is_published = True
                sample.save()
                print('{0}\t{1}\t{2}'.format(
                    experiment.pk, publication.pmid, created
                ),file=sys.stderr)
            except Sample.DoesNotExist:
                print("Experiment {0} not in the database.".format(experiment.pk),file=sys.stderr)'''
        print("\t".join([str(total), publication.pmid, str(created), study.pk,
                         study.secondary_study_accession, publication.title]))

    @transaction.atomic
    def insert_publication(self, pmid, pubmed_info):
        """Insert publication into the database."""
        publication, created = Publication.objects.get_or_create(
            pmid=pmid,
            **pubmed_info
        )
        print('{0} ({1})\t{2}'.format(
            pmid, created, pubmed_info['title']
        ), file=sys.stderr)

        return publication

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

    def fix_unicode(self, string):
        return string.encode('ascii', 'ignore').decode('ascii')

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

        name = '{0} {1} {2} ({3})'.format(
            self.fix_unicode(firstname),
            self.fix_unicode(lastname),
            self.fix_unicode(suffix),
            self.fix_unicode(initial)
        )
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
            'title': soup.find('articletitle').get_text().encode('ascii', 'ignore').decode('ascii'),
            'abstract': soup.find('abstracttext').get_text().encode('ascii', 'ignore').decode('ascii'),
            'reference_ids': ';'.join(ids),
            'keywords': ';'.join(list(keywords))
        }
