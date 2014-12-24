# !/usr/bin/python
import signal
import sys
import cmd
from query_parser import QueryParser
from query_executor import QueryExecutor

class Console(cmd.Cmd):
    __version__ = '0.1'
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "> "
        self.intro  = "appsrepo shell: version " + self.__version__
    
    def do_EOF(self, args):
            """Exit on system end of file character"""
            return self.do_exit(args)
    
    def do_EOF(self, args):
        """Exit on system end of file character (e.g., ctrl-D)"""
        print("\nBye")
        sys.exit(0)
    
    def do_exit(self, args):
        """Quits the shell."""
        print("\rBye")
        sys.exit(0)
    
    def default(self, line):
        """Evaluate the supplied commands"""
        # Evaluate supplied commands        
        query = QueryParser.explain(line.strip())
        # Execute the query
        QueryExecutor.execute(query)

def signal_handler(signal, frame):
    print('\rBye')
    sys.exit(0)

if __name__ == '__main__':
    # Register SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    console = Console()
    console.cmdloop()