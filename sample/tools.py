"""
Useful functions associated with sample.

To use:
from sample.tools import UTIL1, UTIL2, etc...
"""
import os

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from sample.models import Sample, MD5
from tag.models import Tag, ToSample

from staphopia.utils import timeit
from version.tools import get_pipeline_version


@transaction.atomic
def empty_results(table, sid, vid):
    """Empty the results from a table related to a sample and version."""
    cursor = connection.cursor()
    sql = f'DELETE FROM {table} WHERE sample_id={sid} AND version_id={vid};'
    cursor.execute(sql)


def create_tag(user, tag, comment):
    """Create a database tag."""
    try:
        if not comment:
            comment = tag
        tag_obj, created = Tag.objects.get_or_create(
            user=user, tag=tag, comment=comment
        )
        if created:
            print(f'Created new tag: {tag} ({tag_obj.id})')
        return tag_obj
    except IntegrityError as e:
        raise CommandError('tag creation failed: {0}'.format(e))


def get_file_path(file, directory, sample):
    if '{1}' in file:
        file = file.format(directory, sample)
    else:
        file = file.format(directory)

    return os.path.abspath(os.path.realpath(file))


def file_exists(file):
    try:
        return os.path.exists(file)
    except OSError:
        return False


def get_files(directory, sample):
    fq = file_exists(
        get_file_path('{0}/illumina-cleanup/{1}.cleanup.fastq.gz',
                      directory, sample)
    )
    fq_r1 = file_exists(
        get_file_path('{0}/illumina-cleanup/{1}_R1.cleanup.fastq.gz',
                      directory, sample)
    )
    fq_r2 = file_exists(
        get_file_path('{0}/illumina-cleanup/{1}_R2.cleanup.fastq.gz',
                      directory, sample)
    )

    if fq_r1 and fq_r2:
        return get_file_list(True)
    elif fq:
        return get_file_list(False)
    else:
        return None


def test_files_exist(directory, sample, files, optional=False):
    """Read a dict of files, and test if they exist."""
    missing = []
    full_path = {'plasmid': True, 'virulence': True}

    for key, file in files.items():
        path = directory
        if key == 'timeline' or key == 'version':
            path = path.replace('/analyses', '')

        file_path = get_file_path(file, path, sample)
        if file_exists(file_path):
            full_path[key] = file_path
        else:
            if 'plasmid' in key:
                full_path[key] = False
                full_path['plasmid'] = False
            elif 'virulence' in key:
                full_path[key] = False
                full_path['virulence'] = False
            else:
                missing.append(file_path)

    if len(missing) and not optional:
        raise CommandError(
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
        raise CommandError(
            f'Required files missing. Please check {sample_directory} exists.'
        )


def get_user(username):
    from django.contrib.auth.models import User
    # Get User
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise CommandError('user: {0} does not exist'.format(username))

    return user


def get_sample_by_name(username, name):
    """Get a sample instance using the username and name of sample."""
    user = get_user(username)
    sample = False
    try:
        sample = Sample.objects.get(user=user, name=name)
        print(f'Found sample {name} ({sample.id})')
    except Sample.DoesNotExist:
        print(f'Sample {name} does not exist for user {username}')
        pass

    return sample


@transaction.atomic
def check_md5_existence(md5s):
    """Check for MD5 existence, return sample id if it does."""
    exists = False
    for md5sum in md5s:
        try:
            md5 = MD5.objects.get(md5sum=md5sum)
            print(f'MD5 {md5sum} already exists for sample {md5.sample_id}')
            exists = md5.sample_id
        except MD5.DoesNotExist:
            print(f'MD5 {md5sum} not found')
            pass
    return exists


@transaction.atomic
def insert_md5s(sample, md5s):
    for md5 in md5s:
        try:
            MD5.objects.create(sample=sample, md5sum=md5)
            print(f'Inserted md5 {md5} for sample {sample.name}')
        except IntegrityError as e:
            raise CommandError(f'Error, unable to create MD5 object. {e}')


def get_sample(username, name, md5file, sample_info=None, project_info=None):
    """Return Sample object is it exists, else raise error."""
    # Get FASTQ MD5
    md5s = []
    with open(md5file, 'r') as fh:
        for line in fh:
            md5s.append(line.rstrip().split(" ")[0])

    # Check if MD5 exists
    sample_md5 = check_md5_existence(md5s)

    # Check if sample exists
    sample = get_sample_by_name(username, name)

    if sample and sample_md5:
        if sample.id != sample_md5:
            # Error, trying to update a sample when MD5 exists for another
            # sample
            raise CommandError(
                f'MD5s exist for sample {sample_md5}, but sample '
                 '{sample.id} is being updated. Cannot continue.'
            )
            sys.exit(1)
        else:
            return sample
    else:
        # Create a new sample
        sample = handle_sample(
            sample_info, username, force=True, project_info=project_info
        )

        if not sample_md5:
            insert_md5s(sample, md5s)

        return sample


def prep_insert(username, name, directory, optional=False, sample_info=None,
                project_info=None):
    """
    Verify all is good to begin data insert. All files exist, sample exists
    and the version exists.
    """
    print(directory)
    files, missing = get_analysis_status(name, directory, optional=optional)
    sample = get_sample(username, name, files['fastq_original_md5'],
                        sample_info=sample_info, project_info=project_info)
    version = get_pipeline_version(files['version'])

    return [sample, version, files]


@transaction.atomic
def handle_sample(sample_info, username, skip_existing=False, force=False,
                  project_info=None, is_ena=False):
    # Test if results already inserted
    user = get_user(username)
    sample = None
    try:
        # If ena, we can update by user and name incase it already exists
        sample = Sample.objects.get(user=user, name=sample_info['name'])
        print("Found existing sample: {0} ({1})".format(
            sample.name, sample.id
        ))
        if skip_existing:
            print("\tSkip reloading existing data.")
        elif not force:
            raise CommandError(
                'Sample exists, please use --force to use it.'
            )
        else:
            print("Updated sample: {0} {1}".format(sample.id,
                                                   sample.name))
            Sample.objects.filter(user=user, name=sample_info['name']).update(
                name=sample_info['name'],
                is_public=sample_info['is_public'],
                is_published=sample_info['is_published']
            )
    except Sample.DoesNotExist:
        # Create new sample
        try:
            sample = Sample.objects.create(
                user=user,
                name=sample_info['name'],
                is_public=sample_info['is_public'],
                is_published=sample_info['is_published']
            )
            print("Created new sample: {0} {1}".format(sample.id,
                                                       sample.name))
        except IntegrityError as e:
            raise CommandError(
                'Error, unable to create Sample object. {0}'.format(e)
            )

    if project_info:
        tag = create_tag(user, project_info['tag'], project_info['comment'])
        try:
            tosample, created = ToSample.objects.get_or_create(
                sample=sample, tag=tag
            )
            if created:
                print("Project tag '{0}' saved".format(project_info['tag']))
        except IntegrityError as e:
            raise CommandError(
                'Error, unable to link Sample to Tag. {0}'.format(e)
            )

    return sample


def get_file_list(is_paired):
    if is_paired:
        return {
            'annotation_blastp_sprot': (
                '{0}/annotation/blastp-sprot.json.gz'
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

            #'cgmlst_mentalist': '{0}/mlst/mentalist/cgmlst.txt',
            #'cgmlst_mentalist_ties': '{0}/mlst/mentalist/mlst.txt.ties.txt',
            #'cgmlst_mentalist_votes': '{0}/mlst/mentalist/mlst.txt.votes.txt',

            'fastq_adapter': '{0}/illumina-cleanup/{1}.adapter.fastq.json',
            'fastq_cleanup': '{0}/illumina-cleanup/{1}.cleanup.fastq.json',
            'fastq_ecc': '{0}/illumina-cleanup/{1}.post-ecc.fastq.json',
            'fastq_original': '{0}/illumina-cleanup/{1}.original.fastq.json',
            'fastq_r1': '{0}/illumina-cleanup/{1}_R1.cleanup.fastq.gz',
            'fastq_r2': '{0}/illumina-cleanup/{1}_R2.cleanup.fastq.gz',
            'fastq_cleanup_md5': '{0}/illumina-cleanup/{1}.cleanup.md5',
            'fastq_original_md5': '{0}/illumina-cleanup/{1}.original.md5',

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
            #'mlst_mentalist': '{0}/mlst/mentalist/mlst.txt',
            #'mlst_mentalist_ties': '{0}/mlst/mentalist/mlst.txt.ties.txt',
            #'mlst_mentalist_votes': '{0}/mlst/mentalist/mlst.txt.votes.txt',

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
            'resistance_summary': '{0}/resistance/summary.csv',
            'resistance_assembled_seqs': '{0}/resistance/assembled_seqs.fa.gz',
            'resistance_debug_report': '{0}/resistance/debug.report.tsv',

            'sccmec_coverage': '{0}/sccmec/cassette-coverages.gz',
            'sccmec_primers': '{0}/sccmec/primers.json',
            'sccmec_proteins': '{0}/sccmec/proteins.json',
            'sccmec_subtypes': '{0}/sccmec/subtypes.json',

            'variants': '{0}/variants/{1}.variants.vcf.gz',

            'virulence_assembled_genes': '{0}/virulence/assembled_genes.fa.gz',
            'virulence_assemblies': '{0}/virulence/assemblies.fa.gz',
            'virulence_report': '{0}/virulence/report.tsv',
            'virulence_summary': '{0}/virulence/summary.csv',
            'virulence_assembled_seqs': '{0}/virulence/assembled_seqs.fa.gz',
            'virulence_debug_report': '{0}/virulence/debug.report.tsv',
            'virulence_agr_primers': '{0}/agr/primers.json',

            'timeline': '{0}/staphopia-timeline.html',
            'version': '{0}/staphopia-version.txt'
        }
    else:
        return {
            'annotation_blastp_sprot': (
                '{0}/annotation/blastp-sprot.json.gz'
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
            'cgmlst_mentalist_ties': '{0}/mlst/mentalist/mlst.txt.ties.txt',
            'cgmlst_mentalist_votes': '{0}/mlst/mentalist/mlst.txt.votes.txt',

            'fastq_adapter': '{0}/illumina-cleanup/{1}.adapter.fastq.json',
            'fastq_cleanup': '{0}/illumina-cleanup/{1}.cleanup.fastq.json',
            'fastq_ecc': '{0}/illumina-cleanup/{1}.post-ecc.fastq.json',
            'fastq_original': '{0}/illumina-cleanup/{1}.original.fastq.json',
            'fastq_r1': '{0}/illumina-cleanup/{1}.cleanup.fastq.gz',
            'fastq_cleanup_md5': '{0}/illumina-cleanup/{1}.cleanup.md5',
            'fastq_original_md5': '{0}/illumina-cleanup/{1}.original.md5',

            'kmer': '{0}/kmer/{1}.jf',

            'mlst_blastn': '{0}/mlst/mlst-blastn.json',
            'mlst_mentalist': '{0}/mlst/mentalist/mlst.txt',
            'mlst_mentalist_ties': '{0}/mlst/mentalist/mlst.txt.ties.txt',
            'mlst_mentalist_votes': '{0}/mlst/mentalist/mlst.txt.votes.txt',

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

            'virulence_agr_primers': '{0}/agr/primers.json',

            'timeline': '{0}/staphopia-timeline.html',
            'version': '{0}/staphopia-version.txt'
        }
