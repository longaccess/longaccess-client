#! /bin/bash

if [ "$1" == "" ]; then
	echo "./generate.sh <path to pyinstaller>"
	exit 1
fi

PYINST=$1
BINARY=`which lacli`
ARCH=`uname`

$PYINST $BINARY

if [ $? != 0 ] ; then
	exit $?
fi

VERSION=`$BINARY --version | cut -d " " -f 2`
TARBALL="lacli-$ARCH-$VERSION.tar.bz2"

tar cjvf $TARBALL -C ./dist/ lacli

echo "#! /bin/sh" > install.sh
echo "VERSION=\"$VERSION\"" >> install.sh
cat install.template.sh >> install.sh

# s3cmd put -P install.sh $TARBALL s3://download.longaccess.com/
