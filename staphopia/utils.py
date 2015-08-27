
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
