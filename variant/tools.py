"""
Useful functions associated with variant.

To use:
from variant.tools import UTIL1, UTIL2, etc...
"""
from collections import OrderedDict
import sys
import time
import vcf

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import timeit
from variant.models import (
    Annotation,
    Comment,
    Feature,
    Filter,
    Indel,
    Reference,
    SNP,
    Variant
)


@timeit
def insert_variants(sample, version, files, force=False):
    """Insert VCF formatted variants."""
    if force:
        print(f'{sample.name}: Force used, emptying variant related results.')
        Variant.objects.filter(sample=sample, version=version).delete()

    v = Variants(sample, version, files['variants'])
    v.insert_variants()


class Variants(object):
    """Insert VCF into the database."""
    def __init__(self, sample, version, variants):
        """Initialize variables."""
        self.sample = sample
        self.name = sample.name
        self.version = version

        # Read VCF and get required data from database
        self.open_vcf(variants)
        self.get_reference_instance()
        self.get_annotation_instances()
        self.get_feature_instances()
        self.get_locus_tags()
        self.get_comments()
        self.get_comment_instances()
        self.get_filters()
        self.get_filter_instances()
        self.get_snps()

        # Lists for bulk creation
        self.snps = []
        self.indels = []

        # Read through VCF
        self.read_vcf()

    @transaction.atomic
    @timeit
    def insert_variants(self):
        """Insert variant counts."""
        try:
            Variant.objects.create(
                sample=self.sample,
                version=self.version,
                reference=self.reference,
                snp_count=len(self.snps),
                indel_count=len(self.indels),
                snp=self.snps,
                indel=self.indels
            )
        except IntegrityError:
            raise CommandError(f'{self.name} Error saving variants {e}')

    @timeit
    def open_vcf(self, vcf_file):
        """Read input VCF file."""
        try:
            self.vcf_reader = vcf.Reader(filename=vcf_file, compressed=True,
                                         encoding='utf-8')
            self.records = [record for record in self.vcf_reader]
        except IOError:
            raise CommandError('{0} does not exist'.format(input))

    @transaction.atomic
    def get_reference_instance(self):
        """Get reference instance."""
        try:
            r = list(self.vcf_reader.contigs.keys())[0]
            self.reference, created = Reference.objects.get_or_create(
                name=r
            )
        except IntegrityError:
            raise CommandError('Error getting/saving reference information')

    @timeit
    def get_locus_tags(self):
        """Return the primary key of each locus tag."""
        self.locus_tags = {}
        for tag in Annotation.objects.filter(reference=self.reference):
            self.locus_tags[tag.locus_tag] = tag.pk

    def get_feature_instances(self):
        """Return the primary key of each feature type."""
        self.features = {}
        for tag in Feature.objects.filter(reference=self.reference):
            self.features[tag.feature] = tag

    def get_feature(self, feature):
        """Get the feature type of a variant."""
        if feature in self.features:
            return self.features[feature]
        else:
            try:
                feature_obj = Feature.objects.create(
                    reference=self.reference,
                    feature=feature
                )
                self.features[feature] = feature_obj
            except IntegrityError:
                raise CommandError('Error getting/saving feature information')

    @timeit
    def get_annotation_instances(self):
        """Return the instance for each annotation."""
        pks = []
        for ks in Annotation.objects.filter(reference=self.reference):
            pks.append(ks.pk)
        self.annotations = Annotation.objects.in_bulk(pks)

    def get_comments(self):
        """Return the primary key of each comment."""
        self.comments = {}
        for c in Comment.objects.all():
            self.comments[c.comment] = c.pk

    @timeit
    def get_comment_instances(self):
        """Return the instance for each comment."""
        pks = []
        for ks in Comment.objects.all():
            pks.append(ks.pk)
        self.comment_instances = Comment.objects.in_bulk(pks)

    @timeit
    def get_filters(self):
        """Return the primary key of each comment."""
        self.filters = {}
        for f in Filter.objects.all():
            self.filters[f.name] = f.pk

    @timeit
    def get_filter_instances(self):
        """Return the instance for each comment."""
        pks = []
        for ks in Filter.objects.all():
            pks.append(ks.pk)
        self.filter_instances = Filter.objects.in_bulk(pks)

    @transaction.atomic
    def get_annotation(self, record):
        """Check if annotation is already in db, if not insert it."""
        annotation = None
        locus_tag = record.INFO['LocusTag'][0]
        if locus_tag in self.locus_tags:
            pk = self.locus_tags[locus_tag]
            annotation = self.annotations[pk]
        elif locus_tag is not None:
            protein_id = record.INFO['ProteinID'][0]
            if not protein_id:
                protein_id = "not_applicable"

            annotation = Annotation.objects.create(
                reference=self.reference,
                locus_tag=locus_tag,
                protein_id=protein_id,
                gene=('.' if record.INFO['Gene'][0] is None
                      else record.INFO['Gene'][0]),
                product=('.' if record.INFO['Product'][0] is None
                         else record.INFO['Product'][0]),
                note=('.' if record.INFO['Note'][0] is None
                      else record.INFO['Note'][0]),
                is_pseudo=record.INFO['IsPseudo']
            )
            self.locus_tags[locus_tag] = annotation.pk
            self.annotations[annotation.pk] = annotation
        elif locus_tag is None:
            if 'inter_genic' not in self.locus_tags:
                annotation = Annotation.objects.create(
                    reference=self.reference,
                    locus_tag='inter_genic',
                    protein_id='inter_genic',
                    gene='inter_genic',
                    product='inter_genic',
                    note='inter_genic',
                    is_pseudo=record.INFO['IsPseudo']
                )
                self.locus_tags['inter_genic'] = annotation.pk
                self.annotations[annotation.pk] = annotation
            else:
                pk = self.locus_tags['inter_genic']
                annotation = self.annotations[pk]

        return annotation

    @transaction.atomic
    def get_filter(self, filter):
        """Get the GATK filter applid to the entry."""
        record_filters = None
        f = None
        if len(filter) == 0:
            f = 'PASS'
        else:
            f = ', '.join(filter)

        if f in self.filters:
            pk = self.filters[f]
            record_filters = self.filter_instances[pk]
        else:
            record_filters = Filter.objects.create(name=f)
            self.filters[f] = record_filters.pk
            self.filter_instances[record_filters.pk] = record_filters

        return record_filters

    @transaction.atomic
    def get_comment(self, c):
        """Get any comments associated with the entry."""
        comment = None
        if c is None:
            c = 'None'

        if c in self.comments:
            pk = self.comments[c]
            comment = self.comment_instances[pk]
        else:
            comment = Comment.objects.create(comment=c)
            self.comments[c] = comment.pk
            self.comment_instances[comment.pk] = comment

        return comment

    @transaction.atomic
    @timeit
    def create_snp(self, record, reference, annotation, feature):
        """Create a new snp."""
        print(record.POS, feature.feature)
        return SNP.objects.create(
            reference=reference,
            annotation=annotation,
            feature=feature,
            reference_position=record.POS,
            reference_base=record.REF,
            alternate_base=record.ALT[0],

            reference_codon=('.' if record.INFO['RefCodon'][0] is None
                             else record.INFO['RefCodon'][0]),
            alternate_codon=('.' if record.INFO['AltCodon'][0] is None
                             else record.INFO['AltCodon'][0]),
            reference_amino_acid=('.' if record.INFO['RefAminoAcid'][0] is None
                                  else record.INFO['RefAminoAcid'][0]),
            alternate_amino_acid=('.' if record.INFO['AltAminoAcid'][0] is None
                                  else record.INFO['AltAminoAcid'][0]),
            codon_position=(0 if record.INFO['CodonPosition'] is None
                            else record.INFO['CodonPosition']),
            snp_codon_position=(0 if record.INFO['SNPCodonPosition'] is None
                                else record.INFO['SNPCodonPosition']),
            amino_acid_change=('.' if record.INFO['AminoAcidChange'][0] is None
                               else record.INFO['AminoAcidChange'][0]),
            is_synonymous=record.INFO['IsSynonymous'],
            is_transition=record.INFO['IsTransition'],
            is_genic=record.INFO['IsGenic'],
        )

    @timeit
    def get_snps(self):
        """Get all the snps in the database, for positions to be inserted."""
        self.all_snps = {}
        for snp in SNP.objects.filter(
            reference=self.reference,
            reference_position__in=[record.POS for record in self.records]
        ):
            key = (
                snp.reference_position,
                snp.reference_base,
                snp.alternate_base
            )
            self.all_snps[key] = snp.pk

    def get_snp(self, record, reference, annotation, feature):
        """Get an individual snp."""
        snp = False
        while not snp:
            try:
                snp = self.all_snps[(
                    record.POS,
                    record.REF,
                    str(record.ALT[0])
                )]
            except KeyError:
                try:
                    snp = self.create_snp(record, reference, annotation,
                                          feature).pk
                except IntegrityError:
                    print("trying SNP ({0},{1}->{2}) again".format(
                        record.POS, record.REF, record.ALT[0]
                    ), file=sys.stderr)
                    time.sleep(1)
                    continue

        return snp

    @transaction.atomic
    def create_indel(self, record, reference, annotation, feature):
        """Create a new indel."""
        return Indel.objects.create(
            reference=reference,
            annotation=annotation,
            feature=feature,
            reference_position=record.POS,
            reference_base=record.REF,
            alternate_base=(record.ALT if len(record.ALT) > 1 else
                            record.ALT[0]),
            is_deletion=record.is_deletion
        )

    def get_indel(self, record, reference, annotation, feature):
        """Get or create InDel."""
        indel = False
        while not indel:
            try:
                indel = Indel.objects.get(
                    reference=reference,
                    reference_position=record.POS,
                    reference_base=record.REF,
                    alternate_base=(record.ALT if len(record.ALT) > 1 else
                                    record.ALT[0]),
                ).pk
            except Indel.DoesNotExist:
                try:
                    indel = self.create_indel(record, reference, annotation,
                                              feature).pk
                except IntegrityError:
                    print("trying Indel ({0},{1}->{2}) again".format(
                        record.POS, record.REF, record.ALT
                    ), file=sys.stderr)
                    time.sleep(1)
                    continue

        return indel

    @timeit
    def read_vcf(self):
        """Read through the VCF records."""
        # Insert VCF Records
        for record in self.records:
            # Get annotation, filter, comment
            annotation = self.get_annotation(record)
            feature = self.get_feature(record.INFO['FeatureType'][0])
            record_filters = self.get_filter(record.FILTER)
            variant = OrderedDict()
            if record.is_snp:
                comment = self.get_comment(record.INFO['Comments'][0])
                variant['snp_id'] = self.get_snp(record, self.reference,
                                                 annotation, feature)
                variant['comment'] = comment.pk
            else:
                variant['indel_id'] = self.get_indel(record, self.reference,
                                                     annotation, feature)

            # Store variant confidence
            sample_data = record.samples[0].data
            QD = record.INFO['QD'] if 'QD' in record.INFO else 0.0
            try:
                AD = sample_data.AD
            except AttributeError:
                AD = ""

            try:
                GQ = sample_data.GQ
            except AttributeError:
                GQ = 0

            try:
                GT = sample_data.GT
            except AttributeError:
                GT = ""

            try:
                PL = sample_data.PL
            except AttributeError:
                PL = ""

            variant['filter_id'] = record_filters.pk
            variant['AC'] = str(record.INFO['AC']),
            variant['AD'] = str(AD),
            variant['AF'] = str(record.INFO['AF'][0]),
            variant['DP'] = str(record.INFO['DP']),
            variant['GQ'] = str(GQ),
            variant['GT'] = str(GT),
            variant['MQ'] = str(record.INFO['MQ']),
            variant['PL'] = str(PL),
            variant['QD'] = str(QD),
            variant['quality'] = record.QUAL

            if record.is_snp:
                self.snps.append(variant)
            else:
                self.indels.append(variant)


@timeit
def generate_reference_snps(path, name, sequence):
    """
    Generate all possible SNPs in a given reference genome.

    ##fileformat=VCFv4.1
    ##INFO=<ID=AC,Number=A,Type=Integer,Description="Allele count in genotypes,
    for each ALT allele, in the same order as listed">
    ##reference=file:///staphopia/ebs/analysis-pipeline/tool-data/snp/n315.fasta
    ##contig=<ID=gi|29165615|ref|NC_002745.2|,length=2814816>
    #CHROM  POS ID  REF ALT QUAL    FILTER  INFO    FORMAT  GATK
    CHROM   gi|29165615|ref|NC_002745.2|
    POS     7
    ID      .
    REF     A
    ALT     G
    QUAL    27.77
    FILTER  LowQual
    INFO    AC=1;AF=0.5;AN=2;...;VariantType=SNP
    FORMAT  GT:AD:DP:GQ:PL
    GATK    0/1:5,2:7:56:56,0,176
    """
    # Open Reference FASTA
    vcf = []
    vcf.append('##fileformat=VCFv4.1')
    vcf.append(f'##reference=file:///{path}')
    vcf.append(''.join([
          '##INFO=<ID=AC,Number=A,Type=Integer,Description="Allele count in '
          'genotypes, for each ALT allele, in the same order as listed">'
    ]))
    vcf.append(''.join([
        '##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allelic depths '
        'for the ref and alt alleles in the order listed">'
    ]))
    vcf.append('##FILTER=<ID=LowQual,Description="Low quality">')
    vcf.append(f'##contig=<ID={name},length={len(sequence)}>')
    vcf.append("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tGATK")

    bases = ['A', 'C', 'G', 'T']
    for pos, ref_base in enumerate(sequence):
        for base in bases:
            if base == ref_base:
                continue
            else:
                vcf.append('\t'.join([
                    name, str(pos + 1), '.', ref_base, base, '0.00',
                    'LowQual', 'AC=1', 'AD', '1'
                ]))
    return vcf
