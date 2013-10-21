
TARGET="$HOME/local/lib"
BIN="$HOME/local/bin"
ARCH=`uname`

echo "========================================"
echo "Creating $TARGET"
mkdir -p $TARGET 
echo "Creating $BIN"
mkdir -p $BIN 
echo "========================================"
echo
echo "Downloading lacli (the Longaccess command line client)"
echo "from URL and extracting to $TARGET"
curl -s http://download.longaccess.com/lacli-$ARCH-$VERSION.tar.bz2 | tar xjvf - -C $TARGET 
if [ $? != 0 ] ; then
    echo "****************************************"
    echo "ERROR:"
    echo "    Unable to download or extract http://download.longaccess.com/lacli-$ARCH-$VERSION.tar.bz2"
    echo "    It is possible that your architecture is not supported by this installer."
    echo "    You can always install from source: https://github.com/longaccess/longaccess-client"
    echo "    Please contact team@longaccess.com or open an issue at https://github.com/longaccess/longaccess-client."
    echo "****************************************"
    exit 1
fi
echo
echo "========================================"
echo "Creating symlink $TARGET/lacli/lacli -> $BIN/lacli"
ln -s $TARGET/lacli/lacli $BIN/lacli
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
echo
echo "Done."
echo
echo "Start a *new* shell and type \"lacli --help\" for options."
echo 
