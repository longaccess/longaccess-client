try: 
    from blessings import Terminal
    WITH_BLESSINGS = True
except ImportError:
    WITH_BLESSINGS = False

class RichTextUI:
    def __init__(self):

        if WITH_BLESSINGS:
            t = Terminal()
            self.width = t.width
        else:
            self.width = 78

        h_titles = '#   ID         STATUS   SIZE   DATE         TITLE'
        h_pattern= '--- ---------- -------- ------ ------------ ---------------------------------'
        h_pattern= h_pattern.ljust(self.width, '-')
        self.archive_design = {
            'titles': h_titles,
            'pattern': h_pattern,
            'frmt': "{:0%sd} {:>%s} {:<%s} {:>%s} {:<%s} {:<%s}" % tuple( len(p) for p in h_pattern.split(' ')) 
        }

        h_titles = 'ID         SIZE   DATE       TITLE'
        h_pattern= '---------- ------ ---------- ---------------------------------'
        h_pattern= h_pattern.ljust(self.width, '-')
        self.cert_design = {
            'titles': h_titles,
            'pattern': h_pattern,
            'frmt': "{:>%s} {:>%s} {:<%s} {:<%s}" % tuple( len(p) for p in h_pattern.split(' ')) 
        }
        
    def print_archives_header(self):
        print self.archive_design['titles']
        print self.archive_design['pattern']

    def print_archives_line(self, archive):
        h_parts = self.archive_design['pattern'].split()
        if len(archive['title'])>=len(h_parts[-1]):
            archive_title = archive['title'][0:len(h_parts[-1])-2]+'..'
        else:
            archive_title = archive['title']
        archive_title = archive_title.replace('\n',' ')
        print self.archive_design['frmt'].format(
            archive['num'],
            archive['cert'],
            archive['status'],
            archive['size'],
            archive['created'].strftime('%Y-%m-%d'),
            archive_title.encode('utf-8')) 

    def print_certificates_header(self):
        print self.cert_design['titles']
        print self.cert_design['pattern']

    def print_certificates_line(self, certificate):
        h_parts = self.cert_design['pattern'].split()
        if len(certificate['title'])>=len(h_parts[-1]):
            certificate_title = certificate['title'][0:len(h_parts[-1])-2]+'..'
        else:
            certificate_title = certificate['title']
        certificate_title = certificate_title.replace('\n', ' ')
        print self.cert_design['frmt'].format(
            certificate['aid'],
            certificate['size'],
            certificate['created'].strftime('%Y-%m-%d'),
            certificate_title.encode('utf-8')) 
    
