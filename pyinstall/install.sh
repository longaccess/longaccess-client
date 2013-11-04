#!/bin/sh -e

trap cleanup 1 2 3 6 EXIT

cleanup () {
    ret=$?
    if [ -n "$STACK" ] ; then
        echo "cleaning up.."
        IFS=":"
        for item in $STACK ; do
            rm -r "$item"
        done
    fi
    exit $ret
}

_mkdir () {
    echo -n "Creating $1: "
    if [ ! -d "$1" ] ; then
        mkdir "$1"
        STACK="$1:$STACK"
        echo "done"
    else
        echo "exists"
    fi
    echo
}

_separator () {
    echo "========================================"
    echo
}

_download () {
    TARGET=$2
    URL=http://download.longaccess.com/lacli-$1-latest.tar.bz2
    
    _mkdir $TARGET/lacli || { echo "$TARGET/lacli already exists!" ; exit 1; }
    
    echo -n "Downloading lacli (the Longaccess command line client) "

    _failed () {
        echo
        echo "****************************************"
        echo "ERROR:"
        echo "    Unable to $1 http://download.longaccess.com/lacli-$ARCH-latest.tar.bz2"
        echo "    It is possible that your architecture is not supported by this installer."
        echo "    You can always install from source: https://github.com/longaccess/longaccess-client"
        echo "    Please contact team@longaccess.com or open an issue at https://github.com/longaccess/longaccess-client."
        echo "****************************************"
    }

    curl -LIfs "$URL" >/dev/null || { _failed "download" ; exit 1; }
    echo "and extracting to $TARGET/lacli"
    curl -L -s "$URL" | tar xjf - -C "$TARGET" lacli || { _failed "extract" ; exit 1; }
}

_install () {
    echo "========================================"
    echo "Creating symlink $1 -> $BIN/lacli"
    ln -s $1 $BIN/lacli
    echo
    echo "========================================"
    if [ "$SHELL" = "/bin/bash" ]; then
      echo "Adding $BIN to .bashrc"
      echo "# Added by Longaccess (lacli)" >> ~/.bashrc
      echo "export PATH=$BIN:$PATH" >> ~/.bashrc
    elif [ "$SHELL" = "/bin/zsh" ]; then
      echo "Adding $BIN to .zshrc"
      echo "# Added by Longaccess (lacli)" >> ~/.zshrc
      echo "export PATH=$BIN:$PATH" >> ~/.zshrc
    else
      echo "Make sure you add $BIN to your PATH."
    fi
    echo "========================================"
}

_finish () {
    STACK=''
    echo
    echo "Done."
    echo
    echo "Start a *new* shell and type \"lacli --help\" for options."
    echo 
}

main () {
    PREFIX="$HOME/local"
    TARGET="$PREFIX/lib"
    BIN="$PREFIX/bin"
    ARCH=`uname -s`-`uname -p`

    _separator
    _mkdir $PREFIX
    _mkdir $TARGET
    _mkdir $BIN
    _separator
    _download $ARCH $TARGET
    _separator
    _install $TARGET/lacli/lacli $BIN
    _finish

}

main
