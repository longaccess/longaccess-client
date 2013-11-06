from lacli.decorators import command
from lacli.command import LaBaseCommand
from lacli.log import getLogger
from re import match, IGNORECASE
from getpass import getpass


class LaLoginCommand(LaBaseCommand):
    """Login to Longaccess

    Usage: lacli login [<username> <password>]
    """
    prompt = 'lacli:login> '

    def makecmd(self, options):
        cmd = ["login"]
        if options['<username>']:
            cmd.append(options['<username>'])
            if options['<password>']:
                cmd.append(options['<password>'])

        return " ".join(cmd)

    @property
    def username(self):
        return self.prefs['api']['user']

    @username.setter
    def username(self, newuser):
        self.prefs['api']['user'] = newuser

    @property
    def password(self):
        return self.prefs['api']['pass']

    @password.setter
    def password(self, newpassword):
        self.prefs['api']['pass'] = newpassword

    @command(username=str, password=str)
    def do_login(self, username=None, password=None):
        """
        Usage: login [<username>] [<password>]
        """
        if username:
            self.username = username
            if password:
                self.password = password
            elif not self.batch:
                self.password = getpass("Password: ")

        # replace session for all commands
        self.session = self.registry.new_session()

        email = None
        try:
            email = self.session.account['email']
            print "authentication succesfull as", email
        except:
            getLogger().debug("auth failure", exc_info=True)
            print "authentication failed"

        if email and username and not self.batch:
            if match('y(es)?', self.input("Save credentials? "), IGNORECASE):
                self.registry.save_session(self.username, self.password)

    @command()
    def do_logout(self):
        """
        Usage: logout
        """
        self.username = None
        self.password = None
        self.registry.session = None
