## INFO ##
## INFO ##

# Import python modules
from copy        import deepcopy
from collections import OrderedDict
from re          import compile, finditer, DOTALL, VERBOSE, MULTILINE

# Module level constants
REPR = '<{0.__class__.__module__}.{0.__class__.__name__}({1}) at {2}>'

# Helper functions
#------------------------------------------------------------------------------#
def replace(string, rules):
    for pattern, replacement in rules:
        string = string.replace(pattern, replacement)
    return string



#------------------------------------------------------------------------------#
class Data:

    _base_instance = NotImplemented

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, data=NotImplemented,
                       raw_data=NotImplemented,
                       **kwargs) -> 'Data':
        # If data is given as raw_data
        if raw_data is not NotImplemented:
            self.raw_data = raw_data
            self.parse()
        # If data is given as object
        else:
            if data is not NotImplemented:
                self.data = data
            else:
                self.data = kwargs.get('default', None)
            self.compose()
        # Set other attributes
        for attribute, value in kwargs.items():
            setattr(self, attribute, value)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __call__(self, *args, **kwargs) -> 'Data':
        # Create new instance referring to this instance as base-instance
        instance = self.__class__(*args, **kwargs)
        instance._base_instance = self
        return instance


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __repr__(self) -> str:
        return REPR.format(self,
                           ', '.join('{}={}'.format(*a) for a in self._attrs()),
                           hex(id(self)))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _attrs(self):
        yield from ((a, v) for a, v in self.__dict__.items()
                    if not callable(v) and not a.startswith('__'))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _parser(self, string) -> object:
        return string


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _composer(self, object) -> str:
        return repr(object)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def parse(self) -> 'Data':
        self.data = self._parser(self.raw_data)
        return self


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def compose(self) -> 'Data':
        self.raw_data = self._composer(self.data)
        return self



#------------------------------------------------------------------------------#
class Base(Data):

    BASE = NotImplemented

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _parser(self, string) -> object:
        return self.BASE(string)



#------------------------------------------------------------------------------#
class Int(Base):
    BASE = int



#------------------------------------------------------------------------------#
class Str(Base):
    BASE = str



#------------------------------------------------------------------------------#
class Bool(Data):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _parser(self, string) -> object:
        return bool(eval(string, {}, {}))



#------------------------------------------------------------------------------#
class Container(Data):

    BASE   = NotImplemented
    EXTEND = NotImplemented

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def extend(self) -> None:
        data = deepcopy(self.default)
        self.EXTEND(data, self.data)
        self.data = data


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _parser(self, string) -> str:
        string = string.strip()
        self.should_extend = False
        try:
            if self.extensible:
                if string[0] == '+':
                    self.should_extend = True
                    string = string[1:]
        except (AttributeError, IndexError) as e:
            print(e)
            pass
        return string


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def parse(self) -> 'Container':
        super().parse()
        if self.should_extend:
            self.extend()
        return self



#------------------------------------------------------------------------------#
class Sequence(Container):

    # Class level constants
    COMPOSE_REPLACE = [('\\', '\\\\'), (',', '\\,')]
    PARSE_REPLACE   = [('\\\\', '\\'), ('\\,', ',')]
    PARSE_PATTERN   = compile(r"""
        \s*
        (?P<item>(\\\\|\\,|.)+?)
        \s*
        (?:,|$)""", flags=DOTALL|VERBOSE|MULTILINE)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _parser(self, string) -> object:
        string = super()._parser(string)
        return self.BASE(replace(m.group('item'), Sequence.PARSE_REPLACE)
                         for m in finditer(Sequence.PARSE_PATTERN, string))



    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _composer(self, object) -> str:
        return ','.join(replace(str(value), Sequence.COMPOSE_REPLACE)
                        for value in object)



#------------------------------------------------------------------------------#
class Mapping(Container):

    # Class level constants
    COMPOSE_REPLACE = deepcopy(Sequence.COMPOSE_REPLACE) + [(':', '\\:')]
    PARSE_REPLACE   = deepcopy(Sequence.PARSE_REPLACE)   + [('\\:', ':')]
    PARSE_PATTERN   = compile(r"""
        \s*
        (?P<key>(\\\\|\\,|\\:|.)+?)
        \s*
        :
        \s*
        (?P<value>(\\\\|\\,|\\:|.)+?)
        \s*
        (?:,|$)""", flags=DOTALL|VERBOSE|MULTILINE)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _parser(self, string) -> object:
        string = super()._parser(string)
        return self.BASE((replace(m.group('key'), Mapping.PARSE_REPLACE),
                          replace(m.group('value'), Mapping.PARSE_REPLACE))
                         for m in finditer(Mapping.PARSE_PATTERN, string))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _composer(self, object) -> str:
        return ','.join(':'.join((replace(str(key), Mapping.COMPOSE_REPLACE),
                                  replace(str(value), Mapping.COMPOSE_REPLACE)))
                        for key, value in object.items())



#------------------------------------------------------------------------------#
class Set(Sequence):
    # Class level constants
    BASE   = set
    EXTEND = set.update



#------------------------------------------------------------------------------#
class List(Sequence):
    # Class level constants
    BASE   = list
    EXTEND = list.extend



#------------------------------------------------------------------------------#
class Dict(Mapping):
    # Class level constants
    BASE   = dict
    EXTEND = dict.update



#------------------------------------------------------------------------------#
class OrdDict(Mapping):
    # Class level constants
    BASE   = OrderedDict
    EXTEND = OrderedDict.update
