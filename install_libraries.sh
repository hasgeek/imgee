#!/bin/bash
if [ $(uname) == "Linux" ]
then
    sudo apt-get install libjpeg-dev libpng-dev libfreetype6-dev liblcms1-dev libtiff4-dev ghostscript
    sudo apt-get install imagemagick
elif [ $(uname) == "Darwin" ]
then
    which brew > /dev/null
    if [ $? -eq 0 ]
    then
        brew install libjpeg libpng freetype lcms2 libtiff ghostscript librsvg
        brew install imagemagick --with-libtiff --enable-hdri --with-gslib
    else
        echo "Homebrew is not installed. Please install it. Check http://brew.sh for more."
        open http://brew.sh
    fi
fi
