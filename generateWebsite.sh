#!/bin/sh

if [ "$1" = "regen" ]; then
	rm static/img/selection/pic*jpg
fi
cd photography
python genPhotoPage.py $1 
cd ..
hugo
