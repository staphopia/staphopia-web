""" Insert variant analysis results into database. """
from os.path import basename, splitext
import vcf

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from variant.models import Annotation, Comment, Reference, SNP


class Command(BaseCommand):

    """ Insert results into database. """
    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        parser.add_argument('input', metavar='INPUT_VCF',
                            help=('Gzipped annotated VCF formated file to '
                                  'be inserted'))

    def handle(self, *args, **opts):
        """ Insert results to database. """

        # Open VCF for reading
        self.open_vcf(opts['input'])

        # Get reference info
        self.get_reference_instance()

        # Get data already in the DB
        self.get_annotation_instances()
        self.get_locus_tags()
        self.get_comments()
        self.get_comment_instances()

        # Store variants for bulk create
        self.snps = []

        # Read through VCF
        self.read_vcf()

        # Ready to insert variants
        self.insert_snps()

    def open_vcf(self, input):
        try:
            self.vcf_reader = vcf.Reader(open(input, 'r'), compressed=True)
        except IOError:
            raise CommandError('{0} does not exist'.format(input))

    @transaction.atomic
    def get_reference_instance(self):
        try:
            r = splitext(basename(self.vcf_reader.metadata['reference']))[0]
            self.reference, created = Reference.objects.get_or_create(
                name=r
            )
        except IntegrityError:
            raise CommandError('Error getting/saving reference information')

    def get_locus_tags(self):
        """ Return the primary key of each locus tag. """
        self.locus_tags = {}
        for tag in Annotation.objects.filter(reference=self.reference):
            self.locus_tags[tag.locus_tag] = tag.pk

    def get_annotation_instances(self):
        """ Return the instance for each annotation. """
        pks = []
        for ks in Annotation.objects.filter(reference=self.reference):
            pks.append(ks.pk)
        self.annotations = Annotation.objects.in_bulk(pks)

    def get_comments(self):
        """ Return the primary key of each comment. """
        self.comments = {}
        for c in Comment.objects.all():
            self.comments[c.comment] = c.pk

    def get_comment_instances(self):
        """ Return the instance for each comment. """
        pks = []
        for ks in Comment.objects.all():
            pks.append(ks.pk)
        self.comment_instances = Comment.objects.in_bulk(pks)

    @transaction.atomic
    def get_annotation(self, record):
        annotation = None
        locus_tag = record.INFO['LocusTag'][0]
        if locus_tag in self.locus_tags:
            pk = self.locus_tags[locus_tag]
            annotation = self.annotations[pk]
        elif locus_tag is not None:
            annotation = Annotation.objects.create(
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
                annotation = Annotation.objects.create(
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
    def get_comment(self, c):
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
    def create_snp(self, record, reference, annotation):
        self.snps.append(SNP(
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
        ))

    def read_vcf(self):
        # Insert VCF Records
        for record in self.vcf_reader:
            # Get annotation, filter, comment
            annotation = self.get_annotation(record)

            # Insert SNP/Indel
            if record.is_snp:
                self.get_comment(record.INFO['Comments'][0])
                self.create_snp(record, self.reference, annotation)

    @transaction.atomic
    def insert_snps(self):
        SNP.objects.bulk_create(self.snps, batch_size=2000)
        return None
