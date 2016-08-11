"""Add information pertaining to the resitance phenotype for given samples."""

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from sample.models import (
    Sample, ToResistance, Resistance, ResistanceSpecification
)


class Command(BaseCommand):
    """Add resitance phenotype for given samples."""

    help = 'Add resitance phenotype for given samples.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('resistance', metavar='RESISTANCE.txt',
                            help=('Text file with resistance information.'))
        parser.add_argument('antibiotic', type=str,
                            help='(Antibiotic tested.')
        parser.add_argument('test', type=str,
                            help='(How resistance to Antibiotic was tested.')
        parser.add_argument('unit', type=str,
                            help=('Unit of measure to determine resistance.'))
        parser.add_argument('susceptible', type=str, default="",
                            help=('Result of test considered susceptible.'))
        parser.add_argument('intermediate', type=str, default="",
                            help=('Result of test considered intermediate.'))
        parser.add_argument('resistant', type=str, default="",
                            help=('Result of test considered resistant.'))
        parser.add_argument('comment', type=str, default="",
                            help=('Comment on how test was conducted.'))

    def handle(self, *args, **opts):
        """Add resitance phenotype for given samples."""
        # Get or Create Resistance Test
        specification = self.get_resistance_specification(
            opts['susceptible'], opts['intermediate'],
            opts['resistant'], opts['comment']
        )

        # Get or Create Resistance Specification
        resistance = self.get_resistance(opts['antibiotic'], opts['test'],
                                         opts['unit'])

        # Read through all data before insert
        samples = []
        with open(opts['resistance'], 'r') as fh:
            for line in fh:
                sample_id, value, phenotype = line.rstrip().split('\t')
                sample = self.get_sample(sample_id)
                samples.append({
                    'sample': sample, 'value': value, 'phenotype': phenotype
                })

        for sample in samples:
            self.insert_resistance(sample, resistance, specification)

    @transaction.atomic
    def get_resistance_specification(self, susceptible, intermediate,
                                     resistant, comment):
        """Get or Create a ResistanceSpecification."""
        rs_obj, created = ResistanceSpecification.objects.get_or_create(
            susceptible=susceptible,
            intermediate=intermediate,
            resistant=resistant,
            comment=comment
        )

        if created:
            print("Created new Resistance Specification")

        return(rs_obj)

    @transaction.atomic
    def get_resistance(self, antibiotic, test, unit):
        """Get or Create a Resistance."""
        r_obj, created = Resistance.objects.get_or_create(
            antibiotic=antibiotic,
            test=test,
            unit=unit
        )

        if created:
            print("Created new Resistance")

        return(r_obj)

    def get_sample(self, pk):
        """Return Sample object by primary key."""
        try:
            return Sample.objects.get(pk=pk)
        except Sample.DoesNotExist:
            raise CommandError('A sample id, {0}, does not exist'.format(pk))

    @transaction.atomic
    def insert_resistance(self, sample, resistance, specification):
        """Insert phenotype to the database."""
        tr_obj, created = ToResistance.objects.get_or_create(
            sample=sample['sample'],
            resistance=resistance,
            value=sample['value'],
            phenotype=sample['phenotype'],
            specification=specification
        )

        print("{0}\t{1}\t{2}\t{3}".format(
            sample['sample'].sample_tag,
            resistance.antibiotic,
            sample['phenotype'],
            created
        ))
