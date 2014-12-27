'''
    Robert Petit

    Reads output from EBI's data warehouse API and inserts the data into
    proper tables.
'''
import sys
import os.path
from optparse import make_option

from django.core.mail import EmailMessage
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

import ena.models as ena

class Command(BaseCommand):
    help = 'Insert ENA data information into the database.'

    option_list = BaseCommand.option_list + (
        make_option('--study', dest='study',
                    help='A table of study information.'),
        make_option('--experiment', dest='experiment',
                    help='A table of experiment information.'),
        make_option('--run', dest='run',
                    help='A table of run information'),
        make_option('--empty', dest='empty', action='store_true',
                    help='Empty each of the tables'),
        make_option('--debug', action='store_true', dest='debug',
                    default=False, help='Will not write to the database'),
        )

    def handle(self, *args, **options):
        # Required Parameters
        if not options['empty']:
            if not options['study']:
                raise CommandError('--study is requried')
            elif not options['experiment']:
                raise CommandError('--experiment is requried')
            elif not options['run']:
                raise CommandError('--run is requried')
        else:
            ena.Study.objects.all().delete()
            ena.Experiment.objects.all().delete()
            ena.Run.objects.all().delete()
            sys.exit()

        # Test input files
        if not os.path.exists(options['study']):
            raise CommandError('{0} does not exist'.format(options['study']))
        elif not os.path.exists(options['experiment']):
            raise CommandError('{0} does not exist'.format(options['experiment']))
        elif not os.path.exists(options['run']):
            raise CommandError('{0} does not exist'.format(options['run']))

        # Get primary keys for each table
        self.pks = {
            'Study':self.get_primary_keys(ena.Study, 'study_accession'),
            'Experiment':self.get_primary_keys(ena.Experiment, 'experiment_accession'),
            'Run':self.get_primary_keys(ena.Run, 'run_accession'),
        }

        # Insert Studies
        studies_created = self.insert(options['study'], ena.Study, 'Study',
                                      'study_accession', None)

        # Insert Experiments
        exps_created = self.insert(options['experiment'], ena.Experiment,
                                   'Experiment', 'experiment_accession',
                                   'study_accession')

        # Insert Runs
        runs_created = self.insert(options['run'], ena.Run, 'Run',
                                   'run_accession', 'experiment_accession')

        print 'ENA Data Summary (new additions in parentheses)'
        print 'Studies: {0} ({1})'.format(
            ena.Study.objects.count(),
            studies_created
        )
        print 'Experiments: {0} ({1})'.format(
            ena.Experiment.objects.count(),
            exps_created
        )
        print 'Runs: {0} ({1})'.format(
            ena.Run.objects.count(),
            runs_created
        )

        # Email Admin with Update
        labrat = "Staphopia's Friendly Robot <usa300@staphopia.com>"
        subject = '[Staphopia ENA Update] - ENA info has been updated.'
        message = (
            "Project information from ENA has been updated.\n\n"
            "New ENA Additions (total in parentheses)\n"
            "Studies: {0} ({1})\n"
            "Experiments: {2} ({3})\n"
            "Runs: {4} ({5})\n\n"
        ).format(
            studies_created,
            ena.Study.objects.count(),
            exps_created,
            ena.Experiment.objects.count(),
            runs_created,
            ena.Run.objects.count()
        )
        recipients = ['admin@staphopia.com', 'robert.petit@emory.edu']
        email = EmailMessage(subject, message, labrat, recipients)
        email.send(fail_silently=False)


    def get_primary_keys(self, ena_obj, pk):
        '''
            Create a list of all the primary keys in a table, prevents multiple
            queries testing if a primary key exists
        '''
        return list(ena_obj.objects.values_list(pk, flat=True).order_by(pk))

    def test_foreign_key(self, ena_obj, table, value):
        '''
            Make sure the foreign key exists before inserting a row
        '''
        try:
            return ena_obj.objects.get(pk=value)
        except ena_obj.DoesNotExist:
            raise CommandError('EXCEPTION: {0}, Table:{1}, Value:{2}'.format(
                'Foreign Key Missing', table, value
            ))

    @transaction.atomic
    def insert(self, input_file, ena_obj, table, primary_key, foreign_key):
        '''
            Insert new studies into the Study table
        '''
        count = 0
        col_names = False
        fh = open(input_file, 'r')
        for line in fh:
            col_vals = line.rstrip().split('\t')
            if not col_names:
                col_names = col_vals
            else:
                cols = dict(zip(col_names, col_vals))

                # Test if entry exists, if not create
                if cols[primary_key] not in self.pks[table]:
                    if table == 'Experiment':
                        cols[foreign_key] = self.test_foreign_key(
                            ena.Study, table, cols[foreign_key]
                        )
                    elif table == 'Run':
                        cols['is_paired'] = True if int(cols['is_paired']) == 1 else False
                        cols[foreign_key] = self.test_foreign_key(
                            ena.Experiment, table, cols[foreign_key]
                        )

                    row = ena_obj(**cols)
                    row.save()
                    count += 1
        fh.close()

        return count
