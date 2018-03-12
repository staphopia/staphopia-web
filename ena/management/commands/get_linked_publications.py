#! /usr/bin/env python
"""Find links between SRA and Pubmed."""
from __future__ import print_function
import datetime
import requests
import time
import sys

from bs4 import BeautifulSoup

from django.core.mail import EmailMessage
from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ena.models import Experiment, ToPublication, SraLink
from sample.models import Sample, Metadata
from publication.models import ToSample as PubToSample, Publication
from tag.models import ToSample as TagToSample, Tag

EUTILS = 'http://www.ncbi.nlm.nih.gov/entrez/eutils'
ESEARCH = EUTILS + '/esearch.fcgi?db=sra&term'
ESUMMARY = EUTILS + '/esummary.fcgi?db=pubmed&id'
EFETCH = EUTILS + '/efetch.fcgi?db=pubmed&retmode=xml&id'
ELINK = EUTILS + '/elink.fcgi?dbfrom=sra&db=pubmed&id'


class Command(BaseCommand):
    """Find links between SRA and Pubmed."""

    help = 'Find links between SRA and Pubmed.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('--days', dest='days', type=int, default=10,
                            help='Ignore samples checked in last X days.')

    def handle(self, *args, **options):
        """Find links between SRA and Pubmed."""
        user = User.objects.get(username='ena')
        experiments = Experiment.objects.all()
        i = 0
        total = experiments.count()
        pubmed = {}
        checked = 0
        links = 0
        skipped = 0
        for experiment in experiments.iterator():
            sra_obj, skip = self.get_sra_uid(experiment, days=options['days'])
            if not skip:
                checked += 1
                pmids = self.get_pubmed_link(sra_obj.uid)
                if pmids:
                    for pmid in pmids:
                        if pmid not in pubmed:
                            pubmed_obj, tag, created = self.get_pubmed_info(
                                pmid, user
                            )
                            print('{0} ({1})\t{2}'.format(
                                pmid, created, pubmed_obj.title
                            ))
                            pubmed[pmid] = {'obj': pubmed_obj}
                        self.insert_ena_to_pub(experiment, pubmed[pmid]['obj'])
                        sample = self.update_sample(
                            experiment.experiment_accession, user
                        )
                        if sample:
                            # These samples have been processed
                            self.update_metadata(sample, user)
                            self.update_sampletag(sample, tag)
                            self.link_publication_to_sample(sample, pubmed_obj)
                        links += 1
                sra_obj.is_queried = True
                sra_obj.save()
                time.sleep(0.33)
                skipped = 0
            else:
                skipped += 1

            i += 1
            print("{0} -- {1} of {2} ({3:.2f}%) -- Skipped: {4}".format(
                experiment.experiment_accession,
                i,
                total,
                i / float(total) * 100,
                skip
            ))

        self.email_stats(total, checked, skipped, len(pubmed.keys()), links)

    def email_stats(self, total, checked, skipped, pmids, links):
        """Email admin with update."""
        labrat = "Staphopia's Friendly Robot <usa300@staphopia.com>"
        subject = '[Staphopia ENA Update] - GetLinkedPubs Info.'
        message = (
            "A total of {0} samples out of {1} ({2} skipped), were tested for "
            "links between SRA and PubMed.\n\n"
            "{3} publications were linked to {4} samples.\n"
        ).format(checked, total, skipped, pmids, links)
        recipients = ['admin@staphopia.com', 'robert.petit@emory.edu']
        email = EmailMessage(subject, message, labrat, recipients)
        email.send(fail_silently=False)

    @transaction.atomic
    def insert_publication(self, pmid, pubmed_info):
        """Insert publication into the database."""
        return Publication.objects.create(
            pmid=pmid,
            **pubmed_info
        )

    @transaction.atomic
    def insert_ena_to_pub(self, experiment, publication):
        """Insert link to ToPublication table."""
        created = False
        try:
            topub = ToPublication.objects.get(
                experiment_accession=experiment,
                publication=publication
            )
            topub.sra_to_pubmed = True
            topub.save()
        except ToPublication.DoesNotExist:
            topub = ToPublication.objects.create(
                experiment_accession=experiment,
                publication=publication,
                sra_to_pubmed=True
            )
            created = True

        print('{0} ({1})\t{2}'.format(
            experiment.experiment_accession, created, publication.pmid
        ))

        return topub

    @transaction.atomic
    def update_sample(self, name, user):
        success = False
        try:
            # Update the sample
            sample = Sample.objects.get(user=user, name=name)
            sample.is_public = True
            sample.save()
            success = sample
        except Sample.DoesNotExist:
            print(f'Sample {name} does not exist, skipping')

        return success

    @transaction.atomic
    def update_metadata(self, sample, user):
        try:
            # Update the metadata
            metadata = Metadata.objects.get(sample=sample)
            if not metadata.history:
                metadata.history = []

            if 'is_published' in metadata.metadata:
                metadata.history.append({
                    'user_id': user.id,
                    'user_name': user.username,
                    'field': 'is_published',
                    'value': metadata.metadata['is_published'],
                    'date': str(datetime.datetime.now())
                })
            else:
                metadata.history.append({
                    'user_id': user.id,
                    'user_name': user.username,
                    'field': 'is_published',
                    'value': 'CREATED_FIELD',
                    'date': str(datetime.datetime.now())
                })
            metadata.metadata['is_published'] = True
            metadata.save()
        except IntegrityError as e:
            raise CommandError(f'Sample {name} error updating tag, {e}')

    @transaction.atomic
    def link_publication_to_sample(self, sample, publication):
        try:
            pub_obj, create = PubToSample.objects.get_or_create(
                sample=sample,
                publication=publication
            )
        except IntegrityError as e:
            raise CommandError(f'Sample {name} error linking publication, {e}')

    @transaction.atomic
    def update_sampletag(self, sample, tag):
        try:
            # Link to tag
            totag = TagToSample.objects.create(tag=tag, sample=sample)
        except IntegrityError as e:
            raise CommandError(f'Sample {name} does not exist, {e}')

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
        obj = None
        skip = False
        try:
            obj = SraLink.objects.get(
                experiment_accession=experiment
            )
            elapsed = timezone.now() - obj.last_checked
            if elapsed > datetime.timedelta(days=days) or not obj.is_queried:
                skip = False
            else:
                skip = True
        except SraLink.DoesNotExist:
            uid = None
            url = '{0}={1}'.format(ESEARCH, experiment.experiment_accession)
            while not uid:
                soup = self.cook_soup(url)
                try:
                    uid = soup.findAll('id')[0].get_text()
                except IndexError:
                    print("Get UID again...")
                    time.sleep(0.33)
            with transaction.atomic():
                obj = SraLink.objects.create(experiment_accession=experiment,
                                             uid=uid)

        return [obj, skip]

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

    def get_pubmed_info(self, pmid, user):
        """Fetch info (abstract, authors, etc...) related to pubmed id."""
        tag_name = f'PMID:{pmid}'
        created = False
        try:
            publication = Publication.objects.get(pmid=pmid)
            tag, created = Tag.objects.get_or_create(
                user=user, tag=tag_name, comment=publication.title
            )
            return [publication, tag, False]
        except Publication.DoesNotExist:
            url = '{0}={1}'.format(EFETCH, pmid)
            soup = self.cook_soup(url)

            authors = [self.get_author_name(a) for a in soup.findAll('author')]
            ids = [self.get_article_id(a) for a in soup.find_all('articleid')]
            keyword_items = ['keyword', 'descriptorname', 'qualifiername']
            keywords = set(
                [i.get_text() for i in soup.find_all(keyword_items)]
            )
            publication = self.insert_publication(pmid, {
                'authors': ';'.join(authors),
                'title': soup.find('articletitle').get_text(),
                'abstract': soup.find('abstracttext').get_text(),
                'reference_ids': ';'.join(ids),
                'keywords': ';'.join(list(keywords))
            })
            tag, created = Tag.objects.get_or_create(
                user=user, tag=tag_name, comment=publication.title
            )
            created = True
        return [publication, tag, True]
