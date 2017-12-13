"""Insert the results of sample analysis into the database."""
import os
import sys

from django.core.management.base import BaseCommand

from sample.tools import (
    check_md5_existence, get_analysis_status, get_sample_by_name,
    handle_sample, insert_md5s
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
        experiment = os.path.basename(opts['sample_dir'])
        files, missing = get_analysis_status(experiment, opts['sample_dir'])

        # Update or create sample fields
        sample_info = {
            'name': experiment,
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

        # Get FASTQ MD5
        md5s = []
        with open(files['fastq_original_md5'], 'r') as fh:
            for line in fh:
                md5s.append(line.rstrip().split(" ")[0])

        # Check if MD5 exists
        sample_md5 = check_md5_existence(md5s)

        # Check if sample exists
        sample = get_sample_by_name('ena', experiment)

        if sample and sample_md5:
            if sample.id != sample_md5:
                # Error, trying to update a sample when MD5 exists for another
                # sample
                print(f'MD5s exist for sample {sample_md5}, but sample '
                       '{sample.id} is being updated. Cannot continue.',
                       file=sys.err)
                sys.exit(1)

        sample = handle_sample(
            sample_info, 'ena', force=True, project_info=project_info
        )

        if not sample_md5:
            insert_md5s(sample, md5s)
