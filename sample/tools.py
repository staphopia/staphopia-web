"""
Useful functions associated with sample.

To use:
from sample.tools import UTIL1, UTIL2, etc...
"""
import os

from django.core.management.base import CommandError

from sample.models import MetaData


def validate_analysis(directory):
    """
    Walk through a sample directory to check for required files.

    Required Files
    ./SAMPLE.cleanup.fastq.stats
    ./SAMPLE.original.fastq.stats

    ./SAMPLE.contigs.stats
    ./SAMPLE.scaffolds.stats

    ./mlst/blastn/blastn.txt
    ./mlst/srst2/srst2__mlst__Staphylococcus_aureus__results.txt

    ./sccmec/cassettes/sccmec.coverage.gz

    ./annotation/SAMPLE.gff.gz
    ./annotation/SAMPLE.fna.gz
    ./annotation/SAMPLE.ffn.gz
    ./annotation/SAMPLE.faa.gz

    ./SAMPLE.variants.vcf.gz
    """
    files = {
        'stats_filter': None,
        'stats_original': None,
        'contigs': None,
        'scaffolds': None,
        'mlst_blast': None,
        'mlst_srst2': None,
        'sccmec_coverage': None,
        'annotation': {
            'genes': None,
            'proteins': None,
            'contigs': None,
            'gff': None,
        },
        'variants': None,
        'missing': []
    }

    message = {
        'stats_filter': "Missing ./SAMPLE.cleanup.fastq.stats",
        'stats_original': "Missing ./SAMPLE.original.fastq.stats",
        'contigs': "Missing ./SAMPLE.contigs.stats",
        'scaffolds': "Missing ./SAMPLE.scaffolds.stats",
        'mlst_blast': "Missing ./mlst/blastn/blastn.txt",
        'mlst_srst2': ("Missing ./mlst/srst2/srst2__mlst__Staphylococcus_"
                       "aureus__results.txt"),
        'sccmec_coverage': "Missing ./sccmec/cassettes/sccmec.coverage.gz",
        'annotation': {
            'genes': "Missing ./annotation/SAMPLE.gff.gz",
            'proteins': "Missing ./annotation/SAMPLE.fna.gz",
            'contigs': "Missing ./annotation/SAMPLE.ffn.gz",
            'gff': "Missing ./annotation/SAMPLE.faa.gz",
        },
        'variants': "Missing ./SAMPLE.variants.vcf.gz",
    }

    for root, dirs, filelist in os.walk(directory, topdown=False):
        for name in filelist:
            file = os.path.join(root, name)
            if "cleanup.fastq.stats" in name:
                files['stats_filter'] = file
            elif "original.fastq.stats" in name:
                files['stats_original'] = file
            elif "contigs.stats" in name:
                files['contigs'] = file
            elif "scaffolds.stats" in name:
                files['scaffolds'] = file
            elif "mlst/blastn/blastn.txt" in file:
                files['mlst_blast'] = file
            elif "srst2__mlst__Staphylococcus_aureus__results.txt" in name:
                files['mlst_srst2'] = file
            elif "sccmec.coverage.gz" in name:
                files['sccmec_coverage'] = file
            elif "gff.gz" in name:
                files['annotation']['gff'] = file
            elif "fna.gz" in name:
                files['annotation']['contigs'] = file
            elif "ffn.gz" in name:
                files['annotation']['genes'] = file
            elif "faa.gz" in name:
                files['annotation']['proteins'] = file
            elif "variants.vcf.gz" in name:
                files['variants'] = file

    for key, val in files.items():
        if 'missing' not in key:
            if not val:
                files['missing'].append(message[key])

            if key == "annotation":
                if not files[key]['genes']:
                    files['missing'].append(message[key]['genes'])
                if not files[key]['proteins']:
                    files['missing'].append(message[key]['proteins'])
                if not files[key]['contigs']:
                    files['missing'].append(message[key]['contigs'])
                if not files[key]['gff']:
                    files['missing'].append(message[key]['gff'])

    return files


def get_sample(sample_tag):
    """Return MetaData object is it exists, else raise error."""
    try:
        return MetaData.objects.get(sample_tag=sample_tag)
    except MetaData.DoesNotExist:
        raise CommandError('sample_tag: {0} does not exist'.format(sample_tag))


def create_sample_tag(user, sample_tag=None, force=False):
    """
    Get or create a sample tag for a user.

    An error is raised if the sample tag already exists for the use, unless
    force is set to True.
    """
    if sample_tag:
        try:
            MetaData.objects.get(user=user, sample_tag=sample_tag)
            if not force:
                raise CommandError((
                    'A sample is already associated with {0}. Will not use'
                    ' {0} unless --force is given, exiting.').format(
                    sample_tag
                ))
            else:
                print('Focibly using the existing sample_tag {0}'.format(
                    sample_tag
                ))
        except MetaData.DoesNotExist:
            pass
    else:
        num_samples = MetaData.objects.filter(user=user).count()
        sample_tag = '{0}_{1}'.format(
            user.username,
            str(num_samples + 1).zfill(6)
        )

    return sample_tag
