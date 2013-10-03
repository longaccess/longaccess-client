import os
from behave import step
from tempfile import NamedTemporaryFile
from errno import EPIPE
from multiprocessing import Process
from tempfile import mkdtemp


@step(u'an empty file "{name}"')
def empty_file(context, name):
    assert name not in context.files
    f = NamedTemporaryFile()
    assert os.path.exists(f.name), "Path exists"
    assert os.path.isfile(f.name), "Path is file"
    context.files[name] = f


@step(u'a file "{name}" with contents')
def file_with_content(context, name):
    assert name not in context.files
    empty_file(context, name)
    context.files[name].write(context.text)


@step(u'a file "{name}" with {mb} mb of zeroes')
def file_zeroes(context, name, mb):
    assert name not in context.files
    empty_file(context, name)
    context.files[name].truncate(int(mb) * 1024 * 1024)


@step(u'a fifo "{name}" with {mb} mb of zeroes')
def fifo_zeroes(context, name, mb):
    assert name not in context.dirs
    assert name not in context.fifo
    dname = mkdtemp()
    fname = os.path.join(dname, 'fifo')
    os.mkfifo(fname)
    mb = int(mb)

    def run_fifo():
        import sys
        sys.stdout = sys.stderr = open('/tmp/fiflog', 'w')
        sys.stderr.write("START")
        fifo = open(fname, 'w')
        for _ in xrange(mb*1024):
            try:
                fifo.write('0' * 1024)
                print ("wrote 1k\n")
                sys.stdout.flush()
                fifo.flush()
            except IOError as e:
                if e.errno != EPIPE:
                    raise
        fifo.close()

    proc = Process(target=run_fifo)
    proc.start()
    context.fifo[fname] = proc
    context.dirs[name] = dname
    context.files[name] = open(fname, 'r')
