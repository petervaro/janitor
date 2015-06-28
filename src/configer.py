## INFO ##
## INFO ##

# Import python modules
from os.path           import join
from collections       import OrderedDict
from configparser      import ConfigParser

# Import janitor modules
from modules.tagger    import Tagger
from modules.prefixer  import Prefixer
from modules.versioner import Versioner
from configer_types    import Bool, Int, Str, Set, List, Dict, OrdDict



#------------------------------------------------------------------------------#
# Module level constants
_DEFAULT = OrderedDict(
[
    ('black_list', OrderedDict(
    [
        ('names'             , Set(extensible=True,
                                   default={'.gitignore', '.DS_Store'})),
        ('folders'           , Set(extensible=True,
                                   default={'.janitor', '.git', '__pycache__'})),
        ('extensions'        , Set(extensible=True,
                                   default={'a', 'o', 'os', 'so', 'dylib',
                                            'dll', 'exe', 'pyc', 'pyo', 'jpg',
                                            'jpeg', 'png', 'gif', 'pdf'})),
    ])),

    ('versioner', OrderedDict(
    [
        ('use'               , Bool(default=True)),
        ('major_max'         , Int(default=Versioner.MAJOR_MAX)),
        ('major_base'        , Int(default=Versioner.MAJOR_BASE)),
        ('minor_max'         , Int(default=Versioner.MINOR_MAX)),
        ('minor_base'        , Int(default=Versioner.MINOR_BASE)),
        ('maintenance_max'   , Int(default=Versioner.MAINTENANCE_MAX)),
        ('maintenance_base'  , Int(default=Versioner.MAINTENANCE_BASE)),
        ('build_max'         , Int(default=Versioner.BUILD_MAX)),
        ('build_base'        , Int(default=Versioner.BUILD_BASE)),
    ])),

    ('tagger', OrderedDict(
    [
        ('use'               , Bool(default=True)),
        ('exclude_names'     , Set(extensible=True, default=set())),
        ('exclude_folders'   , Set(extensible=True, default=set())),
        ('exclude_extensions', Set(extensible=True, default=set())),
        ('words'             , List(extensible=True, default=Tagger.WORDS)),
        ('marks'             , OrdDict(extensible=True, default=Tagger.MARKS)),
    ])),

    ('prefixer', OrderedDict(
    [
        ('use'               , Bool(default=True)),
        ('exclude_names'     , Set(extensible=True, default=set())),
        ('exclude_folders'   , Set(extensible=True, default=set())),
        ('exclude_extensions', Set(extensible=True, default=set())),
        ('tag'               , Str(default=Prefixer.TAG)),
        ('align'             , Str(default=Prefixer.ALIGN_LEFT)),
        ('width'             , Int(default=Prefixer.WIDTH)),
        ('block'             , Str(default=Prefixer.BLOCK)),
    ])),
])



#------------------------------------------------------------------------------#
class Configer:

    # Class level constants
    FILE_NAME = 'JANITOR'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class InvalidConfigFilePath(Exception): pass
    class UnsupportedTypeForExtension(Exception): pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @classmethod
    def from_default(cls, **kwargs):
        config = ConfigParser()
        for section, options in _DEFAULT.items():
            config.add_section(section)
            section = config[section]
            for key, value in options.items():
                section[key] = value.raw_data
        # Create new instance
        return cls(config=config, **kwargs)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, config=None,
                       config_dir_path=None,
                       config_file_path=None):
        # If file path manually specified
        if config_file_path:
            self._file_path = config_file_path
        # If file path is the default one
        elif config_dir_path:
            self._file_path = join(config_dir_path, Configer.FILE_NAME)
        # If there is not file path and no config object passed
        elif not config:
            raise InvalidConfigFilePath

        # If no config object passed
        if not config:
            # Create config object
            config = ConfigParser()
            # If config file exists
            try:
                with open(self._file_path, mode='r') as file:
                    config.read_file(file)
            # If no config file found
            except FileNotFoundError:
                pass

        # Store config object as a simple dictionary
        self._conf = OrderedDict((s, OrderedDict(**o))
                                 for s, o in config.items() if s != 'DEFAULT')

        # Go through all sections
        for section, def_section in _DEFAULT.items():
            # If section is defined by the user
            try:
                usr_section = self._conf[section]
            # If section is missing from user's config
            except KeyError:
                # Use default options
                self._conf[section] = {k:v for k,v in def_section.items()}
                continue

            # Go through all options
            for key, data_type in def_section.items():
                # If value is defined by the user
                try:
                    usr_section[key] = data_type(raw_data=usr_section[key])
                # If value is not defined by the user
                except KeyError:
                    usr_section[key] = data_type
                    continue


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __repr__(self):
        return repr(self._conf)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __getitem__(self, key):
        try:
            section, option, *_ = key
            return self._conf[section][option].data
        except ValueError:
            return {k: v.data for k, v in self._conf[section].items()}


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def to_file(self):
        # TODO: This is exactly the same as in the `from_default` method =>
        #       unify this into a helper function or a private method
        config = ConfigParser()
        for section, options in self._conf.items():
            config.add_section(section)
            section = config[section]
            for key, value in options.items():
                section[key] = value.raw_data
        with open(self._file_path, mode='w') as file:
            config.write(file, space_around_delimiters=False)
        return self._file_path
