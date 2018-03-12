"""Update members of SNP and InDel IDs."""
from collections import OrderedDict
import sys

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from api.utils import query_database
from staphopia.utils import timeit
from sample.models import Sample
from variant.models import (
    Variant, SNP, Indel, Reference, IndelMember, SNPMember
)


@timeit
def get_variant_members(reference_id, is_indel=False):
    sql = """SELECT id
             FROM variant_{0}
             WHERE reference_id={1}
             ORDER BY id ASC;""".format(
        'indel' if is_indel else 'snp',
        reference_id
    )
    members = OrderedDict()
    for row in query_database(sql):
        members[row['id']] = []
    return members


class Command(BaseCommand):
    """Update members of SNP and InDel IDs."""

    help = 'Update members of SNP and InDel IDs.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('--reference', metavar='REFERENCE',
                            default='gi|29165615|ref|NC_002745.2|',
                            help=('Reference genome.'))

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert results to database."""
        try:
            reference = Reference.objects.get(name=opts['reference'])
        except IntegrityError as e:
            raise CommandError(f'Reference Error: {e}')

        # Full update, so empty tables
        self.delete_members(reference)

        # Create of SNP and Indel IDs
        snps = get_variant_members(reference.pk)
        indels = get_variant_members(reference.pk, is_indel=True)

        sql = """SELECT sample_id
                 FROM variant_variant AS v
                 LEFT JOIN sample_sample AS s
                 ON v.sample_id=s.id
                 WHERE s.is_public=TRUE AND v.reference_id={0}""".format(
            reference.pk
        )
        print('Start variant reading/processing')
        i = 1
        rows = query_database(sql)
        total = len(rows)
        for row in rows:
            try:
                variant = Variant.objects.get(sample=row['sample_id'],
                                              reference=reference)
            except Variant.DoesNotExist:
                pass
            if i % 100 == 0:
                print(f'{i} of {total} samples processed')
            for snp in variant.snp:
                snps[snp['snp_id']].append(row['sample_id'])

            for indel in variant.indel:
                indels[indel['indel_id']].append(row['sample_id'])
            i += 1

        # Update member columns
        self.insert_indels(indels, reference)
        self.insert_snps(snps, reference)

    @timeit
    @transaction.atomic
    def delete_members(self, reference):
        """Force update, so remove from table."""
        print('Emptying member related results.')
        SNPMember.objects.filter(reference=reference).delete()
        IndelMember.objects.filter(reference=reference).delete()


    @timeit
    @transaction.atomic
    def insert_snps(self, snps, reference):
        """Bulk insert snp members."""
        snp_members = []
        print(f'Inserting members for {len(snps)} SNPs...')
        for snp_id, members in snps.items():
            members.sort()
            snp_members.append(SNPMember(
                reference=reference,
                snp_id=snp_id,
                count=len(members),
                members=members
            ))
        SNPMember.objects.bulk_create(snp_members, batch_size=10000)


    @timeit
    @transaction.atomic
    def insert_indels(self, indels, reference):
        """Bulk insert indel members."""
        indel_members = []
        print(f'Inserting members for {len(indels)} Indels...')
        for indel_id, members in indels.items():
            members.sort()
            indel_members.append(IndelMember(
                reference=reference,
                indel_id=indel_id,
                count=len(members),
                members=members
            ))
        IndelMember.objects.bulk_create(indel_members, batch_size=10000)
