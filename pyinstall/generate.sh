#!/bin/sh -e


if [ "$#" -gt 0 ] ; then
    PYINST=$1
else
    PYINST=$(which pyinstaller)
fi

if test -z "$PYINST"; then
	echo "./generate.sh <path to pyinstaller>"
	exit 1
fi

BINARY=`which lacli`

if [ -x $BINARY ] ; then
    # reinstall as .egg to make sure
    pip uninstall -y lacli
    pip install --egg ..
fi

ARCH=`uname -s`-`uname -p`

$PYINST lacli.spec

if [ $? != 0 ] ; then
	exit $?
fi

VERSION=`$BINARY --version | cut -d " " -f 2`
TARBALL="lacli-$ARCH-$VERSION.tar.bz2"

tar cjvf $TARBALL -C ./dist/ lacli

echo "#! /bin/sh" > install.sh
echo "VERSION=\"$VERSION\"" >> install.sh
cat install.template.sh >> install.sh

[ -x upload.sh ] && ./upload.sh install.sh $TARBALL
