from lacli.decorators import command
from lacli.command import LaBaseCommand


class LaLoginCommand(LaBaseCommand):
    """Login to Longaccess

    Usage: lacli login [<username> <password>]
    """
    prompt = 'lacli:login> '

    def __init__(self, session, cache, prefs, *args, **kwargs):
        super(LaLoginCommand, self).__init__(
            session, cache, prefs, *args, **kwargs)
        self.prefs = prefs

    def makecmd(self, options):
        return "login"

    @command(username=str, password=str)
    def do_login(self, username=None, password=None):
        """
        Usage: login [<username> <password>]
        """
        if username or 'user' in self.prefs['api']:
            if self.prefs['api']['user']:
                self.session.set_session_factory(None)
                print "authentication succesfull"
                return
        print "authentication failed"
