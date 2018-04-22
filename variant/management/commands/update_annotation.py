"""Add phase info to variant annotations."""
from django.core.management.base import BaseCommand

from Bio import SeqIO

from variant.models import Annotation, Reference


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('input', metavar='INPUT_GENBANK',
                            help=('Annotated GenBank file for the reference '
                                  'to be updated'))

    def handle(self, *args, **opts):
        """Insert results to database."""
        # Open GenBank for reading
        phases = {}
        features = ["CDS", "rRNA", "tRNA", "ncRNA", "repeat_region",
                    "misc_feature"]
        gb = SeqIO.read(open(opts['input'], 'r'), 'genbank')
        for feature in gb.features:
            if feature.type in features:
                if 'locus_tag' in feature.qualifiers:
                    phases[feature.qualifiers['locus_tag'][0]] = feature.strand

        # Example Reference Name: gi|29165615|ref|NC_002745.2|
        ref_name = "gi|{0}|ref|{1}.{2}|".format(
            gb.annotations['gi'],
            gb.name,
            gb.annotations['sequence_version']
        )
        reference = Reference.objects.get(name=ref_name)

        # Loop through Annotation objects
        for obj in Annotation.objects.filter(reference=reference):
            if obj.locus_tag in phases:
                print('{0} --> {1}'.format(
                    obj.locus_tag, phases[obj.locus_tag]
                ))
                obj.strand = phases[obj.locus_tag]
                obj.save()
