#!/bin/bash
if [ $(uname) == "Linux" ]
then
    sudo apt-get install libjpeg-dev libpng-dev libfreetype6-dev liblcms1-dev libtiff4-dev librsvg2-dev ghostscript
    sudo apt-get install imagemagick
    sudo sed -i.bak "s/\&quot;gs\&quot;/\&quot;gs\&quot; -dUseCIEColor/g" $(convert -list delegate | grep Path | sed -e "s/Path: //g")
    sudo sed -r -i.bak "s/(-dUseCIEColor )+/-dUseCIEColor /g" $(convert -list delegate | grep Path | sed -e "s/Path: //g")
elif [ $(uname) == "Darwin" ]
then
    which brew > /dev/null
    if [ $? -eq 0 ]
    then
        brew install libjpeg libpng freetype lcms2 libtiff ghostscript librsvg gnu-sed
        brew install imagemagick --with-libtiff --enable-hdri --with-gslib
        gsed -r -i.bak "s/\&quot;gs\&quot;/\&quot;gs\&quot; -dUseCIEColor/g" $(convert -list delegate | grep Path | sed -e "s/Path: //g")
        gsed -r -i.bak "s/(-dUseCIEColor )+/-dUseCIEColor /g" $(convert -list delegate | grep Path | sed -e "s/Path: //g")
    else
        echo "Homebrew is not installed. Please install it. Check http://brew.sh for more."
        open http://brew.sh
    fi
fi
