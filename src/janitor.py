#!/usr/bin/env python3
## INFO ##
## INFO ##

# Import python modules
from sys     import argv
from os      import (getcwd,
                     makedirs)
from os.path import (join,
                     isdir,
                     expanduser,
                     expandvars)

# Import janitor modules
from configer          import Configer
from modules.tagger    import Tagger
from modules.prefixer  import Prefixer
from modules.versioner import Versioner


# Module level constants
_MARKER     = '==> '
_INDENT     = ' '*8
_JPRINT     = '\033[32m{}\033[37;1mjanitor:\033[0m'.format(_MARKER)
_JERROR     = '\033[31m{}\033[37;1mjanitor: \033[31mError:\033[0m'.format(_MARKER)
_CACHE_DIR  = '.janitor'
_BOOL_LONG  = ('default', 'generate', 'help', 'md5',
               'rebuild', 'sha', 'update', 'version')
_WORD_LONG  = 'config', 'path'
_SPEC_LONG  = 'exclude', 'increase'
_SPEC_VALID = {'exclude' : {'tagger', 'prefixer', 'versioner'},
               'increase': {Versioner.INC_MAJOR,
                            Versioner.INC_MINOR,
                            Versioner.INC_MAINTENANCE,
                            Versioner.INC_BUILD}}
_ARGS_ALL   = set(_BOOL_LONG + _WORD_LONG + _SPEC_LONG)
_SHORT_TO_LONG = {
    'c': 'config'  , 'C': 'config',
    'd': 'default' , 'D': 'default',
    'e': 'exclude' , 'E': 'exclude',
    'g': 'generate', 'G': 'generate',
    'h': 'help'    , 'H': 'help',
    'i': 'increase', 'I': 'increase',
    'm': 'md5'     , 'M': 'md5',
    'p': 'path'    , 'P': 'path',
    'r': 'rebuild' , 'R': 'rebuild',
    's': 'sha'     , 'S': 'sha',
    'u': 'update'  , 'U': 'update',
    'v': 'version' , 'V': 'version',
}

_HELP = """
NAME
    janitor - light and fast project's administration maintainer utility

SYNOPSIS
    janitor [OPTION]...

DESCRIPTION
    Collects tagged comments from files, generates header-prefixes for
    sources and maintain version sequences of a project.

    -D, -d, --default
        Janitor will use its builtin default values and won't look for a config
        file. It could be used to test how janitor works, or can be used as
        "clean" solution not to include any extra files in a repository.

    -G, -g, --generate
        Generates a sample configuration file at the working path.

    -M, -m, --md5
        By default, janitor will use the `xxHash` method to hash the files in
        the working path. However this means, it needs the `pyhashxx` external
        module. By defining this argument, the execution will use the MD5
        hashing instead, which is a part of python's standard library.

    -R, -r, --rebuild
        Janitor will remove the cache, and regenerate it by processing all the
        files and folders. Specifying this argument can be useful, when for
        example the `prefixer`'s block is changed, so it needs to be updated in
        all files.

    -S, -s, --sha
        By default, janitor will use the `xxHash` method to hash the files in
        the working path. However this means, it needs the `pyhashxx` external
        module. By defining this argument, the execution will use the SHA
        hashing instead, which is a part of python's standard library.

    -U, -u, --update
        Janitor will update the cache, but won't change the files, nor increase
        the version sequences of the project. Defining this argument can be
        useful, right after the cloning/syncing from the version-control
        repository, as it won't change anything, but will keep the cache
        updated.

    -C=[FILE], -c=[FILE], --config=[FILE]
        By default janitor will look for a file named `{CONF}` in the working
        path. This behaviour can be altered by specifying an "external"
        configuration file. This can be useful, when lots of projects are using
        the exact same settings, and they can share the same `{CONF}` file.

    -E=[MOD], -e=[MOD], --exclude=[MOD]
        By default all the modules will be invoked during the execution. This
        behaviour can be altered by excluding a module (MOD). This argument only
        takes a single module, but the argument can be passed several times to
        exclude more than one modules. Invalid values will be omitted. The valid
        values are:
            - tagger
            - prefixer
            - versioner

    -I=[SEQ], -i=[SEQ], --increase=[SEQ]
        By default the `versioner` module will increase the `build` sequence,
        and when it reaches its maximum value, it will increase the next
        sequence. This behaviour can be altered, by directly manipulating any of
        the sequences. The valid values are:
            - major
            - minor
            - maintenance
            - build

    -P[PATH], -p[PATH], --path=[PATH]
        By default janitor will use the current path as the working directory,
        but this behaviour can be altered, by specifying an alternative path.

    -V, -v, --version
        Prints the version of janitor.

    -H, -h, --help
        Prints this text.
""".format(CONF=Configer.FILE_NAME)


# Helper functions
#------------------------------------------------------------------------------#
def jprint(*args, **kwargs):
    print(_JPRINT, *args, **kwargs)

#------------------------------------------------------------------------------#
def jerror(*args, **kwargs):
    print(_JERROR, *args, **kwargs)


#------------------------------------------------------------------------------#
class Janitor:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @classmethod
    def from_cli(cls, *arguments):
        options = {}
        # Check all arguments
        for argument in arguments:
            # If argument is valid
            try:
                # If argument is word like
                if argument.startswith('--'):
                    argument, *value = argument[2:].split('=')
                    if argument not in _ARGS_ALL:
                        raise KeyError
                # If argument is a character
                elif argument.startswith('-'):
                    argument, *value = argument[1:].split('=')
                    argument = _SHORT_TO_LONG[argument]
            # If argument is invalid
            except KeyError:
                return jerror('Invalid argument {!r}'.format(argument))

            # If argument has an option
            try:
                if argument in _SPEC_LONG:
                    value = value[0]
                    if value:
                        options.setdefault(argument, set()).add(value)
                    else:
                        raise IndexError
                elif argument in _WORD_LONG:
                    value = value[0]
                    if value:
                        options[argument] = value
                    else:
                        raise IndexError
                elif argument in _BOOL_LONG:
                    options[argument] = True
            except IndexError:
                return jerror('No value passed to {!r}'.format(argument))

        # Pass options to new instance
        return cls(**options)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, help     = False,
                       version  = False,
                       rebuild  = False,
                       update   = False,
                       generate = False,
                       default  = False,
                       md5      = False,
                       sha      = False,
                       path     = None,
                       config   = None,
                       exclude  = set(),
                       increase = set()):
        # Print version information
        if version:
            return jprint('version: 1.0.0.000 (20150621)')

        # Print help information
        if help:
            # TODO: add version number to help text
            return print(_HELP)

        # Set working-path
        path = expanduser(expandvars(path or getcwd()))
        jprint('Sets work path:\n{}{}'.format(_INDENT, path))

        # Create cache directory if does not exist
        cache_dir = join(path, _CACHE_DIR)
        makedirs(cache_dir, exist_ok=True)
        jprint('Sets cache directory:\n{}{}'.format(_INDENT, cache_dir))


        #configer = Configer(path=cache_dir, )

        # Create sample config file if specified
        if generate:
            configer = Configer.from_default(config_dir_path=path)
            return jprint('Generates configuration file:'
                          '\n{}{}'.format(_INDENT, configer.to_file()))

        # Set configuration
        if default:
            configer = Configer.from_default()
            jprint('Uses default configuration')
        elif config:
            config = expanduse(expandvars(config))
            configer = Configer(config_file_path=config)
            jprint('Uses manually specified configuration file:'
                   '\n{}{}'.format(_INDENT, config))
        else:
            configer = Configer(config_dir_path=path)
            jprint('Uses configuration file:'
                   '\n{}{}'.format(_INDENT, join(path, Configer.FILE_NAME)))

        return print(configer)

        # Check increase options
        for option in increase:
            if option not in _SPEC_VALID['increase']:
                return jerror("{!r} is invalid for 'increase'".format(option))
        # Increase version number
        if increase:
            versioner = Versioner(path=cache_dir,
                                  options=increase,
                                  **configer['versioner'])
            versioner.to_file()
            return jprint('Current version is: {}'.format(versioner.version))

        # Import hashing
        if md5:
            from hashlib import md5
            hasher = md5
            jprint('Uses MD5 hashing algroithm')
        elif sha:
            from hashlib import sha1
            hasher = sha1
            jprint('Uses SHA1 hashing algroithm')
        #else:
        #    from pyhashxx import hash
        #    jprint('Uses xxHash hashing algorithm')

        # Rebuild or update
        if rebuild:
            jprint('Rebuilds cache files')
            return
        elif update:
            jprint('Updates cache files')
            return

        # Exclude modules

        # Collect all changed files
        jprint('Scans all files in:\n{}{}'.format(_INDENT, path))

        # Go through each module and pass the necessary infos to them



#------------------------------------------------------------------------------#
if __name__ == '__main__':
    Janitor.from_cli(*argv[1:])
