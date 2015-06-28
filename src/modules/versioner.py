## INFO ##
## INFO ##

# Import python modules
from os.path import join

#------------------------------------------------------------------------------#
class Versioner:

    # Class level constants
    FILE_NAME        = 'version'
    MAJOR            = 0
    MINOR            = 0
    MAINTENANCE      = 1
    BUILD            = 0
    MAJOR_MAX        = 0
    MINOR_MAX        = 9
    MAINTENANCE_MAX  = 9
    BUILD_MAX        = 99
    MAJOR_BASE       = 10
    MINOR_BASE       = 10
    MAINTENANCE_BASE = 10
    BUILD_BASE       = 10
    INC_MAJOR        = 'major'
    INC_MINOR        = 'minor'
    INC_MAINTENANCE  = 'maintenance'
    INC_BUILD        = 'build'
    #VERSION_FORMAT   =
    #DATETIME_FORMAT  =

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def version(self):
        return '.'.join((self._major,
                         self._minor,
                         self._maintenance,
                         self._build)) + date


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, path, options=None, **limits):
        # Set values
        self._path             = join(path, Versioner.FILE_NAME)
        self._major_max        = limits.get('major_max', Versioner.MAJOR_MAX)
        self._major_base       = limits.get('minor_max', Versioner.MINOR_MAX)
        self._maintenance_max  = limits.get('maintenance_max', Versioner.MAINTENANCE_MAX)
        self._build_max        = limits.get('build_max', Versioner.BUILD_MAX)
        self._major_base       = limits.get('major_base', Versioner.MAJOR_BASE)
        self._major_base       = limits.get('minor_base', Versioner.MINOR_BASE)
        self._maintenance_base = limits.get('maintenance_base', Versioner.MAINTENANCE_BASE)
        self._build_base       = limits.get('build_base', Versioner.BUILD_BASE)

        # Get current version
        try:
            with open(self._path, mode='r+') as file:
                pass
        except FileNotFoundError:
            pass

        self.version = '1.0.0.000 (20150621)'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def to_file(self):
        pass
        #with open(self._path, mode='w') as file:
        #    pass
