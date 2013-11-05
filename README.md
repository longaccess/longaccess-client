The Longaccess client
======================

This is the prototype client program for interacting with the [Longaccess service][la]. It is usable via the command line on systems that have [Python][py] installed but also requires a registered account. If you are unfamiliar with other aspects of the Longaccess service a good place to start is "[What is Longaccess?][]"

Installation
------------

We have binary packages for certain platforms, like MacOS X, Windows 8 64-bit, Linux and FreeBSD. For more information see the [Longaccess downloads page][lad]. For other platforms or purposes you can download or clone the source repository, create a [virtualenv][ve] if needed, and install the client via `pip`. E.g.:

    pip install https://github.com/longaccess/longaccess-client/tarball/master

Dependencies
------------

The prebuilt binary packages are self-contained, i.e. they do not have any hard external dependencies. There is however a soft dependency on an external tool to securely delete files from the filesystem, see below for more information. When installing from source most dependencies are automatically installable via `pip`. On some platforms the installation might require manually installing development packages, e.g. on [Fedora Linux][] you might need to install the `python2-devel` package. Additionally if graphical user interface dialogs are desired [PySide][] must be available.

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


Secure removal
--------------

When removing archives and certificates from the disk the program supports [secure deletion][sd] through an external program. In case a suitable removal program cannot be found<sup>*</sup> the client will complain and give further instructions. Currently we automatically support the following tools, if they are available on the system path:

* [srm][] (Mac, Unix)
* [shred][] (Unix)
* [sdelete][] (Windows, proprietary)
* [Eraser][] (Windows, open-source)

_* or one has not been provided via the optional argument to the `delete` command._

[la]: https://www.longaccess.com "the Longaccess website"
[lad]: https://downloads.longaccess.com "the Longaccess downloads page"
[py]: http://www.python.org "the python website"
[ve]: http://www.virtualenv.org "virtualenv"
[What is Longaccess?]: https://github.com/longaccess/longaccess-docs/blob/master/what_is_longaccess.md "what is Longaccess?"
[sd]: https://ssd.eff.org/tech/deletion "Secure deletion - EFF"
[srm]: http://en.wikipedia.org/wiki/Srm_(Unix) "SRM (Unix) - Wikipedia"
[shred]: http://en.wikipedia.org/wiki/Shred_(Unix) "Shred (Unix) - Wikipedia"
[sdelete]: http://technet.microsoft.com/en-us/sysinternals/bb897443.aspx "SDelete - Windows sysinternals"
[Eraser]: http://eraser.heidi.ie/ "Eraser"
[Fedora]: http://fedoraproject.org "Fedora"
[PySide]: http://pyside.org "PySide is a Python binding of the cross-platform GUI toolkit Qt." 
