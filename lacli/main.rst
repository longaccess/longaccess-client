Doctest for main
================

>>> from lacli.main import settings

Invalid debug value
-------------------

>>> settings({'--home': '/tmp', '--debug': 'foo'})
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "lacli/main.py", line 51, in settings
    debug = int(options.get('--debug', 0))
ValueError: invalid literal for int() with base 10: 'foo'

Setting verify to false
-----------------------

>>> import os
>>> os.environ['LA_API_VERIFY'] = '0'
>>> prefs, cache = settings({'--home': '/tmp'})
>>> prefs['api']['verify']
False

Batch operation
---------------

without batch operation:

>>> prefs, cache = settings({'--home': '/tmp'})
>>> prefs['command']['batch']

with batch operation:

>>> import os
>>> os.environ['LA_BATCH_OPERATION'] = '1'
>>> prefs, cache = settings({'--home': '/tmp'})
>>> prefs['command']['batch']
True
>>> prefs, cache = settings({'--home': '/tmp/foo/bar'})
>>> os.path.exists('/tmp/foo/bar')
True

Command args
------------

>>> prefs, cache = settings({'--home': '/tmp',
...     '<command>': 'foo', '<args>': 1})
>>> prefs['foo']
1

