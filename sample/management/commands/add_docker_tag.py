"""Add a docker image tag to the database."""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand

from sample.models import Docker


class Command(BaseCommand):
    """Add a docker image tag to the database."""

    help = 'Add a docker image tag to the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('repo', metavar='REPO',
                            help=('Docker repository name'))
        parser.add_argument('tag', metavar='TAG',
                            help=('Tag of the Docker image used in analysis'))
        parser.add_argument('sha256', metavar='SHA256',
                            help=('SHA256 id of the Docker image'))

    @transaction.atomic
    def handle(self, *args, **opts):
        """Add a docker image tag to the database."""
        try:
            Docker.objects.create(
                repo=opts['repo'],
                tag=opts['tag'],
                sha256=opts['sha256']
            )
            print(f'Added {opts["repo"]}:{opts["tag"]}')
        except IntegrityError:
            print(f'{opts["repo"]}:{opts["tag"]} already exists.')
