## INFO ##
## INFO ##

# Import python modules
from os.path import (join,
                     isfile)
from pickle  import (dump,
                     load,
                     HIGHEST_PROTOCOL)


#------------------------------------------------------------------------------#
class Checker:

    BLOCK_SIZE = 2**16
    CACHE_FILE = 'checksum'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, cache_dir,
                       curr_hash_id,
                       hasher):
        # Store static values
        self._hash_id   = curr_hash_id
        self._hasher    = hasher
        self._cache_dir = cache_dir
        self._cache     = cache = {}

        # If a cache file already exists
        try:
            with open(join(cache_dir, Checker.CACHE_FILE), mode='rb') as cache_file:
                prev_hash_id, cache_data = load(cache_file)
                if prev_hash_id != curr_hash_id:
                    return
                for file, check_sum in cache_data.items():
                    # If file still exists
                    if isfile(file):
                        cache[file] = check_sum
        # IF this is the first time Checker is running
        except (FileNotFoundError, EOFError):
            pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def hash(self, file):
        check_sum  = self._hasher()
        block_size = Checker.BLOCK_SIZE
        with open(file, 'rb') as data:
            buffer = data.read(block_size)
            while buffer:
                check_sum.update(buffer)
                buffer = data.read(block_size)
        return check_sum.digest()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def update(self, files):
        hash  = self.hash
        cache = self._cache
        for file in files:
            cache[file] = hash(file)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def rebuild(self):
        self._cache = {}


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def is_changed(self, file):
        # Return wether check_sum differs or not
        return not self._cache.get(file, -1.0) == self.hash(file)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def to_file(self):
        # Serialize cache and save it to the cache dir
        with open(join(self._cache_dir, Checker.CACHE_FILE), mode='wb') as cache_file:
            dump((self._hash_id, self._cache), cache_file, HIGHEST_PROTOCOL)
