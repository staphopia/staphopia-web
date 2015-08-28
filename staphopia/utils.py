
def timeit(method):
    import time

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r\t%2.2f sec' % (method.__name__, te - ts)
        return result

    return timed


def gziplines(fname):
    from subprocess import Popen, PIPE
    f = Popen(['zcat', fname], stdout=PIPE)
    for line in f.stdout:
        yield line


def read_fasta(fasta, compressed=False):
    id = None
    seq = []
    records = {}
    fh = None

    if compressed:
        fh = gziplines(fasta)
    else:
        fh = open(fasta, 'r')

    for line in fh:
        line = line.rstrip()
        if line.startswith('>'):
            if len(seq):
                records[id] = ''.join(seq)
                seq = []
            id = line[1:].split(' ')[0]
        else:
            seq.append(line)

    records[id] = ''.join(seq)

    return records
