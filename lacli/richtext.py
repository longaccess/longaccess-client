try:
    from blessings import Terminal
    WITH_BLESSINGS = True
except ImportError:
    WITH_BLESSINGS = False

import sys
import time
import pyaml
from lacli.adf import creation


def format_size(bytes):
    size = ""
    if bytes:
        kib = bytes // 1024
        mib = kib // 1024
        gib = mib // 1024
        if not kib:
            size = "{} B".format(bytes)
        elif not mib:
            size = "{} KB".format(kib)
        elif not gib:
            size = "{} MB".format(mib)
        else:
            size = "{} GB".format(gib)
    return size


class RichTextUI:
    def __init__(self):

        if WITH_BLESSINGS:
            t = Terminal()
            self.width = t.width
        else:
            self.width = 78
        if not self.width:
            self.width = 78

        h_titles = '#   ID         STATUS    SIZE   DATE         TITLE'
        h_pattern = ('--- ---------- --------- ------ ------------ '
                     '---------------------------------')
        h_pattern = h_pattern.ljust(self.width, '-')
        h_frmt = "{:0%sd} {:>%s} {:<%s} {:>%s} {:<%s} {:<%s}" % tuple(
            len(p) for p in h_pattern.split(' '))
        self.archive_design = {
            'titles': h_titles,
            'pattern': h_pattern,
            'frmt': h_frmt
        }

        h_titles = 'ID         SIZE   DATE       TITLE'
        h_pattern = ('---------- ------ ---------- '
                     '---------------------------------')
        h_pattern = h_pattern.ljust(self.width, '-')
        h_frmt = "{:>%s} {:>%s} {:<%s} {:<%s}" % tuple(
            len(p) for p in h_pattern.split(' '))
        self.cert_design = {
            'titles': h_titles,
            'pattern': h_pattern,
            'frmt': h_frmt
        }

        h_titles = '#  ID      SIZE   FREE CREATED      EXPIRES      TITLE'
        h_pattern = ('-- ----- ------ ------ ------------ '
                     '------------ ------------------------------')
        h_pattern = h_pattern.ljust(self.width, '-')
        h_frmt = "{:0%sd} {:>%s} {:>%s} {:>%s} {:<%s} {:<%s} {:<%s}" % tuple(
            len(p) for p in h_pattern.split(' '))
        self.capsule_design = {
            'titles': h_titles,
            'pattern': h_pattern,
            'frmt': h_frmt
        }

    def print_archives_header(self):
        print self.archive_design['titles']
        print self.archive_design['pattern']

    def print_archives_line(self, archive):
        h_parts = self.archive_design['pattern'].split()
        if len(archive['title']) >= len(h_parts[-1]):
            archive_title = archive['title'][0:len(h_parts[-1])-2]+'..'
        else:
            archive_title = archive['title']
        archive_title = archive_title.replace('\n', ' ')
        print self.archive_design['frmt'].format(
            archive['num'],
            archive['cert'],
            archive['status'],
            archive['size'],
            archive['created'].strftime('%Y-%m-%d'),
            archive_title.encode('utf-8'))

    def print_capsules_header(self):
        print self.capsule_design['titles']
        print self.capsule_design['pattern']

    def print_capsules_line(self, capsule):
        h_parts = self.capsule_design['pattern'].split()
        if len(capsule['title']) >= len(h_parts[-1]):
            capsule_title = capsule['title'][0:len(h_parts[-1])-2]+'..'
        else:
            capsule_title = capsule['title']
        print self.capsule_design['frmt'].format(
            capsule['num'],
            capsule['id'],
            format_size(capsule['size']),
            format_size(capsule['remaining']),
            capsule['created'].strftime('%Y-%m-%d'),
            capsule['expires'].strftime('%Y-%m-%d'),
            capsule_title.encode('utf-8'))

    def print_certificates_header(self):
        print self.cert_design['titles']
        print self.cert_design['pattern']

    def print_certificates_line(self, certificate):
        h_parts = self.cert_design['pattern'].split()
        if len(certificate['title']) >= len(h_parts[-1]):
            certificate_title = certificate['title'][0:len(h_parts[-1])-2]+'..'
        else:
            certificate_title = certificate['title']
        certificate_title = certificate_title.replace('\n', ' ')
        print self.cert_design['frmt'].format(
            certificate['aid'],
            certificate['size'],
            certificate['created'].strftime('%Y-%m-%d'),
            certificate_title.encode('utf-8'))

    def print_certificates_list(self, certs, debug):
        if len(certs):
            self.print_certificates_header()
            for cert in sorted(certs.itervalues(), key=creation):
                aid = cert['signature'].aid
                title = cert['archive'].title
                size = format_size(cert['archive'].meta.size)
                self.print_certificates_line(certificate={
                    'aid': aid,
                    'size': size,
                    'title': title,
                    'created': cert['archive'].meta.created
                })
                if debug > 2:
                    for doc in cert.itervalues():
                        pyaml.dump(doc, sys.stdout)
                    print
            return True
        else:
            return False

    def countdown(self, num):
        print num,
        for n in reversed(range(num-1)):
            sys.stdout.flush()
            time.sleep(1)
            sys.stdout.write(", {}".format(n+1))
            yield ""
