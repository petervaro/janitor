## INFO ##
## INFO ##

# Import python modules
from collections import OrderedDict

#------------------------------------------------------------------------------#
class Tagger:

    # Class level constants
    WORDS = ['fixme', 'todo', 'bug', 'hack', 'note', 'xxx']
    MARKS = OrderedDict([('!!!', 'alert'), ('???', 'question')])
