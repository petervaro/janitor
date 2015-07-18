## INFO ##
## INFO ##

# Import python modules
from os.path           import join
from copy              import deepcopy
from collections       import OrderedDict
# TODO: Change ValueErrors in the __init__ method to
#       JSONDecodeError, when Python 3.5 will be released
from json              import load, dump#, JSONDecodeError

# Import janitor modules
from modules.tagger    import Tagger
from modules.prefixer  import Prefixer
from modules.versioner import Versioner
from orderedset        import OrderedSet



#------------------------------------------------------------------------------#
# Module level constants
_EXTEND_DEFAULT = 'extend_default'
_EXTENDERS      = 'update', 'extend'
_DEFAULT        = OrderedDict(
[
    ('exclude', OrderedDict(
    [
        # TODO: `names` should `files` instead for clearity
        ('names'             , (OrderedSet, OrderedSet(('.gitignore',
                                                        '.DS_Store',
                                                        'JANITOR')))),
        ('folders'           , (OrderedSet, OrderedSet(('.janitor',
                                                        '.git',
                                                        '__pycache__')))),
        ('extensions'        , (OrderedSet, OrderedSet(('a', 'o', 'os', 'so',
                                                        'dylib', 'dll', 'exe',
                                                        'pyc', 'pyo', 'jpg',
                                                        'jpeg', 'png', 'gif',
                                                        'pdf')))),
    ])),

    ('versioner', OrderedDict(
    [
        ('use'               , (bool, True)),
        ('major_max'         , (int, Versioner.MAJOR_MAX)),
        ('major_base'        , (int, Versioner.MAJOR_BASE)),
        ('minor_max'         , (int, Versioner.MINOR_MAX)),
        ('minor_base'        , (int, Versioner.MINOR_BASE)),
        ('maintenance_max'   , (int, Versioner.MAINTENANCE_MAX)),
        ('maintenance_base'  , (int, Versioner.MAINTENANCE_BASE)),
        ('build_max'         , (int, Versioner.BUILD_MAX)),
        ('build_base'        , (int, Versioner.BUILD_BASE)),
    ])),

    ('tagger', OrderedDict(
    [
        ('use'               , (bool, True)),
        ('exclude'           , (OrderedDict, OrderedDict())),
        ('words'             , (OrderedSet, Tagger.WORDS)),
        ('marks'             , (OrderedDict, Tagger.MARKS)),
    ])),

    ('prefixer', OrderedDict(
    [
        ('use'               , (bool, True)),
        ('exclude'           , (OrderedDict, OrderedDict())),
        ('tag'               , (str, Prefixer.TAG)),
        ('align'             , (str, Prefixer.ALIGN_LEFT)),
        ('width'             , (int, Prefixer.WIDTH)),
        ('block'             , (int, Prefixer.BLOCK)),
    ])),
])



#------------------------------------------------------------------------------#
class Configer:

    # Class level constants
    FILE_NAME = 'JANITOR'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class InvalidConfigFilePath(Exception): pass
    class InvalidConfigFileFormat(Exception): pass
    class InvalidExtendDefaultOption(Exception): pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @classmethod
    def from_default(cls, **kwargs):
        return cls(config=deepcopy(_DEFAULT), **kwargs)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, config=None,
                       config_dir_path=None,
                       config_file_path=None):
        # If custom file-path and file-name specified
        if config_file_path is not None:
            self._file_path = config_file_path
        # If custom file-path, but default file-name specified
        elif config_dir_path is not None:
            self._file_path = join(config_dir_path, Configer.FILE_NAME)
        # If no file-path specified AND not even
        # an already processed configuration passed
        elif config is None:
            raise Configer.InvalidConfigFilePath

        # If no config object passed
        if config is None:
            # If config file exists
            try:
                with open(self._file_path, mode='r') as file:
                    config = load(file, object_pairs_hook=OrderedDict)
            # If config file is invalid
            except ValueError as e:
                raise Configer.InvalidConfigFileFormat(str(e))
            # If no config file found
            except FileNotFoundError:
                config = OrderedDict()

        # Store config object
        self._conf = config

        # Go through all sections
        for section_name, section_defaults in _DEFAULT.items():
            # If section is defined by the user
            try:
                section_user = self._conf[section_name]
            # If section is missing from user's config
            except KeyError:
                self._conf[section_name] = \
                    OrderedDict((k, v) for k, (t, v) in section_defaults.items())
                continue

            # Get/set extend_default option
            extend_default = set(section_user.get(_EXTEND_DEFAULT, ()))

            # Go through all options
            for option, (type_cast, default) in section_defaults.items():
                # If value is defined by the user
                try:
                    defined = type_cast(section_user[option])
                    #print(defined)
                    # If option should extend the default values
                    if (option in extend_default):
                        default = deepcopy(default)
                        # Try to extend cloned defaults
                        for method_name in _EXTENDERS:
                            try:
                                getattr(default, method_name)(defined)
                                break
                            except AttributeError:
                                continue
                        # If cloned default cannot be extended
                        else:
                            raise Configer.InvalidExtendDefaultOption
                        # Store extended defaults
                        raise KeyError
                    # Store casted user defined value
                    section_user[option] = defined
                # If value is not defined by the user
                except KeyError:
                    section_user[option] = default
                # Value cannot be casted to the proper type
                except ValueError as e:
                    raise Configer.InvalidConfigFileFormat(str(e))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __repr__(self):
        return repr(self._conf)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __getitem__(self, section):
        return self._conf[section]


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
