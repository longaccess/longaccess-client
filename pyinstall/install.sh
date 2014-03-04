#!/bin/sh -e

trap cleanup 1 2 3 6 EXIT

cleanup () {
    ret=$?
    if [ -n "$STACK" ] ; then
        printf "cleaning up..\n"
        IFS=":"
        for item in $STACK ; do
            rm -r "$item"
        done
    fi
    exit $ret
}

_mkdir () {
    printf "Creating $1: "
    if [ ! -d "$1" ] ; then
        mkdir "$1"
        STACK="$1:$STACK"
        printf "done\n\n"
    else
        printf "exists\n\n"
    fi
}

_separator () {
    printf "\n========================================\n\n"
}

_download () {
    TARGET=$2
    URL=http://download.longaccess.com/lacli-$1-latest.tar.bz2
    
    _mkdir $TARGET/lacli || { printf "$TARGET/lacli already exists!\n" ; exit 1; }
    
    printf "Downloading lacli (the Longaccess command line client) "

    _failed () {
        printf "\n"
        printf "****************************************\n"
        printf "ERROR:\n"
        printf "    Unable to $1 http://download.longaccess.com/lacli-$ARCH-latest.tar.bz2\n"
        printf "    It is possible that your architecture is not supported by this installer.\n"
        printf "    You can always install from source: https://github.com/longaccess/longaccess-client\n"
        printf "    Please contact team@longaccess.com or open an issue at https://github.com/longaccess/longaccess-client.\n"
        printf "****************************************\n"
    }

    curl -LIfs "$URL" >/dev/null || { _failed "download" ; exit 1; }
    printf "and extracting to $TARGET/lacli\n"
    curl -L -s "$URL" | tar xjf - -C "$TARGET" lacli || { _failed "extract" ; exit 1; }
}

_install () {
    _separator
    printf "Creating symlink $1 -> $BIN/lacli\n"
    ln -s $1 $BIN/lacli
    _separator
    if [ "$SHELL" = "/bin/bash" ]; then
      printf "Adding $BIN to .bashrc\n"
      printf "# Added by Longaccess (lacli)\n" >> ~/.bashrc
      printf "export PATH=$BIN:$PATH\n" >> ~/.bashrc
    elif [ "$SHELL" = "/bin/zsh" ]; then
      printf "Adding $BIN to .zshrc\n"
      printf "# Added by Longaccess (lacli)\n" >> ~/.zshrc
      printf "export PATH=$BIN:$PATH\n" >> ~/.zshrc
    else
      printf "Make sure you add $BIN to your PATH.\n"
    fi
    _separator
}

_finish () {
    STACK=''
    printf "\nDone.\n" 
    printf "\nStart a *new* shell and type \"lacli --help\" for options.\n"
}

main () {
    PREFIX="$HOME/local"
    TARGET="$PREFIX/lib"
    BIN="$PREFIX/bin"
    ARCH=`uname -s`-`uname -m`

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
