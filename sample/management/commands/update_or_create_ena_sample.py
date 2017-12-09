"""Insert the results of sample analysis into the database."""
import os

from django.core.management.base import BaseCommand

from sample.tools import (
    get_analysis_status, handle_new_sample, update_ena_md5sum
)

from ena.models import Experiment, Study


class Command(BaseCommand):
    """Insert the results of sample analysis into the database."""

    help = 'Insert the results of sample analysis into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('sample_dir', metavar='SAMPLE_DIRECTORY',
                            help=('User name for the owner of the sample.'))

    def handle(self, *args, **opts):
        """Insert the results of sample analysis into the database."""

        # Validate all files are present, will cause error if files are missing
        print("Validating required files are present...")
        experiment = os.path.basename(opts['sample_dir'])
        files, missing = get_analysis_status(experiment, opts['sample_dir'])

        # Get FASTQ MD5
        md5sum = None
        print(files['fastq_md5'])
        with open(files['fastq_md5'], 'r') as fh:
            for line in fh:
                md5sum = line.rstrip()

        # Update existing samples
        update_ena_md5sum('ena', experiment, md5sum)

        sample_info = {
            'sample_tag': experiment,
            'is_paired': True if 'fastq_r2' in files else False,
            'is_public': True,
            'is_published': False
        }

        # Create tag pointing to study accessions
        project_info = None
        try:
            experiment_obj = Experiment.objects.get(
                experiment_accession=experiment
            )
            project_info = {
                'tag': experiment_obj.study_accession.study_accession,
                'comment': experiment_obj.study_accession.study_title
            }
        except Experiment.DoesNotExist:
            print('{0} does not exist.'.format(opts['experiment']))

        handle_new_sample(
            sample_info, 'ena', md5sum, force=True, project_info=project_info
        )
