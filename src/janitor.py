#!/usr/bin/env python3
## INFO ##
## INFO ##

# Import python modules
from textwrap    import wrap
from time        import sleep
from sys         import (argv,
                         exit,
                         stderr)
from shutil      import rmtree
from os          import (walk,
                         chdir,
                         getcwd,
                         makedirs,
                         EX_USAGE,
                         EX_CONFIG)
from os.path     import (join,
                         isdir,
                         abspath,
                         splitext,
                         basename,
                         expanduser,
                         expandvars)
from collections import OrderedDict
from subprocess  import check_output

# Import janitor modules
from checker           import Checker
from configer          import Configer
from modules.tagger    import Tagger
from modules.prefixer  import Prefixer
from modules.versioner import Versioner


# TODO: If `janitor` not running in a terminal, remove colors
#       To detect this, use the `os.isatty()` function

# Module level constants
_MARKER        = '==> '
_INDENT        = ' '*4
_JPRINT        = '\033[32;1m{}\033[37mjanitor:\033[0m'.format(_MARKER)
_JERROR        = '\033[31;1m{}\033[37mjanitor: \033[31mError:\033[0m'.format(_MARKER)
_CACHE_DIR     = '.janitor'
_MODULES       = 'versioner', 'tagger', 'prefixer'
_MOD_USE_FILE  = _MODULES[1:]
_MOD_NAME_LEN  = len(max(*_MOD_USE_FILE, key=len)) + 1
_SKIP          = '{{}}\033[37;1m{{:<{}}}\033[33m skips\033[37m:\033[0m '.format(_MOD_NAME_LEN)
_USE           = '{{}}\033[37;1m{{:<{}}}\033[32m uses\033[37m:\033[0m  '.format(_MOD_NAME_LEN)
_BOOL_LONG     = ('default', 'generate', 'help', 'kill', 'md5',
                  'rebuild', 'sha', 'update', 'version', 'watch')
_WORD_LONG     = 'config', 'path', 'time'
_SPEC_LONG     = 'exclude', 'increase'
_SPEC_VALID    = {'exclude' : {'tagger', 'prefixer', 'versioner'},
                  'increase': {Versioner.INC_MAJOR,
                               Versioner.INC_MINOR,
                               Versioner.INC_MAINTENANCE,
                               Versioner.INC_BUILD}}
_ARGS_ALL      = set(_BOOL_LONG + _WORD_LONG + _SPEC_LONG)
_SHORT_TO_LONG = {
    'c': 'config'  , 'C': 'config',
    'd': 'default' , 'D': 'default',
    'e': 'exclude' , 'E': 'exclude',
    'g': 'generate', 'G': 'generate',
    'h': 'help'    , 'H': 'help',
    'i': 'increase', 'I': 'increase',
    'k': 'kill'    , 'K': 'kill',
    'm': 'md5'     , 'M': 'md5',
    'p': 'path'    , 'P': 'path',
    'r': 'rebuild' , 'R': 'rebuild',
    's': 'sha'     , 'S': 'sha',
    't': 'time'    , 'T': 'time',
    'u': 'update'  , 'U': 'update',
    'v': 'version' , 'V': 'version',
    'w': 'watch'   , 'W': 'watch',
}

_HELP = OrderedDict((
    ('\033[37;1mNAME\033[0m',
        "janitor - light and fast project's administration maintainer utility"),

    ('\033[37;1mSYNOPSIS\033[0m',
        'janitor [OPTION]...'),

    ('\033[37;1mDESCRIPTION\033[0m',
        'Collects tagged comments from files, generates header-prefixes for '
        'sources and maintain version sequences of a project.'),

    ('_DESCRIPTION', OrderedDict((
        ('\033[37;1m-D\033[0m, \033[37;1m-d\033[0m, \033[37;1m--default\033[0m',
            "Janitor will use its builtin default values and won't look for a "
            "config file. It could be used to test how janitor works, or can "
            "be used as 'clean' solution not to include any extra files in a "
            "repository."),

        ('\033[37;1m-G\033[0m, '
         '\033[37;1m-g\033[0m, '
         '\033[37;1m--generate\033[0m',
            'Generates a sample configuration file at the working path.'),

        ('\033[37;1m-M\033[0m, '
         '\033[37;1m-m\033[0m, '
         '\033[37;1m--md5\033[0m',
            "By default, janitor will use the `xxHash` method to hash the "
            "files in the working path. However this means, it needs the "
            "`pyhashxx` external module. By defining this argument, the "
            "execution will use the MD5 hashing instead, which is a part of "
            "python's standard library."),

        ('\033[37;1m-R\033[0m, '
         '\033[37;1m-r\033[0m, '
         '\033[37;1m--rebuild\033[0m',
            'Janitor will remove the cache, and regenerate it by processing '
            'all the files and folders. Specifying this argument can be '
            "useful, when for example the `prefixer`'s block is changed, so it "
            'needs to be updated in all files.'),

        ('\033[37;1m-S\033[0m, '
         '\033[37;1m-s\033[0m, '
         '\033[37;1m--sha\033[0m',
            'By default, janitor will use the `xxHash` method to hash the '
            'files in the working path. However this means, it needs the '
            '`pyhashxx` external module. By defining this argument, the '
            'execution will use the SHA hashing instead, which is a part of '
            "python's standard library."),

        ('\033[37;1m-U\033[0m, '
         '\033[37;1m-u\033[0m, '
         '\033[37;1m--update\033[0m',
            "anitor will update the cache, but won't change the files, nor "
            'increase the version sequences of the project. Defining this '
            'argument can be useful, right after the cloning/syncing from the '
            "version-control repository, as it won't change anything, but will "
            'keep the cache updated.'),

        ('\033[37;1m-K\033[0m, '
         '\033[37;1m-k\033[0m, '
         '\033[37;1m--kill\033[0m',
            'Remove everything from the work path which is janitor related.'),

        ('\033[37;1m-W\033[0m, '
         '\033[37;1m-w\033[0m, '
         '\033[37;1m--watch\033[0m',
            'Constantly running and checking for changes.'),

        ('\033[37;1m-T=[SECS]\033[0m, '
         '\033[37;1m-t=[SECS]\033[0m, '
         '\033[37;1m--time=[SECS]\033[0m',
            'Specify time interval (in seconds) to look for file changes. The '
            'default value is 10 seconds. This option is only meaningful when '
            'passed with `--watch`.'),

        ('\033[37;1m-C=[FILE]\033[0m, '
         '\033[37;1m-c=[FILE]\033[0m, '
         '\033[37;1m--config=[FILE]\033[0m',
            ('By default janitor will look for a file named `{CONF}` in the '
             'working path. This behaviour can be altered by specifying an '
             '"external" configuration file. This can be useful, when lots of '
             'projects are using the exact same settings, and they can share '
             'the same `{CONF}` file.').format(CONF=Configer.FILE_NAME)),

        ('\033[37;1m-E=[MOD]\033[0m, '
         '\033[37;1m-e=[MOD]\033[0m, '
         '\033[37;1m--exclude=[MOD]\033[0m',
            'By default all the modules will be invoked during the execution. '
            'This behaviour can be altered by excluding a module (MOD). This '
            'argument only takes a single module, but the argument can be '
            'passed several times to exclude more than one modules. Invalid '
            'values will be omitted. The valid values are: tagger, prefixer '
            'and versioner.'),

        ('\033[37;1m-I=[SEQ]\033[0m, '
         '\033[37;1m-i=[SEQ]\033[0m, '
         '\033[37;1m--increase=[SEQ]\033[0m',
            'By default the `versioner` module will increase the `build` '
            'sequence, and when it reaches its maximum value, it will increase '
            'the next sequence. This behaviour can be altered, by directly '
            'manipulating any of the sequences. The valid values are: major, '
            'minor, maintenance and build.'),

        ('\033[37;1m-P=[PATH]\033[0m, '
         '\033[37;1m-p=[PATH]\033[0m, '
         '\033[37;1m--path=[PATH]\033[0m',
            'By default janitor will use the current path as the working '
            'directory, but this behaviour can be altered, by specifying an '
            'alternative path.'),

        ('\033[37;1m-V\033[0m, '
         '\033[37;1m-v\033[0m, '
         '\033[37;1m--version\033[0m',
            'Prints the version of janitor.'),

        ('\033[37;1m-H\033[0m, '
         '\033[37;1m-h\033[0m, '
         '\033[37;1m--help\033[0m',
            'Prints this text.'),
    )))
))



# Helper functions
#------------------------------------------------------------------------------#
def help_printer(data,
                 width =80,
                 indent='',
                 level =0):
    # Create indentations and length which left
    spaces_1 = indent*level
    spaces_2 = spaces_1 + indent
    length_1 = width - len(spaces_1)
    length_2 = width - len(spaces_2)

    # Process input data
    for key, value in data.items():
        # If value is a dictionary
        try:
            help_printer(value, width, indent, level + 1)
        # If value is a string
        except AttributeError:
            # Wrap both key and value
            for indent, lines in ((spaces_1, wrap(key, width=length_1)),
                                  (spaces_2, wrap(value, width=length_2))):
                # Print lines with indentation
                for line in lines:
                    print(indent, line, sep='')
            # Separate blocks with a single new line
            print()

#------------------------------------------------------------------------------#
def jprint(*args, **kwargs):
    print(_JPRINT, *args, **kwargs)

#------------------------------------------------------------------------------#
def jerror(*args, **kwargs):
    print(_JERROR, file=stderr, *args, **kwargs)

#------------------------------------------------------------------------------#
def jskip(indent, owner, *args, **kwargs):
    print(_SKIP.format(indent, owner + ':'), *args, **kwargs)

#------------------------------------------------------------------------------#
def juse(indent, owner, *args, **kwargs):
    print(_USE.format(indent, owner + ':'), *args, **kwargs)


#------------------------------------------------------------------------------#
class Janitor:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class Skip(Exception): pass
    class FinishedWithoutError(Exception): pass


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
                jerror('Invalid argument {!r}'.format(argument))
                exit(EX_USAGE)

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
                jerror('No value passed to {!r}'.format(argument))
                exit(EX_USAGE)

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
                       kill     = False,
                       watch    = False,
                       time     = 10.0,
                       path     = None,
                       config   = None,
                       exclude  = set(),
                       increase = set()):
        try:
            # Print version information
            if version:
                return jprint('version: 1.0.0.000 (20150621)')

            # Print help information
            if help:
                # TODO: add version number to help text
                _, width = (int(v) for v in
                                check_output('stty size',
                                             shell=True).decode('utf-8').split())
                return help_printer(_HELP, width, _INDENT)

            # Set working-path
            path = abspath(expanduser(expandvars(path or getcwd())))
            chdir(path)
            jprint('Sets work path:\n{}{}'.format(_INDENT, path))

            # Create cache directory if does not exist
            cache_dir = join(path, _CACHE_DIR)
            makedirs(cache_dir, exist_ok=True)
            jprint('Sets cache directory:\n{}{}'.format(_INDENT, cache_dir))

            # Remove everything and return
            if kill:
                jprint('Removes every janitor data from work path')
                rmtree(cache_dir, ignore_errors=True)
                raise Janitor.FinishedWithoutError

            # Create sample config file if specified
            if generate:
                configer = Configer.from_default(config_dir_path=path)
                jprint('Generates configuration file:'
                       '\n{}{}'.format(_INDENT, configer.to_file()))
                raise Janitor.FinishedWithoutError

            # Set configuration
            try:
                if default:
                    configer = Configer.from_default()
                    jprint('Uses default configuration')
                elif config:
                    config = expanduser(expandvars(config))
                    configer = Configer(config_file_path=config)
                    jprint('Uses manually specified configuration file:'
                           '\n{}{}'.format(_INDENT, config))
                else:
                    configer = Configer(config_dir_path=path)
                    jprint('Uses configuration file:'
                           '\n{}{}'.format(_INDENT, join(path, Configer.FILE_NAME)))
            except Configer.InvalidConfigFileFormat as e:
                jerror('Invalid JSON format in the configuration file')
                jerror(e)
                exit(EX_CONFIG)

            ## If use the `versioner` module
            #if configer['versioner']['use']:
            #    pass

            ## Check increase options
            #for option in increase:
            #    if option not in _SPEC_VALID['increase']:
            #        return jerror("{!r} is invalid for 'increase'".format(option))
            ## Increase version number
            #if increase:
            #    versioner = Versioner(path=cache_dir,
            #                          options=increase,
            #                          **configer['versioner'])
            #    versioner.to_file()
            #    return jprint('Current version is: {}'.format(versioner.version))

            # Import hashing algorithm
            if md5:
                hash_id = 0
                from hashlib  import md5    as hasher
                jprint('Uses MD5 hashing algorithm')
            elif sha:
                hash_id = 1
                from hashlib  import sha1   as hasher
                jprint('Uses SHA1 hashing algorithm')
            else:
                hash_id = 2
                try:
                    from pyhashxx import Hashxx as hasher
                    jprint('Uses xxHash hashing algorithm')
                except ImportError:
                    jerror('cannot use default hashing: '
                           'pyhashxx is not installed')
                    exit(EX_CONFIG)

            # Create checker
            checker = Checker(cache_dir, hash_id, hasher)

            # Rebuild or update
            if rebuild:
                jprint('Rebuilds cache files')
                checker.rebuild()

            # Collect all-excludes
            all_exclude = configer['exclude']
            for module in _MOD_USE_FILE:
                if configer[module]['use']:
                    mod_exclude = configer[module]['exclude']
                    for type in all_exclude:
                        try:
                            all_exclude[type] &= mod_exclude[type]
                        except KeyError:
                            pass

            # If watching look for time
            if watch:
                try:
                    time = float(time)
                    jprint('Sets watch time interval to: {} seconds'.format(time))
                except ValueError:
                    jerror('Invalid value for `time`: '
                           '{!r} is not a floating point number'.format(time))
                    exit(EX_CONFIG)

            # Go through each module and pass the necessary infos to them
            first_cycle = True
            while True:
                if first_cycle:
                    jprint('Walks through all files and folders in work path:')
                changed_files = []
                for root, dirs, files in walk(path):
                    # If skip this folder and all subfolders for every module
                    if root in all_exclude['folders']:
                        if first_cycle:
                            jskip(_INDENT, '<ALL>', join(root, '*'), sep='')
                        dirs.clear()
                        continue

                    # If skip subfolder
                    for dir in dirs:
                        if dir in all_exclude['folders']:
                            if first_cycle:
                                jskip(_INDENT, '<ALL>', join(root, dir, '*'))
                            dirs.remove(dir)

                    # Go through all files
                    for file in files:
                        _, ext = splitext(file)
                        # If extension or the filepath is on the black-list
                        if (ext in all_exclude['extensions']     or
                            ext[1:] in all_exclude['extensions'] or
                            file in all_exclude['names']):
                                if first_cycle:
                                    jskip(_INDENT, '<ALL>', join(root, file))
                                continue

                        # If file changed
                        file = join(root, file)
                        if checker.is_changed(file):
                            changed_files.append(file)
                            # If this is an update cycle only
                            if update:
                                continue
                            # Go through each module
                            for module in _MOD_USE_FILE:
                                mod_exclude = configer[module]['exclude']
                                # If file should be processed
                                try:
                                    # If this folder is excluded for module
                                    exclude = mod_exclude.get('folders', ())
                                    if (root in exclude or
                                        basename(root) in exclude):
                                            raise Janitor.Skip

                                    # If this extension is excluded for module
                                    exclude = mod_exclude.get('extensions', ())
                                    if (ext in exclude or
                                        ext[1:] in exclude):
                                            raise Janitor.Skip

                                    # If this file is excluded for module
                                    exclude = mod_exclude.get('names', ())
                                    if (file in exclude):
                                        raise Janitor.Skip

                                    # Use this file
                                    juse(_INDENT, module, file)
                                # If file should be skipped
                                except Janitor.Skip:
                                    jskip(_INDENT, module, file)
                                    continue

                # If any file changed since last
                # check, update and save cache
                if changed_files:
                    #for module in _MODULES:
                    #    module.done()
                    #    module.to_file()
                    if update:
                        jprint('Updates cache files')
                    checker.update(changed_files)
                    checker.to_file()
                    if (watch and
                        not first_cycle):
                        jprint('Watching for changes...')

                # If constantly watching
                if watch:
                    if first_cycle:
                        jprint('Watching for changes...')
                    first_cycle = False
                    update      = False
                    sleep(time)
                else:
                    break
        # If no error occured
        except KeyboardInterrupt:
            print()
        except Janitor.FinishedWithoutError:
            pass

        # Report to user
        return jprint('Finished')


#------------------------------------------------------------------------------#
if __name__ == '__main__':
    Janitor.from_cli(*argv[1:])
