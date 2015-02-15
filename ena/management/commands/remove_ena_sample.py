""" Create a new Sample for an ENA experiement. """
import sys
import json

from optparse import make_option

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from ena.models import Experiment, ToSample, Run
from samples.models import Sample


class Command(BaseCommand):

    """ Create new sample for ENA data. """

    help = 'Return the paired status of an experiment accession'

    option_list = BaseCommand.option_list + (
        make_option('--experiment', dest='experiment',
                    help='File of Experiment accessions to be removed.'),
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        """ Create new sample for ENA data. """
        # Required Parameters
        if not opts['experiment']:
            raise CommandError('--experiment is requried')

        fh = open(opts['experiment'], 'r')
        for line in fh:
            line = line.rstrip()
            print "Removing {0}".format(line)
            d = Sample.objects.get(sample_tag=line).delete()

        fh.close()
