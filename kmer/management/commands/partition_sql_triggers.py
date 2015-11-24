""" Estimate partitions. """
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Predict optimal substring groupings for partitions.'

    def add_arguments(self, parser):
        parser.add_argument('partitions', metavar='PARTITIONS',
                            help='Two columns of partitions.')

    def handle(self, *args, **opts):
        # Read count file
        partitions = {}
        with open(opts['partitions'], "r") as f:
            for line in f:
                line = line.strip()
                partition, member = line.split('\t')

                if partition not in partitions:
                    partitions[partition] = []

                partitions[partition].append("'{0}'".format(member))

        print 'CREATE OR REPLACE FUNCTION kmer_string_insert_trigger()'
        print 'RETURNS TRIGGER AS $$'
        print 'BEGIN'
        first = True
        for partition, members in partitions.iteritems():
            if first:
                print '    IF ({0} IN ({1})) THEN'.format(
                    'substring(NEW.string, 25, 31)', ','.join(members)
                )
                first = False
            else:
                print '    ELSEIF ({0} IN ({1})) THEN'.format(
                    'substring(NEW.string, 25, 31)', ','.join(members)
                )
            print '        INSERT INTO kmer_string_{0} VALUES (NEW.*);'.format(
                partition
            )

        print '    ELSE'
        print("        RAISE EXCEPTION 'String not assigned to a table."
              " Please look into it!';")
        print '    END IF;'
        print '    RETURN NULL;'
        print 'END;'
        print '$$'
        print 'LANGUAGE plpgsql;'
        print '\n'
        print 'CREATE TRIGGER insert_kmer_string_trigger'
        print '  BEFORE INSERT ON kmer_string'
        print '  FOR EACH ROW EXECUTE PROCEDURE kmer_string_insert_trigger();'
        print ''
