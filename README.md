The Longaccess client
======================

This is the prototype client program for interacting with the [Longaccess service][la]. It is usable via the command line on systems that have [Python][py] installed but also requires a registered account. If you are unfamiliar with other aspects of the Longaccess service a good place to start is "[What is Longaccess?][]"

Installation
------------

We have binary packages for certain platforms, like MacOS X, Linux and FreeBSD. For more information see the [Longaccess downloads page][lad]. For other platforms or purposes you can download or clone the source repository, create a [`virtualenv`][ve] if needed, and install the client via `pip`. E.g.:

    pip install https://github.com/longaccess/longaccess-client/tarball/master

Usage
-----

After installation the program is invoked as `lacli`. Run it with no arguments to see a synopsis of supported usages. In short, there are three basic commands:

* `lacli archive` helps you manage archives
* `lacli certificate` helps you manage certificates
* `lacli capsules` let's you view your available capsules 

Alternatively one may run the program interactively by running `lacli -i`.

The `lacli` command supports certain global options which you can see in the aforementioned synopsis. The only required argument however is the authentication parameters which we discuss in the next section.

Authentication
--------------

In order to use the service you must first have a username and password for the service. You can provide them to the program in two ways:

1. as global arguments, e.g. `lacli -u user -p pass archive list ...`
2. as entries in your `.netrc` file. This way you will not have to provide them everytime (but you should keep your `.netrc` safe)

Example usage
-------------

An example scenario:


    $ lacli archive list
    No available archives.
    $ lacli archive create /home/kouk/toread -t documents
    Encrypting..
    archive prepared
    $ lacli archive list
    001  36MiB             documents      LOCAL           
    $ lacli archive upload 1
    /home/kouk/.longaccess/data/2013-10-18-documents.zip.crypt : |###################| ETA:  0:00:00 349.66 MB/s
    Upload finished, waiting for verification
    Press Ctrl-C to check manually later
    status: completed
    Certificate 68-H1BK saved.
    Use lacli certificate list to see your certificates, or lacli certificate --help for more options
    done.
    $ lacli archive list
    001  36MiB             documents   COMPLETE    68-H1BK
    $ lacli certificate list
       68-H1BK  36MiB documents
    $ lacli certificate export 68-H1BK
    Created files:
    longaccess-68-H1BK.html
    longaccess-68-H1BK.yaml
    $


[la]: https://www.longaccess.com "the Longaccess website"
[lad]: https://downloads.longaccess.com "the Longaccess downloads page"
[py]: http://www.python.org "the python website"
[ve]: http://www.virtualenv.org "virtualenv"
[What is Longaccess?]: https://github.com/longaccess/longaccess-docs/blob/master/what_is_longaccess.md "what is Longaccess?"
