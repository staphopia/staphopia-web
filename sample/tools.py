"""
Useful functions associated with sample.

To use:
from sample.tools import UTIL1, UTIL2, etc...
"""
import os

from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from sample.models import Sample, Program, Tag, ToTag


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


def file_exists(file, directory, sample):
    if '{1}' in file:
        file = file.format(directory, sample)
    else:
        file = file.format(directory)
    try:
        target = os.path.abspath(os.path.realpath(file))
        return os.path.exists(target)
    except OSError:
        return False


def get_files(directory, sample):

    fq = file_exists('{0}/illumina-cleanup/{1}.cleanup.fastq.gz',
                     directory, sample)
    fq_r1 = file_exists('{0}/illumina-cleanup/{1}_R1.cleanup.fastq.gz',
                        directory, sample)
    fq_r2 = file_exists('{0}/illumina-cleanup/{1}_R2.cleanup.fastq.gz',
                        directory, sample)

    if fq_r1 and fq_r2:
        return get_file_list(True)
    elif fq:
        return get_file_list(False)
    else:
        return None


def get_file_list(is_paired):
    if is_paired:
        return {
            'annotation_blastp_sprot': (
                '{0}/annotation/blastp-sprot.json.gz'
            ),
            'annotation_blastp_proteins': (
               '{0}/annotation/blastp-proteins.json.gz'
            ),
            'annotation_blastp_staph': (
                '{0}/annotation/blastp-Staphylococcus.json.gz'
            ),
            'annotation_contigs': '{0}/annotation/{1}-contigs.txt',
            'annotation_genes': '{0}/annotation/{1}.ffn.gz',
            'annotation_gff': '{0}/annotation/{1}.gff.gz',
            'annotation_proteins': '{0}/annotation/{1}.faa.gz',

            'assembly_contigs': '{0}/assembly/{1}.contigs.fasta.gz',
            'assembly_contig_stats': '{0}/assembly/{1}.contigs.json',
            'assembly_graph': '{0}/assembly/{1}.assembly_graph.fastg.gz',
            'assembly_scaffolds': '{0}/assembly/{1}.scaffolds.fasta.gz',
            'assembly_scaffold_stats': '{0}/assembly/{1}.scaffolds.json',

            'cgmlst_mentalist': '{0}/mlst/mentalist/cgmlst.txt',

            'fastq_adapter': '{0}/illumina-cleanup/{1}.adapter.fastq.json',
            'fastq_cleanup': '{0}/illumina-cleanup/{1}.cleanup.fastq.json',
            'fastq_ecc': '{0}/illumina-cleanup/{1}.post-ecc.fastq.json',
            'fastq_original': '{0}/illumina-cleanup/{1}.original.fastq.json',
            'fastq_r1': '{0}/illumina-cleanup/{1}_R1.cleanup.fastq.gz',
            'fastq_r2': '{0}/illumina-cleanup/{1}_R2.cleanup.fastq.gz',
            'fastq_md5': '{0}/illumina-cleanup/{1}.cleanup.md5',

            'kmer': '{0}/kmer/{1}.jf',

            'mlst_ariba_assembled_genes': (
                '{0}/mlst/ariba/assembled_genes.fa.gz'
            ),
            'mlst_ariba_assemblies': '{0}/mlst/ariba/assemblies.fa.gz',
            'mlst_ariba_report': '{0}/mlst/ariba/report.tsv',
            'mlst_ariba_mlst_report': '{0}/mlst/ariba/mlst_report.tsv',
            'mlst_ariba_assembled_seqs': '{0}/mlst/ariba/assembled_seqs.fa.gz',
            'mlst_ariba_debug_report': '{0}/mlst/ariba/debug.report.tsv',
            'mlst_ariba_details': '{0}/mlst/ariba/mlst_report.details.tsv',
            'mlst_blastn': '{0}/mlst/mlst-blastn.json',
            'mlst_mentalist': '{0}/mlst/mentalist/mlst.txt',

            'plasmid_contigs': '{0}/plasmids/{1}.contigs.fasta.gz',
            'plasmid_contig_stats': '{0}/plasmids/{1}.contigs.json',
            'plasmid_graph': '{0}/plasmids/{1}.assembly_graph.fastg.gz',
            'plasmid_scaffolds': '{0}/plasmids/{1}.scaffolds.fasta.gz',
            'plasmid_scaffold_stats': '{0}/plasmids/{1}.scaffolds.json',

            'resistance_assembled_genes': (
                '{0}/resistance/assembled_genes.fa.gz'
            ),
            'resistance_assemblies': '{0}/resistance/assemblies.fa.gz',
            'resistance_report': '{0}/resistance/report.tsv',
            'resistance_assembled_seqs': '{0}/resistance/assembled_seqs.fa.gz',
            'resistance_debug_report': '{0}/resistance/debug.report.tsv',
            'resistance_clusters': '{0}/resistance/log.clusters.gz',

            'sccmec_coverage': '{0}/sccmec/cassette-coverages.gz',
            'sccmec_primers': '{0}/sccmec/primers.json',
            'sccmec_proteins': '{0}/sccmec/proteins.json',
            'sccmec_subtypes': '{0}/sccmec/subtypes.json',

            'variants': '{0}/variants/{1}.variants.vcf.gz',

            'virulence_assembled_genes': '{0}/virulence/assembled_genes.fa.gz',
            'virulence_assemblies': '{0}/virulence/assemblies.fa.gz',
            'virulence_report': '{0}/virulence/report.tsv',
            'virulence_assembled_seqs': '{0}/virulence/assembled_seqs.fa.gz',
            'virulence_debug_report': '{0}/virulence/debug.report.tsv',
            'virulence_clusters': '{0}/virulence/log.clusters.gz',

            'timeline': '{0}/staphopia-timeline.html'
        }
    else:
        return {
            'annotation_blastp_sprot': (
                '{0}/annotation/blastp-sprot.json.gz'
            ),
            'annotation_blastp_proteins': (
               '{0}/annotation/blastp-proteins.json.gz'
            ),
            'annotation_blastp_staph': (
                '{0}/annotation/blastp-Staphylococcus.json.gz'
            ),
            'annotation_contigs': '{0}/annotation/{1}-contigs.txt',
            'annotation_genes': '{0}/annotation/{1}.ffn.gz',
            'annotation_gff': '{0}/annotation/{1}.gff.gz',
            'annotation_proteins': '{0}/annotation/{1}.faa.gz',

            'assembly_contigs': '{0}/assembly/{1}.contigs.fasta.gz',
            'assembly_contig_stats': '{0}/assembly/{1}.contigs.json',
            'assembly_graph': '{0}/assembly/{1}.assembly_graph.fastg.gz',
            'assembly_scaffolds': '{0}/assembly/{1}.scaffolds.fasta.gz',
            'assembly_scaffold_stats': '{0}/assembly/{1}.scaffolds.json',

            'cgmlst_mentalist': '{0}/mlst/mentalist/cgmlst.txt',

            'fastq_adapter': '{0}/illumina-cleanup/{1}.adapter.fastq.json',
            'fastq_cleanup': '{0}/illumina-cleanup/{1}.cleanup.fastq.json',
            'fastq_ecc': '{0}/illumina-cleanup/{1}.post-ecc.fastq.json',
            'fastq_original': '{0}/illumina-cleanup/{1}.original.fastq.json',
            'fastq_r1': '{0}/illumina-cleanup/{1}.cleanup.fastq.gz',
            'fastq_md5': '{0}/illumina-cleanup/{1}.cleanup.md5',

            'kmer': '{0}/kmer/{1}.jf',

            'mlst_blastn': '{0}/mlst/mlst-blastn.json',
            'mlst_mentalist': '{0}/mlst/mentalist/mlst.txt',

            'plasmid_contigs': '{0}/plasmids/{1}.contigs.fasta.gz',
            'plasmid_contig_stats': '{0}/plasmids/{1}.contigs.json',
            'plasmid_graph': '{0}/plasmids/{1}.assembly_graph.fastg.gz',
            'plasmid_scaffolds': '{0}/plasmids/{1}.scaffolds.fasta.gz',
            'plasmid_scaffold_stats': '{0}/plasmids/{1}.scaffolds.json',

            'sccmec_coverage': '{0}/sccmec/cassette-coverages.gz',
            'sccmec_primers': '{0}/sccmec/primers.json',
            'sccmec_proteins': '{0}/sccmec/proteins.json',
            'sccmec_subtypes': '{0}/sccmec/subtypes.json',

            'variants': '{0}/variants/{1}.variants.vcf.gz',

            'timeline': '{0}/staphopia-timeline.html'
        }


def test_files_exist(directory, sample, files, optional=False):
    """Read a dict of files, and test if they exist."""
    missing = []
    full_path = {'plasmid': True}
    for key, file in files.items():
        path = directory
        if key == 'timeline':
            path = path.replace('/analyses', '')

        if file_exists(file, path, sample):
            full_path[key] = file
        else:
            if key == 'plasmid':
                full_path['plasmid'] = False
            else:
                missing.append(file)

    if len(missing) and not optional:
        raise RuntimeError(
            'Required files are missing.\nMissing Files...\n{0}'.format(
                '\n'.join(missing)
            )
        )

    return [full_path, missing]


def print_analysis_status(sample, found_files, missing_file,
                          print_incomplete=False):
    if len(missing_file):
        if print_incomplete:
            if print_incomplete:
                print('{0}, missing files...'.format(sample))
                for line in missing_file:
                    print('\t{0}'.format(line))
        print('{0}\tINCOMPLETE'.format(sample))
    elif not found_files and not missing_file:
        print('{0}\tINCOMPLETE MISSING FASTQ'.format(sample))
    else:
        print('{0}\tOK'.format(sample))


def get_analysis_status(sample, sample_directory, optional=False):
    directory = '{0}/analyses'.format(sample_directory)
    files = get_files(directory, sample)
    if files:
        return test_files_exist(directory, sample, files, optional=optional)
    else:
        return [False, False]


def handle_new_sample(sample_info, username, fastq_md5, skip_existing=False,
                      force=False, project_info=None):
    from django.contrib.auth.models import User
    # Get User
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise CommandError('user: {0} does not exist'.format(username))

    # Get FASTQ MD5
    fq_md5sum = None
    with open(fastq_md5, 'r') as fh:
        for line in fh:
            fq_md5sum = line.rstrip()

    # Test if results already inserted
    sample = None
    try:
        sample = Sample.objects.get(md5sum=fq_md5sum)
        print("Found existing sample: {0} ({1})".format(
            sample.sample_tag, sample.md5sum
        ))
        if skip_existing:
            print("\tSkip reloading existing data.")
        elif not force:
            raise CommandError(
                'Sample exists, please use --force to use it.'
            )
        else:
            Sample.objects.filter(md5sum=fq_md5sum).update(
                sample_tag=sample_info['sample_tag'],
                is_paired=sample_info['is_paired'],
                is_public=sample_info['is_public'],
                is_published=sample_info['is_published']
            )
    except Sample.DoesNotExist:
        # Create new sample
        try:
            sample = Sample.objects.create(
                user=user,
                sample_tag=sample_info['sample_tag'],
                md5sum=fq_md5sum,
                is_paired=sample_info['is_paired'],
                is_public=sample_info['is_public'],
                is_published=sample_info['is_published']
            )
            print("Created new sample: {0} {1}".format(sample.id,
                                                       sample.sample_tag))
        except IntegrityError as e:
            raise CommandError(
                'Error, unable to create Sample object. {0}'.format(e)
            )

    if project_info:
        tag = create_tag(user, project_info['tag'], project_info['comment'])
        try:
            totag, created = ToTag.objects.get_or_create(
                sample=sample, tag=tag
            )
            if created:
                print("Project tag '{0}' saved".format(project_info['tag']))
        except IntegrityError as e:
            raise CommandError(
                'Error, unable to link Sample to Tag. {0}'.format(e)
            )
