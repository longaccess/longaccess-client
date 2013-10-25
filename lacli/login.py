from lacli.decorators import command
from lacli.command import LaBaseCommand


class LaLoginCommand(LaBaseCommand):
    """Login to Longaccess

    Usage: lacli login
    """
    prompt = 'lacli:login> '

    def makecmd(self, options):
        return "login"

    @command()
    def do_login(self):
        """
        Usage: login
        """
        print "authentication succesfull"
