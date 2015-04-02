import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import socket
import time

from datatypes.config import Section

##############################################################################
#
##############################################################################

class Config(object):

    """
    MODEL:

    1. Files specified in the "include" attribute are read recursively.
    2. Starts with "include" set to ["environment.py", "secrets.py", "system.py"]
    3. These may include other customization files that override standard config.
    4. Do not check in these customization files.
    5. Word hostname in names is replaced by the actual hostname before inclusion.
    6. The hostname customization files are meant to be checked in.

    """

    #########################################

    class Config(object):

        def __init__(self):

            self.path = Section()

            self.path.root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.path.config = os.path.join(self.path.root, 'config')
            self.path.run = os.path.join(self.path.root, 'run')
            self.path.logs = os.path.join(self.path.root, 'logs')
            self.path.www = os.path.join(self.path.root, 'www')

            self.hostname = socket.gethostname()
            self.include = ["environment.py", "secrets.py", "system.py"]
            self._included = {}
            self._include()

        #########################################

        def _include(self):

            if not hasattr(self, "include"):
                return

            include = self.include

            del self.include

            for name in include:

                name = name.replace("hostname", self.hostname)

                if name in self._included:
                    raise Exception("recursive include: " + name)
                else:
                    self._included[name] = True

                path = os.path.join(self.path.config, name)

                try:
                    open(path, "r")
                except:
                    continue

                execfile(path, globals(), self.__dict__)

                self._include()

    #########################################

    def __init__(self):
        object.__setattr__(self, "_config", self.Config())

    #########################################

    def __getattr__(self, name):
        return getattr(self._config, name)

    def __setattr__(self, name, value):
        return setattr(self._config, name, value)

##############################################################################
#
##############################################################################

config = Config()
