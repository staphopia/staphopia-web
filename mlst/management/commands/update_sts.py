""" Update S. aureus sequence types. """
import urllib2

from django.core.mail import EmailMessage
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from mlst.models import SequenceTypes


class Command(BaseCommand):

    """ Update S. aureus sequence types. """

    help = 'Update S. aureus sequence types.'

    @transaction.atomic
    def handle(self, *args, **opts):
        """ Update S. aureus sequence types. """
        data = urllib2.urlopen("http://pubmlst.org/data/profiles/saureus.txt")

        if data is not None:
            column_names = []
            for line in data:
                line = line.rstrip()
                cols = line.split('\t')
                if cols[0] == 'ST':
                    column_names = [c.replace('_', '') for c in cols]
                    column_names[0] = 'st'
                else:
                    st, created = SequenceTypes.objects.update_or_create(**{
                        column_names[0]: cols[0],
                        column_names[1]: cols[1],
                        column_names[2]: cols[2],
                        column_names[3]: cols[3],
                        column_names[4]: cols[4],
                        column_names[5]: cols[5],
                        column_names[6]: cols[6],
                        column_names[7]: cols[7],
                    })
            print 'Total STs: {0}'.format(SequenceTypes.objects.count())

            # Email Admin with Update
            labrat = "Staphopia's Friendly Robot <usa300@staphopia.com>"
            subject = '[Staphopia MLST Update] - MLST info has been updated.'
            message = 'Total STs: {0}'.format(
                SequenceTypes.objects.count()
            )
            recipients = ['admin@staphopia.com', 'robert.petit@emory.edu']
            email = EmailMessage(subject, message, labrat, recipients)
            email.send(fail_silently=False)
        else:
            raise CommandError('Unable to retrieve updated STs, try again '
                               'later?')
