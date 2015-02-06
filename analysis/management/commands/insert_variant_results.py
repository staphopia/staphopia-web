""" Insert variant analysis results into database. """
import vcf
from optparse import make_option

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
    VariantInfo,
    VariantReference,
    VariantSNP,
    VariantToIndel,
    VariantToSNP
)


class Command(BaseCommand):

    """ Insert results into database. """

    help = 'Insert the analysis results into the database.'

    option_list = BaseCommand.option_list + (
        make_option('--sample_tag', dest='sample_tag',
                    help='Sample tag for which the data is for'),
        make_option('--input', dest='input',
                    help='Gzipped annotated VCF formated file to be inserted'),
        make_option('--pipeline_version', dest='pipeline_version',
                    help=('Version of the pipeline used in this analysis. '
                          '(Default: 0.1)')),
    )

    @transaction.atomic
    def handle(self, *args, **opts):
        """ Insert results to database. """
        # Required Parameters
        if not opts['sample_tag']:
            raise CommandError('--sample_tag is requried')
        elif not opts['input']:
            raise CommandError('--input is requried')
        elif not opts['pipeline_version']:
            opts['pipeline_version'] = "0.1"

        # Read VCF
        try:
            vcf_reader = vcf.Reader(open(opts['input'], 'r'), compressed=True)
        except IOError:
            raise CommandError('{0} does not exist'.format(opts['input']))

        # Sample
        try:
            sample = Sample.objects.get(sample_tag=opts['sample_tag'])
        except Sample.DoesNotExist:
            raise CommandError('sample_tag: {0} does not exist'.format(
                opts['sample_tag']
            ))

        # Pipeline Version
        try:
            pipeline_version, created = PipelineVersion.objects.get_or_create(
                module='variant',
                version=opts['pipeline_version']
            )
        except IntegrityError as e:
            raise CommandError('PipelineVersion Error: {0}'.format(e))

        # Variant
        variant, created = Variant.objects.get_or_create(
            sample=sample,
            version=pipeline_version
        )

        # Reference
        try:
            reference, created = VariantReference.objects.get_or_create(
                name=vcf_reader.metadata['reference']
            )
        except VariantReference.IntegrityError:
            raise CommandError('Error getting/saving reference information')

        # Get data already in the DB
        annotations = self.get_annotation_instances(reference)
        locus_tags = self.get_locus_tags(reference)
        comments = self.get_comments()
        comment_instances = self.get_comment_instances()
        filters = self.get_filters()
        filter_instances = self.get_filter_instances()

        # Insert VCF Records
        for record in vcf_reader:
            # Get or insert annotation
            annotation = None
            locus_tag = record.INFO['LocusTag'][0]
            if locus_tag in locus_tags:
                annotation = annotations[locus_tags[locus_tag]]
            elif locus_tag is not None:
                annotation = VariantAnnotation.objects.create(
                    reference=reference,
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
                locus_tags[locus_tag] = annotation.pk
                annotations[annotation.pk] = annotation
            elif locus_tag is None:
                if 'inter_genic' not in locus_tags:
                    annotation = VariantAnnotation.objects.create(
                        reference=reference,
                        locus_tag='inter_genic',
                        protein_id='inter_genic',
                        gene='inter_genic',
                        db_xref='inter_genic',
                        product='inter_genic',
                        note='inter_genic'
                    )
                    locus_tags['inter_genic'] = annotation.pk
                    annotations[annotation.pk] = annotation
                else:
                    annotation = annotations[locus_tags['inter_genic']]

            # Insert Info
            info, created = VariantInfo.objects.get_or_create(
                AC=str(record.INFO['AC']),
                AD=str(record.samples[0]['AD']),
                AF=record.INFO['AF'][0],
                AN=record.INFO['AN'],
                DP=record.INFO['DP'],
                GQ=record.samples[0]['GQ'],
                GT=record.samples[0]['GT'],
                MQ=record.INFO['MQ'],
                PL=str(record.samples[0]['PL']),
                QD=record.INFO['QD']
            )

            # Insert Filter
            record_filters = None
            f = None
            if len(record.FILTER) == 0:
                f = 'PASS'
            else:
                f = ', '.join(record.FILTER)

            if f in filters:
                record_filters = filter_instances[filters[f]]
            else:
                record_filters = VariantFilter.objects.create(
                    name=f
                )
                filters[f] = record_filters.pk
                filter_instances[record_filters.pk] = record_filters

            # Insert SNP/Indel
            if record.is_snp:
                # Get or insert Comment
                comment = None
                c = record.INFO['Comments'][0]
                if c is None:
                    c = 'None'

                if c in comments:
                    comment = comment_instances[comments[c]]
                else:
                    comment = VariantComment.objects.create(
                        comment=c
                    )
                    comments[c] = comment.pk
                    comment_instances[comment.pk] = comment

                # Get or create SNP
                snp, created = VariantSNP.objects.get_or_create(
                    reference=reference,
                    annotation=annotation,
                    reference_position=record.POS,
                    reference_base=record.REF,
                    alternate_base=record.ALT[0],

                    reference_codon=('.' if record.INFO['RefCodon'][0] is None
                                     else record.INFO['RefCodon'][0]),
                    alternate_codon=('.' if record.INFO['AltCodon'][0] is None
                                     else record.INFO['AltCodon'][0]),

                    reference_amino_acid=('.' if record.INFO['RefAminoAcid'][0]
                                          is None
                                          else record.INFO['RefAminoAcid'][0]),
                    alternate_amino_acid=('.' if record.INFO['AltAminoAcid'][0]
                                          is None
                                          else record.INFO['AltAminoAcid'][0]),

                    codon_position=(0 if record.INFO['CodonPosition'] is None
                                    else record.INFO['CodonPosition']),
                    snp_codon_position=(0 if record.INFO['SNPCodonPosition']
                                        is None
                                        else record.INFO['SNPCodonPosition']),
                    amino_acid_change=('.' if record.INFO['AminoAcidChange'][0]
                                       is None
                                       else record.INFO['AminoAcidChange'][0]),

                    is_synonymous=record.INFO['IsSynonymous'],
                    is_transition=record.INFO['IsTransition'],
                    is_genic=record.INFO['IsGenic'],
                )

                # Insert SNP
                try:
                    VariantToSNP.objects.create(
                        variant=variant,
                        snp=snp,
                        comment=comment,
                        info=info,
                        filters=record_filters,
                        quality=record.QUAL
                    )
                except IntegrityError as e:
                    raise CommandError('VariantSNP Error: {0}'.format(e))
            else:
                # Get or create InDel
                indel, created = VariantIndel.objects.get_or_create(
                    reference=reference,
                    annotation=annotation,
                    reference_position=record.POS,
                    reference_base=record.REF,
                    alternate_base=(record.ALT if len(record.ALT) > 1 else
                                    record.ALT[0]),
                    is_deletion=record.is_deletion
                )

                # Insert InDel
                try:
                    VariantToIndel.objects.create(
                        variant=variant,
                        indel=indel,
                        info=info,
                        filters=record_filters,
                        quality=record.QUAL
                    )
                except IntegrityError as e:
                    raise CommandError('VariantIndel Error: {0}'.format(e))

    def get_locus_tags(self, reference):
        """ Return the primary key of each locus tag. """
        locus_tags = {}
        for tag in VariantAnnotation.objects.filter(reference=reference):
            locus_tags[tag.locus_tag] = tag.pk
        return locus_tags

    def get_annotation_instances(self, reference):
        """ Return the instance for each annotation. """
        pks = []
        for ks in VariantAnnotation.objects.filter(reference=reference):
            pks.append(ks.pk)
        return VariantAnnotation.objects.in_bulk(pks)

    def get_comments(self):
        """ Return the primary key of each comment. """
        comments = {}
        for c in VariantComment.objects.all():
            comments[c.comment] = c.pk
        return comments

    def get_comment_instances(self):
        """ Return the instance for each comment. """
        pks = []
        for ks in VariantComment.objects.all():
            pks.append(ks.pk)
        return VariantComment.objects.in_bulk(pks)

    def get_filters(self):
        """ Return the primary key of each comment. """
        filters = {}
        for f in VariantFilter.objects.all():
            filters[f.name] = f.pk
        return filters

    def get_filter_instances(self):
        """ Return the instance for each comment. """
        pks = []
        for ks in VariantFilter.objects.all():
            pks.append(ks.pk)
        return VariantFilter.objects.in_bulk(pks)
