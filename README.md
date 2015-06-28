
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

Basically `JANITOR` is just a "fancy" `INI` file, with some special features
and syntax aditions. For example some values require sequences (sets or lists),
while some requires mapping types. `JANITOR` uses a simplified syntax similar
to the `python` syntax of these types.

There is the sequence type:

```
key_string = value, 1, True, 123.456
```

And there is the mapping type:

```
key_sting = alpha: 0, beta: 1, gamma: 2, delta: 3
```

Because these literals are using special characters (like: '`,`' or '`:`') the
syntax also provides escape sequences of these characters. For example this:

```
key_string = hello\, world, hey\, there!
```

is equal to:

```
["hello, world", "hey, there!"]
```

Or this:

```
key_string = your name\: Clara: yes, your name\: Donna: no
```

is equal to this:

```
{"your name: Clara": "yes", "your name: Donna": "no"}
```

And the syntax also supports the escaping from the escape character as well:

```
key_string = escape: \\, comma: \,
```

is equal to:

```
{"escape": "\\", "comma": ","}
```

Some of these containers holds predefined values, which are correct, but we need
to extend those values with additional ones. `JANITOR`'s syntax also provides a
sugar for that, the first non-whitespace character has to be a `+`. For example,
if the default values of '`world`' are '`hello`' and '`good bye`', using this:

```
world = + hi, bye
```

is equal to:

```
["hello", "good bye", "hi", "bye"]
```


Known issues
------------

Microsoft Windows is not supported at the moment.
