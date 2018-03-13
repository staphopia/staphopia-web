"""Insert CGMLST results into database."""
from django.core.management.base import BaseCommand

from api.utils import query_database


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the CGMLST results into the database.'

    def handle(self, *args, **opts):
        cgmlst = {}
        total = 0
        for row in query_database("SELECT mentalist FROM cgmlst_cgmlst;"):
            string = []
            for k in sorted(row['mentalist'], key=lambda x: int(x)):
                # k = Loci, v = Allele
                string.append(str(row['mentalist'][k]))
            cgmlst_string = ':'.join(string)
            if cgmlst_string not in cgmlst:
                cgmlst[cgmlst_string] = 1
            else:
                cgmlst[cgmlst_string] += 1
            total += 1

        print(f'Total: {total}, Total CGMLST: {len(cgmlst)}')
