""" Estimate partitions. """
import numpy as np
import random

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Predict optimal substring groupings for partitions.'

    def add_arguments(self, parser):
        parser.add_argument('counts', metavar='SUBSTRING_COUNTS',
                            help='Text file of substring counts.')
        parser.add_argument('--partitions', type=int, dest='partitions',
                            default=10,
                            help='Total partitions to create. (Default = 10)')
        parser.add_argument('--repetitions', type=int, dest='repetitions',
                            default=1,
                            help='Number of times to repeat creation.')

    def create_partitions(self, substrings, total, end):
        partitions = {}
        processed = {}
        # Create strating points
        counts = {}
        for substring, count in substrings.iteritems():
            counts[count] = substring

        for count in sorted(counts.keys(), reverse=True)[0:end]:
            substring = counts[count]
            processed[substring] = True
            partitions[substring] = {
                'members': [substring],
                'total': int(count)
            }

        keys = list(partitions.keys())
        for substring in substrings.keys():
            count = substrings[substring]
            if substring not in processed:
                random.shuffle(keys)
                for p in keys:
                    partition = partitions[p]
                    if (count + partition['total']) <= total:
                        partition['members'].append(substring)
                        partition['total'] = count + partition['total']
                        processed[substring] = True
                        break
                    else:
                        pass
            else:
                pass

            # still not in there, add it to current min
            if substring not in processed:
                min_total = 10 ** 16
                key = None
                for p in keys:
                    partition = partitions[p]
                    if partition['total'] <= min_total:
                        min_total = partition['total']
                        key = p

                partitions[key]['members'].append(substring)
                partitions[key]['total'] = count + partitions[key]['total']
                processed[substring] = True

        sizes = []
        for p in partitions:
            sizes.append(partitions[p]['total'])
        a = np.array(sizes)
        diff = abs(np.max(a) - np.min(a))

        return [partitions, diff, np.max(a), np.min(a)]

    def handle(self, *args, **opts):
        # Read count file
        substrings = {}
        total = 0
        with open(opts['counts'], "r") as f:
            for line in f:
                line = line.strip()
                substring, count = line.split('\t')
                substrings[substring] = int(count)
                total += int(count)

        size = total / opts['partitions']

        top_partition = None
        min_diff = 10 ** 14
        for i in xrange(opts['repetitions']):
            partition, diff_size, max_size, min_size = self.create_partitions(
                substrings, size, opts['partitions']
            )
            if diff_size < min_diff:
                min_diff = diff_size
                top_partition = partition

            print '{0}\t{1:,}\t{2:,}\t{3:,}\t{4:,}'.format(
                i, min_size, max_size, diff_size, min_diff
            )

        print '{0:,}\t{1:,}\t{2}'.format(total, size, len(substrings.keys()))
        total_members = 0
        sizes = []
        with open('partition.info', 'w') as a, open('partition.txt', 'w') as b:
            for p in sorted(top_partition.keys()):
                total_members += len(top_partition[p]['members'])
                sizes.append(len(top_partition[p]['members']))
                a.write('{0}\t{1}\t{2:,}\n'.format(
                    p,
                    len(top_partition[p]['members']),
                    top_partition[p]['total']
                ))

                for member in sorted(top_partition[p]['members']):
                    b.write('{0}\t{1}\n'.format(p, member))

        print len(substrings.keys()), total_members
        a = np.array(sizes)
        print np.min(a), np.mean(a), np.median(a), np.max(a)
