#! /bin/bash

if [ "$1" == "" ]; then
	echo "./generate.sh <path to pyinstaller>"
	exit 1
fi

PYINST=$1
BINARY=`which lacli`

$PYINST $BINARY

if [ $? != 0 ] ; then
	exit $?
fi

VERSION=`$BINARY --version | cut -d " " -f 2`

tar cjvf lacli-$VERSION.tar.bz2 -C ./dist/ lacli
