from blessings import Terminal

class RichTextUI:
    def __init__(self):
        t = Terminal()
        self.width = t.width

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
        self.capsule_design = {
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
        print self.archive_design['frmt'].format(
            archive['num'],
            archive['cert'],
            archive['status'],
            archive['size'],
            archive['created'].strftime('%Y-%m-%d'),
            archive_title) 

    