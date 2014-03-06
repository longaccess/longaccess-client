#!/bin/sh -e

if [ "$#" -gt 0 ] ; then
    PYINST=$1
else
    PYINST=$(which pyinstaller) || { 
        echo "pyinstaller not found. Try: ./generate.sh <path to pyinstaller>"
        exit 1
    }
fi

if ! test -x "$PYINST" ; then
    echo "$PYINST is not executable!"
    exit 1
fi

if which lacli >/dev/null 2>&1 ; then
    # reinstall as .egg
    pip uninstall -y lacli
fi

pip install --egg ..

BINARY=$(which lacli)
ARCH=`uname -s`-`uname -m`

$PYINST lacli.spec

# don't include files with 444 mode
chmod -R u+r ./dist

VERSION=`$BINARY --version | cut -d " " -f 2`
TARBALL="lacli-$ARCH-$VERSION.tar.bz2"
LATEST="lacli-$ARCH-latest.tar.bz2"

tar cjvf $TARBALL -C ./dist/ lacli

if [ -x upload.sh ] ; then
    ./upload.sh install.sh
    ./upload.sh $TARBALL $LATEST
fi
