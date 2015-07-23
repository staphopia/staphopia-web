""" Create new sample for custom sample. """
import json

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from samples.models import Sample


class Command(BaseCommand):

    """ Create new sample for custom sample. """

    help = 'Create new sample for custom data.'

    def add_arguments(self, parser):
        parser.add_argument('user', metavar='USERNAME',
                            help=('User name for the owner of the sample.'))
        parser.add_argument('--strain', type=str, default="",
                            help=('Strain name of the input sample.'))
        parser.add_argument('--is_paired', action='store_true',
                            help='Sample contains paired reads.')
        parser.add_argument('--comment', type=str, default="",
                            help='Any comments about the sample.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """ Create new sample for custom sample. """
        # Required Parameters
        try:
            user = User.objects.get(username=opts['user'])
        except User.DoesNotExist:
            raise CommandError('user: {0} does not exist'.format(
                opts['user']
            ))

        # Create sample_tag
        num_samples = Sample.objects.filter(user=user).count()
        sample_tag = '{0}_{1}'.format(
            user.username,
            str(num_samples + 1).zfill(6)
        )

        # Create new sample
        sample = Sample(
            user=user,
            sample_tag=sample_tag,
            strain=opts['strain'],
            is_paired=opts['is_paired'],
            comments=opts['comment']
        )
        sample.save()

        print json.dumps({
            'sample_id': sample.pk,
            'sample_tag': sample.sample_tag,
            'strain': sample.strain,
            'is_paired': sample.is_paired,
            'comment': sample.comments
        })
