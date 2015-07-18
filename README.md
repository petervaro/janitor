
Dependencies
------------

Janitor by default uses [`pyhashxx`](https://github.com/ewencp/pyhashxx), which
is not part of python's standard library. However, this is an optional
dependency, as you can define wether janitor should use `MD5` or `SHA1` or not:

```
$ janitor -m
$ janitor -s
```

But if you want to use the default (and fastest) `xxHash` algroithm, you should
install it via the package installer:

```
$ sudo pip install pyhashxx
$ janitor
```


Use it through the command line
-------------------------------

First create a sample configuration file:

```
$ janitor -g
```

After a version-control synchronization, you should run update only:

```
$ janitor -u
```

To increase the version only (for example the `minor` sequence), you should use:

```
$ janitor -i=minor
```

For more details on arguments:

```
$ janitor -h
```


Use it through python
---------------------

You can use `janitor` via `python` not only through the its CLI. This can be
very useful, when working with a `python` based build system, for example:
[SCons](http://scons.org).

This example specifies the working path, uses the `MD5` for hashing and does't
increment the version sequences:

```python
from janitor import Janitor

Janitor(path    = '/tmp',
        md5     = True,
        exclude = {'versioner'})
```


The `JANITOR` configuration file
--------------------------------

The `JANITOR` file is a `json` file, where the root object has to be a type of
`Object`. There can be one *global* preference, called `exclude` and several
module preferences, like `versioner` or `prefixer`.

Everything has a default value, so you only have to specify, what you want to
overwrite. In some cases (mostly when a container is needed) the desired
behaviour should be extending the default values, not overwrite them. `JANITOR`
can handle these situations, by providing an `extend_default` key, in ever
`module` and the global preferences. For example, if you want to `exclude` the
files `"hello.x"` and `"world.y"` and you also want to exclude the files
excluded by default (`[".gitignore", ".DS_Store"]`), then you have to type in:

```json
{
    "exclude":
    {
        "names":
        [
            "hello.x",
            "world.y"
        ],
        "extend_default":
        [
            "names"
        ]
    }
}
```


Known issues
------------

Currently there is no support for Microsoft Windows and the future of the
support is unknown at this moment.
