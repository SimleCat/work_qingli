#! /usr/bin/python
# -*- coding: utf-8

import myprint
import sys
from myprint import OverScolling

title_template = "Scan Devices: Number[%d], Time Interval[%s], Count[%d]"

info_template = "%s: %s"


def printTitle(num, time_interval, cnt):
	mode = 'bold'
	fore = 'white'
	back = 'green'	
	title = title_template % (num, str(time_interval), cnt)
	myprint.printHLine(1, 1, myprint.terminal_width, ' ', mode, fore, back, False)
	myprint.printString_Center(1, title, mode, fore, back)


def printInfo(dev_id, dev_info, num, state):
	mode = 'bold'
	fore = 'black'
	fore_error = 'white'
	back = 'green'
	back_error = 'red'
	back_change = 'yellow'
	x = 1
	y = 3
	if state == 1:
		back = back_change
	elif state == -1:
		fore = fore_error
		back = back_error
	myprint.printHLine(x, y+num, myprint.terminal_width, ' ', mode, fore, back, False)
	string = info_template % (str(dev_id), str(dev_info))
	myprint.printString(x, y+num, string, mode, fore, back, False)
	myprint.moveCursor(0, myprint.terminal_hight)
	sys.stdout.flush()


scoll = None

def initOutput(y1):
	global scoll
	mode = ''
	fore = ''
	back = ''
	x1 = 1
	# y1 = len(cup_scale) + 6
	x2 = myprint.terminal_width
	y2 = myprint.terminal_hight
	scoll = OverScolling(x1, y1, x2, y2, mode, fore, back)

def printOutput(string):
	global scoll
	scoll.addString(string)

def init(num_dev, time_interval):
	myprint.clearScreen()
	printTitle(num_dev, time_interval, 0)
	# printInfo(None, None, True)
	initOutput(num_dev + 4)


if __name__ == '__main__':
	init(10, "0.5s")
	printOutput("Start Test!")
	print ''



