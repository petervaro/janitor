## INFO ##
## INFO ##

# Import python modules
from collections import OrderedDict

#------------------------------------------------------------------------------#
# HACK: at some point implement a real OrderedSet
class OrderedSet(OrderedDict):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, iterable=()):
        super().__init__()
        self.update(iterable)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __repr__(self):
        return 'OrderedSet({!r})'.format(list(self.keys()))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def add(self, key):
        self[key] = None


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def update(self, iterable):
        super().update(OrderedDict.fromkeys(iterable))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def intersection(self, other, *others):
        section = self&other
        for other in others:
            section &= other
        return section


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __and__(self, other):
        return set(self.keys())&other


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __rand__(self, other):
        return other&set(self.keys())
