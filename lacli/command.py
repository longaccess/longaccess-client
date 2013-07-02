import cmd

class LaCommand(cmd.Cmd):
    """ Our LA command line interface"""
    prompt='lacli> '  

    def do_tvmconf(self, line):
        """tvmconf
        reset TVM access configuration (key, token, etc)"""

        return True

    def do_EOF(self, fname):
        return True
	
