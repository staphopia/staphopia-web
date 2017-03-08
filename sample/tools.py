"""
Useful functions associated with sample.

To use:
from sample.tools import UTIL1, UTIL2, etc...
"""
import os

from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from sample.models import Sample, Program, Tag


def test_files(directory, sample_tag, files, optional=False,
               print_incomplete=False):
    """Read a dict of files, and test if they exist."""
    missing = []
    full_path = {}
    for key, file in files.items():
        if '{1}' in file:
            file = file.format(directory, sample_tag)
        else:
            file = file.format(directory)

        if os.path.exists(file):
            full_path[key] = file
        else:
            missing.append(file)

    if len(missing):
        if not optional:
            raise CommandError(
                'Required files are missing.\nMissing Files...\n{0}'.format(
                    '\n'.join(missing)
                )
            )
        else:
            if print_incomplete:
                print('{0}, missing files...'.format(sample_tag))
                for line in missing:
                    print('\t{0}'.format(line))
            return None
    else:
        return full_path


def validate_time(directory):
    """Test if optional runtime files exist."""
    return test_files(directory, None, {
        'illumina_assembly': '{0}/logs/time/illumina_assembly.txt',
        'predict_mlst': '{0}/logs/time/predict_mlst.txt',
        'fastq_cleanup': '{0}/logs/time/fastq_cleanup.txt',
        'kmer_analysis': '{0}/logs/time/kmer_analysis.txt',
        'submit_job': '{0}/logs/time/submit_job.txt',
        'predict_sccmec': '{0}/logs/time/predict_sccmec.time',
        'call_variants': '{0}/logs/time/call_variants.txt',
        'annotation': '{0}/logs/time/annotation.txt'
    }, optional=True
    )


def validate_analysis(directory, sample_tag, optional=False,
                      print_incomplete=False):
    """Test if required files exist."""
    return test_files('{0}/analyses'.format(directory), sample_tag, {
        # FASTQ
        'stats_filter': '{0}/fastq-stats/{1}.cleanup.fastq.json',
        'stats_original': '{0}/fastq-stats/{1}.original.fastq.json',

        # Assembly
        'contigs': '{0}/assembly/{1}.contigs.json',
        'scaffolds': '{0}/assembly/{1}.scaffolds.json',
        'assembly': '{0}/assembly/{1}.scaffolds.fasta.gz',

        # Plasmid Assembly
        'plasmid-contigs': '{0}/plasmids/{1}.plasmid-contigs.json',
        'plasmid-scaffolds': '{0}/plasmids/{1}.plasmid-scaffolds.json',
        'plasmid-assembly': '{0}/plasmids/{1}.plasmid-scaffolds.fasta.gz',

        # MLST
        'mlst_blast': '{0}/mlst/mlst-blastn.json',
        'mlst_srst2': ('{0}/mlst/srst2__mlst__Staphylococcus_aureus__'
                       'results.txt'),

        # SCCmec
        'sccmec_coverage': '{0}/sccmec/cassette-coverages.gz',
        'sccmec_primers': '{0}/sccmec/primers.json',
        'sccmec_proteins': '{0}/sccmec/proteins.json',
        'sccmec_subtypes': '{0}/sccmec/subtypes.json',

        # Annotation
        'annotation_genes': '{0}/annotation/{1}.ffn.gz',
        'annotation_proteins': '{0}/annotation/{1}.faa.gz',
        'annotation_contigs': '{0}/annotation/{1}-contigs.txt',
        'annotation_gff': '{0}/annotation/{1}.gff.gz',
        'annotation_blastp_sprot': (
            '{0}/annotation/blastp-sprot.json.gz'
        ),
        'annotation_blastp_proteins': (
            '{0}/annotation/blastp-proteins.json.gz'
        ),
        'annotation_blastp_staph': (
            '{0}/annotation/blastp-Staphylococcus-uniref50.json.gz'
        ),

        # Variants
        'variants': '{0}/variants/{1}.variants.vcf.gz',

        # Kmers
        'kmers': '{0}/kmer/{1}.jf',
    }, optional=optional, print_incomplete=print_incomplete)


def get_sample(db_tag):
    """Return Sample object is it exists, else raise error."""
    try:
        return Sample.objects.get(db_tag=db_tag)
    except Sample.DoesNotExist:
        raise CommandError('db_tag: {0} does not exist'.format(db_tag))


def create_tag(user, tag, comment):
    """Create a database tag."""
    try:
        if not comment:
            comment = tag
        tag_obj, created = Tag.objects.get_or_create(
            user=user, tag=tag, comment=comment
        )
        return tag_obj
    except IntegrityError as e:
        raise CommandError('tag creation failed: {0}'.format(e))


def get_program_id(program, version, comments):
    """Add program and version to database."""
    program_obj, created = Program.objects.get_or_create(
        program=program,
        version=version,
        comments=comments
    )

    if created:
        print("Added {0} ({1}) to Program table".format(program, version))

    return program_obj
