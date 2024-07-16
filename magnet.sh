#!/bin/bash

#INSTALL xdotool: 
#ADD keyboard shortcuts


#1. get screen size
W=$(xwininfo -root | grep "Width" | awk -F: '{print $2}')
H=$(xwininfo -root | grep "Height" | awk -F: '{print $2}')

#compute new size and position
if [[ $1 == "f" ]]; then
	#full
	W2=$((W/1))
	H2=$((H/1))
	X2=0
	Y2=0
elif [[ $1 == "t" ]]; then
	#top
	W2=$W
	H2=$((H/2))
	X2=0
	Y2=0
elif [[ $1 == "b" ]]; then
	#bottom
	W2=$W
	H2=$((H/2))
	X2=0
	Y2=$((H/2))
elif [[ $1 == "l" ]]; then
	#left
	W2=$((W/2))
	H2=$H
	X2=0
	Y2=0
elif [[ $1 == "r" ]]; then
	#right
	W2=$((W/2))
	H2=$H
	X2=$((W/2))
	Y2=0
elif [[ $1 == "c" ]]; then
	#center
	W2=$((W/2))
	H2=$((H/2))
	X2=$((W/4))
	Y2=$((H/4))
elif [[ $1 == "tl" ]]; then
	#top-left
	W2=$((W/2))
	H2=$((H/2))
	X2=0
	Y2=0
elif [[ $1 == "tr" ]]; then
	#top right
	W2=$((W/2))
	H2=$((H/2))
	X2=$((W/2))
	Y2=0
elif [[ $1 == "bl" ]]; then
	#bottom left
	W2=$((W/2))
	H2=$((H/2))
	X2=0
	Y2=$((H/2))
elif [[ $1 == "br" ]]; then
	#bottom right
	W2=$((W/2))
	H2=$((H/2))
	X2=$((W/2))
	Y2=$((H/2))
elif [[ $1 == "13l" ]]; then
	#1/3 left
	W2=$((W/3))
	H2=$((H/1))
	X2=0
	Y2=0
elif [[ $1 == "13c" ]]; then
	#1/3 center
	W2=$((W/3))
	H2=$((H/1))
	X2=$((W/3))
	Y2=0
elif [[ $1 == "13r" ]]; then
	#1/3 right
	W2=$((W/3))
	H2=$((H/1))
	X2=$((W*2/3))
	Y2=0
elif [[ $1 == "23l" ]]; then
	#2/3 left
	W2=$((W*2/3))
	H2=$((H/1))
	X2=0
	Y2=0
elif [[ $1 == "23c" ]]; then
	#2/3 center
	W2=$((W*2/3))
	H2=$((H/1))
	X2=$((W*1/6))
	Y2=0
elif [[ $1 == "23r" ]]; then
	#2/3 right
	W2=$((W*2/3))
	H2=$((H/1))
	X2=$((W/3))
	Y2=0
fi

#removes window property that prevents xdotool works
wmctrl -r :ACTIVE: -b remove,maximized_vert,maximized_horz
wmctrl -r :ACTIVE: -b remove,above,below
wmctrl -r :ACTIVE: -b remove,fullscreen
#resize and move the window
xdotool getactivewindow windowsize $W2 $H2
xdotool getactivewindow windowmove $X2 $Y2
