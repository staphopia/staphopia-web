""" Update SRST2 tale to new Schema (9/16/2015). """
import re

from django.db import transaction
from django.core.management.base import BaseCommand

from mlst.models import Srst2


class Command(BaseCommand):
    """ Update SRST2 tale to new Schema (9/16/2015). """
    help = 'Update SRST2 tale to new Schema (9/16/2015).'

    @transaction.atomic
    def handle(self, *args, **opts):
        """ Insert results to database. """
        i = 0
        total = Srst2.objects.all().count()
        for row in Srst2.objects.all():
            st_stripped, is_exact = self.determine_st(row.st_original)
            row.st_stripped = st_stripped
            row.is_exact = is_exact
            row.save()
            i += 1
            if i % 100 == 0:
                print '{0} of {1} completed.'.format(i, total)

    def determine_st(self, st):
        exact_st = re.compile('^(\d+)$')
        likely_st = re.compile('^(\d+)(.*)$')

        if exact_st.match(st):
            # Exact match
            return [int(st), True]
        elif likely_st.match(st):
            # Good idea, there is either mismatches or uncertainity
            m = likely_st.match(st)
            return [int(m.group(1)), False]
        else:
            # Unable to determine ST
            return [0, False]
