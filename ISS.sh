#!/bin/sh
if [ ! -f /home/pi/Code/ISSInUse.txt ]; then
	touch /home/pi/Code/ISSInUse.txt
	python3 /home/pi/Code/ISS.py
	rm -r /home/pi/Code/ISSInUse.txt
fi
