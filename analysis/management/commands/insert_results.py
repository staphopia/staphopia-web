'''

'''
import json
import os.path
from optparse import make_option

from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from samples.models import Sample
from analysis.models import *

class Command(BaseCommand):
    help = 'Insert the analysis results into the database.'

    option_list = BaseCommand.option_list + (
        make_option('--sample_id', dest='sample_id',
                    help='Sample ID for which the data is for'),
        make_option('--table', dest='table',
                    help=('Table (fastq_original, fastq_clean, assembly, mlst, '
                          'sccmec, resistance, virulence, snp) to insert data '
                          'into ')),
        make_option('--input', dest='input',
                    help='JSON formated file containing data to be inserted'),
        make_option('--pipeline_version', dest='pipeline_version',
                    help='Version of the pipeline used in this analysis.'),
        make_option('--debug', action='store_true', dest='debug', 
                    default=False, help='Will not write to the database'),
        
        )

    def handle(self, *args, **options):
        # Required Parameters
        if not options['sample_id']:
            raise CommandError('--sample_id is requried')
        elif not options['table']:
            raise CommandError('--table is requried')
        elif not options['input']:
            raise CommandError('--input is requried')
        elif not options['pipeline_version']:
            raise CommandError('--pipeline_version is requried')
        
        # Sample 
        try:
            sample = Sample.objects.get(pk=options['sample_id'])
        except Sample.DoesNotExist:
            raise CommandError('sample_id: {0} does not exist'.format(options['sample_id']))
        
        # Database Table
        accepted_tables = ['fastq_original', 'fastq_clean', 'assembly_contigs', 
                           'assembly_scaffolds', 'mlst', 'sccmec', 'resistance',
                           'virulence', 'snp']
        if options['table'] not in accepted_tables:
            raise CommandError(
                'Unknown table: {0}. Use one of the following: {1}'.format(
                    options['table'], 
                    ', '.join(accepted_tables)
                )
            )
        
        # Input File
        if not os.path.exists(options['input']):
            raise CommandError('{0} does not exist'.format(options['input']))

        # Pipeline Version
        try:
            module = options['table'].split('_')[0]
            pipeline_version = PipelineVersions.objects.get_or_create(
                module=module, 
                version=options['pipeline_version']
            )[0]
        except PipelineVersions.DoesNotExist:
            raise CommandError('Error saving pipeline information')
        
        # JSON input 
        try:
            with open(options['input'], 'r') as f:
                json_data = json.loads(f.readline().rstrip())
        except ValueError as e:
            raise CommandError('{0} is not valid JSON'.format(options['input']))            

        # Everything checks out, load it up
        table_object = None
        if options['table'].startswith('fastq'):
            is_original = False if options['table'] == 'fastq_clean' else True
            table_object = FastqStats(
                sample=sample, 
                is_original=is_original, 
                rank=self.get_rank(json_data),
                version_id=pipeline_version.pk,
                **json_data
            )
        elif options['table'].startswith('assembly'):
            is_scaffolds = False if options['table'] == 'assembly_contigs' else True
            table_object = AssemblyStats(
                sample=sample, 
                is_scaffolds=is_scaffolds,
                version_id=pipeline_version.pk,
                **json_data
            )
        elif options['table'] == 'mlst':
            pass
        elif options['table'] == 'sccmec':
            pass
        elif options['table'] == 'resistance':
            pass
        elif options['table'] == 'virulence':
            pass
        elif options['table'] == 'snp':
            pass
            
        if not options['debug']:
            try:
                table_object.save()
                print 'Saved results'
            except IntegrityError as e:
                raise CommandError(('{0}. Either the data is already in '
                                    'there or the pipeline version should '
                                    'be updated.').format(e)) 
            
        else:
            print 'Did not save results'
        
    def get_rank(self, data):
        if data['mean_read_length'] >= 75:
            if data['coverage'] >= 45 and data['qual_mean'] >= 30:
                return 3
            elif data['coverage'] >= 20 and data['qual_mean'] >= 20:
                return 2
            else:
                return 1
        else:
            return 1

            