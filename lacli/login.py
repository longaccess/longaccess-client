from lacli.cmdutil import command
from lacore.async import block
from lacli.command import LaBaseCommand
from lacore.log import getLogger
from lacli.exceptions import ApiNoSessionError
from lacore.exceptions import (ApiAuthException, ApiErrorException,
                               ApiUnavailableException)
from twisted.internet import defer
from re import match, IGNORECASE
from getpass import getpass


class LaLoginCommand(LaBaseCommand):
    """Login to Longaccess

    Usage: lacli login [<username> <password>]
    """
    prompt = 'lacli:login> '
    email = None

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

        save = (self.username, self.password)

        if not username:
            if self.batch:
                username = self.username
            else:
                username = self.input("Username/email: ")

        if not password:
            if self.batch:
                password = self.password
            else:
                password = getpass("Password: ")

        try:
            self.login_batch(username, password)
            print "authentication succesfull as", self.email
            if not self.batch:
                if self.username != save[0] or self.password != save[1]:
                    if match('y(es)?$', self.input("Save credentials? "),
                             IGNORECASE):
                        self.registry.save_session(
                            self.username, self.password)
        except Exception:
            getLogger().debug("auth failure", exc_info=True)
            print "authentication failed"

    def login_batch(self, username, password):
        block(self.login_async)(username, password)

    @defer.inlineCallbacks
    def login_async(self, username, password):
        self.username = username
        self.password = password
        session = self.registry.new_session()
        try:
            account = yield session.async_account
            self.email = account['email']
            self.session = session
            getLogger().debug("logged in {}".format(self.email))
        except ApiErrorException:
            raise
        except ApiUnavailableException:
            raise
        except ApiNoSessionError:
            raise
        except Exception as e:
            self.username = self.password = None
            getLogger().debug("auth failure", exc_info=True)
            raise ApiAuthException(username=username, exc=e)

    @command()
    def do_logout(self):
        """
        Usage: logout
        """
        self.logout_batch()

    def logout_batch(self):
        self.username = None
        self.password = None
        self.email = None
        self.registry.session = None
