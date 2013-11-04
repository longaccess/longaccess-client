Doctest for with_api_response 
=============================

Mock function
-------------

In these examples we will use a mock function:

>>> from mock import Mock
>>> orig = Mock(__name__='orig')
>>> orig.return_value.json.return_value=None

The function returns an object that mocks an API response. It has a "json" method that returns None for now. Next we wrap our mock function and run it succesfully (no output):

>>> from lacli.decorators import *
>>> f = with_api_response(orig)
>>> f(None)

Next we will provide a "raise_for_status" method to the mock response, which raises an Exception:

>>> rfs = orig.return_value.raise_for_status
>>> rfs.side_effect = Exception()
>>> f(None)
Traceback (most recent call last):
  File "/usr/local/lib/python2.7/doctest.py", line 1289, in __run
    compileflags, 1) in test.globs
  File "<doctest lacli.decorators.with_api_response[6]>", line 1, in <module>  # NOQA
    f(None)
  File "/home/kouk/code/longaccess-cli/lacli/decorators.py", line 52, in wrap  # NOQA
    raise ApiErrorException(e)
ApiErrorException: the server couldn't fulfill your request

If the exception is HTTP related:

>>> rsp = Mock()
>>> rfs.side_effect = HTTPError(response=rsp)
>>> f(None)
Traceback (most recent call last):
  File "/usr/local/lib/python2.7/doctest.py", line 1289, in __run
    compileflags, 1) in test.globs
  File "<doctest lacli.decorators.with_api_response[10]>", line 1, in <module> # NOQA
    f(None)
  File "/home/kouk/code/longaccess-cli/lacli/decorators.py", line 56, in wrap  # NOQA
    raise ApiErrorException(e)
ApiErrorException: the server couldn't fulfill your request

If the exception is HTTP 404:

>>> rsp.status_code = 404
>>> rfs.side_effect = HTTPError(response=rsp)
>>> f(None)
Traceback (most recent call last):
  File "/usr/local/lib/python2.7/doctest.py", line 1289, in __run
    compileflags, 1) in test.globs
  File "<doctest lacli.decorators.with_api_response[10]>", line 1, in <module> # NOQA
    f(None)
  File "/home/kouk/code/longaccess-cli/lacli/decorators.py", line 56, in wrap  # NOQA
    raise ApiUnavailableException(e)
ApiUnavailableException: resource not found

If the exception is HTTP 401:

>>> rsp.status_code = 401
>>> rfs.side_effect = HTTPError(response=rsp)
>>> f(None)
Traceback (most recent call last):
  File "/usr/local/lib/python2.7/doctest.py", line 1289, in __run
    compileflags, 1) in test.globs
  File "<doctest lacli.decorators.with_api_response[10]>", line 1, in <module> # NOQA
    f(None)
  File "/home/kouk/code/longaccess-cli/lacli/decorators.py", line 56, in wrap  # NOQA
    raise ApiAuthException(e)
ApiAuthException: authentication failed

If there were no credentials provided to the API class:

>>> rfs.side_effect = ApiNoSessionError()
>>> f(None)
Traceback (most recent call last):
  File "/usr/local/lib/python2.7/doctest.py", line 1289, in __run
    compileflags, 1) in test.globs
  File "<doctest lacli.decorators.with_api_response[6]>", line 1, in <module>  # NOQA
    f(None)
  File "/home/kouk/code/longaccess-cli/lacli/decorators.py", line 52, in wrap  # NOQA
    raise effect
ApiNoSessionError: no session credentials provided.

If the connection could not be opened:

>>> rfs.side_effect = ConnectionError()
>>> f(None)
Traceback (most recent call last):
  File "/usr/local/lib/python2.7/doctest.py", line 1289, in __run
    compileflags, 1) in test.globs
  File "<doctest lacli.decorators.with_api_response[6]>", line 1, in <module>  # NOQA
    f(None)
  File "/home/kouk/code/longaccess-cli/lacli/decorators.py", line 52, in wrap  # NOQA
    raise ApiUnavailableException(e)
ApiUnavailableException: resource not found
