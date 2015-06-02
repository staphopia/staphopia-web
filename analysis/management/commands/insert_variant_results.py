""" Insert variant analysis results into database. """
from os.path import basename, splitext
import time
import vcf

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from samples.models import Sample
from analysis.models import (
    PipelineVersion,
    Variant,
    VariantAnnotation,
    VariantComment,
    VariantFilter,
    VariantIndel,
    VariantReference,
    VariantSNP,
    VariantToIndel,
    VariantToSNP
)


class Command(BaseCommand):

    """ Insert results into database. """
    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help='Sample tag for which the data is for')
        parser.add_argument('input', metavar='INPUT_VCF',
                            help=('Gzipped annotated VCF formated file to '
                                  'be inserted'))
        parser.add_argument('--pipeline_version', default='0.1',
                            help=('Version of the pipeline used in this '
                                  'analysis. (Default: 0.1)'))

    def handle(self, *args, **opts):
        """ Insert results to database. """

        # Get sample and pipeline instances
        self.get_sample_instance(opts['sample_tag'])
        self.get_pipeline_instance(opts['pipeline_version'])

        # Open VCF for reading
        self.open_vcf(opts['input'])

        # Get reference info
        self.get_reference_instance()

        # Create Variant entry
        self.create_new_variant()

        # Get data already in the DB
        self.get_annotation_instances()
        self.get_locus_tags()
        self.get_comments()
        self.get_comment_instances()
        self.get_filters()
        self.get_filter_instances()

        # Store variants for bulk create
        self.snps = []
        self.indels = []

        # Read through VCF
        self.read_vcf()

        # Ready to insert variants
        self.insert_snps()
        self.insert_indels()

    def get_sample_instance(self, sample_tag):
        try:
            self.sample = Sample.objects.get(sample_tag=sample_tag)
        except Sample.DoesNotExist:
            raise CommandError('SAMPLE_TAG: {0} does not exist'.format(
                sample_tag
            ))

    def get_pipeline_instance(self, version):
        try:
            self.pipeline_version, c = PipelineVersion.objects.get_or_create(
                module='variant',
                version=version
            )
        except IntegrityError as e:
            raise CommandError('PipelineVersion Error: {0}'.format(e))

    def open_vcf(self, input):
        try:
            self.vcf_reader = vcf.Reader(open(input, 'r'), compressed=True)
        except IOError:
            raise CommandError('{0} does not exist'.format(input))

    @transaction.atomic
    def get_reference_instance(self):
        try:
            r = splitext(basename(self.vcf_reader.metadata['reference']))[0]
            self.reference, created = VariantReference.objects.get_or_create(
                name=r
            )
        except IntegrityError:
            raise CommandError('Error getting/saving reference information')

    @transaction.atomic
    def create_new_variant(self):
        try:
            self.variant = Variant.objects.create(
                sample=self.sample,
                version=self.pipeline_version
            )
        except IntegrityError:
            raise CommandError(
                'Variant entry already exists for {0} ({1})'.format(
                    self.sample, self.pipeline_version
                )
            )

    def get_locus_tags(self):
        """ Return the primary key of each locus tag. """
        self.locus_tags = {}
        for tag in VariantAnnotation.objects.filter(reference=self.reference):
            self.locus_tags[tag.locus_tag] = tag.pk

    def get_annotation_instances(self):
        """ Return the instance for each annotation. """
        pks = []
        for ks in VariantAnnotation.objects.filter(reference=self.reference):
            pks.append(ks.pk)
        self.annotations = VariantAnnotation.objects.in_bulk(pks)

    def get_comments(self):
        """ Return the primary key of each comment. """
        self.comments = {}
        for c in VariantComment.objects.all():
            self.comments[c.comment] = c.pk

    def get_comment_instances(self):
        """ Return the instance for each comment. """
        pks = []
        for ks in VariantComment.objects.all():
            pks.append(ks.pk)
        self.comment_instances = VariantComment.objects.in_bulk(pks)

    def get_filters(self):
        """ Return the primary key of each comment. """
        self.filters = {}
        for f in VariantFilter.objects.all():
            self.filters[f.name] = f.pk

    def get_filter_instances(self):
        """ Return the instance for each comment. """
        pks = []
        for ks in VariantFilter.objects.all():
            pks.append(ks.pk)
        self.filter_instances = VariantFilter.objects.in_bulk(pks)

    @transaction.atomic
    def get_annotation(self, record):
        annotation = None
        locus_tag = record.INFO['LocusTag'][0]
        if locus_tag in self.locus_tags:
            pk = self.locus_tags[locus_tag]
            annotation = self.annotations[pk]
        elif locus_tag is not None:
            annotation = VariantAnnotation.objects.create(
                reference=self.reference,
                locus_tag=locus_tag,
                protein_id=record.INFO['ProteinID'][0],
                gene=('.' if record.INFO['Gene'][0] is None
                      else record.INFO['Gene'][0]),
                db_xref=''.join(record.INFO['DBXref']),
                product=('.' if record.INFO['Product'][0] is None
                         else record.INFO['Product'][0]),
                note=('.' if record.INFO['Note'][0] is None
                      else record.INFO['Note'][0])
            )
            self.locus_tags[locus_tag] = annotation.pk
            self.annotations[annotation.pk] = annotation
        elif locus_tag is None:
            if 'inter_genic' not in self.locus_tags:
                annotation = VariantAnnotation.objects.create(
                    reference=self.reference,
                    locus_tag='inter_genic',
                    protein_id='inter_genic',
                    gene='inter_genic',
                    db_xref='inter_genic',
                    product='inter_genic',
                    note='inter_genic'
                )
                self.locus_tags['inter_genic'] = annotation.pk
                self.annotations[annotation.pk] = annotation
            else:
                pk = self.locus_tags['inter_genic']
                annotation = self.annotations[pk]

        return annotation

    @transaction.atomic
    def get_filter(self, filter):
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
            record_filters = VariantFilter.objects.create(name=f)
            self.filters[f] = record_filters.pk
            self.filter_instances[record_filters.pk] = record_filters

        return record_filters

    @transaction.atomic
    def get_comment(self, c):
        comment = None
        if c is None:
            c = 'None'

        if c in self.comments:
            pk = self.comments[c]
            comment = self.comment_instances[pk]
        else:
            comment = VariantComment.objects.create(comment=c)
            self.comments[c] = comment.pk
            self.comment_instances[comment.pk] = comment

        return comment

    @transaction.atomic
    def create_snp(self, record, reference, annotation):
        return VariantSNP.objects.create(
            reference=reference,
            annotation=annotation,
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

    def get_snp(self, record, reference, annotation):
        snp = False
        while not snp:
            try:
                snp = VariantSNP.objects.get(
                    reference=reference,
                    reference_position=record.POS,
                    reference_base=record.REF,
                    alternate_base=record.ALT[0]
                )
            except VariantSNP.DoesNotExist:
                try:
                    snp = self.create_snp(record, reference, annotation)
                except IntegrityError:
                    print "trying SNP ({0},{1}->{2}) again".format(
                        record.POS, record.REF, record.ALT[0]
                    )
                    time.sleep(1)
                    continue

        return snp

    @transaction.atomic
    def create_indel(self, record, reference, annotation):
        return VariantIndel.objects.create(
            reference=reference,
            annotation=annotation,
            reference_position=record.POS,
            reference_base=record.REF,
            alternate_base=(record.ALT if len(record.ALT) > 1 else
                            record.ALT[0]),
            is_deletion=record.is_deletion
        )

    def get_indel(self, record, reference, annotation):
        # Get or create InDel
        indel = False
        while not indel:
            try:
                indel = VariantIndel.objects.get(
                    reference=reference,
                    reference_position=record.POS,
                    reference_base=record.REF,
                    alternate_base=(record.ALT if len(record.ALT) > 1 else
                                    record.ALT[0]),
                )
            except VariantIndel.DoesNotExist:
                try:
                    indel = self.create_indel(record, reference, annotation)
                except IntegrityError:
                    print "trying Indel ({0},{1}->{2}) again".format(
                        record.POS, record.REF, record.ALT
                    )
                    time.sleep(1)
                    continue

        return indel

    def read_vcf(self):
        # Insert VCF Records
        for record in self.vcf_reader:
            # Get annotation, filter, comment
            annotation = self.get_annotation(record)
            record_filters = self.get_filter(record.FILTER)

            # Insert SNP/Indel
            if record.is_snp:
                comment = self.get_comment(record.INFO['Comments'][0])
                snp = self.get_snp(record, self.reference, annotation)

                # Store SNP
                try:
                    self.snps.append(
                        VariantToSNP(
                            variant=self.variant,
                            snp=snp,
                            comment=comment,
                            filters=record_filters,
                            AC=str(record.INFO['AC']),
                            AD=str(record.samples[0]['AD']),
                            AF=record.INFO['AF'][0],
                            DP=record.INFO['DP'],
                            GQ=record.samples[0]['GQ'],
                            GT=record.samples[0]['GT'],
                            MQ=record.INFO['MQ'],
                            PL=str(record.samples[0]['PL']),
                            QD=record.INFO['QD'],
                            quality=record.QUAL
                        )
                    )
                except IntegrityError as e:
                    raise CommandError('VariantSNP Error: {0}'.format(e))
            else:
                indel = self.get_indel(record, self.reference, annotation)

                # Insert InDel
                try:
                    self.indels.append(
                        VariantToIndel(
                            variant=self.variant,
                            indel=indel,
                            filters=record_filters,
                            AC=str(record.INFO['AC']),
                            AD=str(record.samples[0]['AD']),
                            AF=record.INFO['AF'][0],
                            DP=record.INFO['DP'],
                            GQ=record.samples[0]['GQ'],
                            GT=record.samples[0]['GT'],
                            MQ=record.INFO['MQ'],
                            PL=str(record.samples[0]['PL']),
                            QD=record.INFO['QD'],
                            quality=record.QUAL
                        )
                    )
                except IntegrityError as e:
                    raise CommandError('VariantIndel Error: {0}'.format(e))

    @transaction.atomic
    def insert_snps(self):
        VariantToSNP.objects.bulk_create(self.snps, batch_size=2000)
        return None

    @transaction.atomic
    def insert_indels(self):
        VariantToIndel.objects.bulk_create(self.indels, batch_size=2000)
        return None
