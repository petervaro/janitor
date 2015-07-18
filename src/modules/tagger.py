## INFO ##
## INFO ##

# Import python modules
from collections import OrderedDict

# Import janitor module
from orderedset  import OrderedSet



#------------------------------------------------------------------------------#
class Tagger:

    # Class level constants
    WORDS = OrderedSet(('fixme', 'todo', 'bug', 'hack', 'note', 'xxx'))
    MARKS = OrderedDict([('!!!', 'alert'), ('???', 'question')])
