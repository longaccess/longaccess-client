import os
from behave import step
from behave_cli import format_vars
from tempfile import NamedTemporaryFile, mkdtemp
from errno import EPIPE
from multiprocessing import Process


@step(u'an empty file "{name}"')
def empty_file(context, name, directory=None):
    assert name not in context.files
    f = NamedTemporaryFile(dir=directory)
    assert os.path.exists(f.name), "Path exists"
    assert os.path.isfile(f.name), "Path is file"
    context.files[name] = f


@step(u'an empty folder "{name}"')
def empty_dir(context, name):
    assert name not in context.dirs
    dname = mkdtemp()
    assert os.path.isdir(dname), "Path is directory"
    context.dirs[name] = dname


@step(u'under "{directory}" an empty file "{name}"')
@format_vars
def file_under_dir(context, directory, name):
    empty_file(context, name, directory)


@step(u'file "{path}" is unreadable')
@format_vars
def file_unreadable(context, path):
    assert os.path.exists(path), "Path exists"
    os.chmod(path, 0)
    opened = False
    try:
        with open(path):
            opened = True
    except IOError:
        pass
    assert not opened


@step(u'directory "{path}" is unwritable')
@format_vars
def dir_unwritable(context, path):
    assert os.path.exists(path), "Path exists"
    assert os.path.isdir(path), "Is directory"
    os.chmod(path, 0)
    written = False
    try:
        NamedTemporaryFile(dir=path)
        written = True
    except OSError:
        pass
    assert not written


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
