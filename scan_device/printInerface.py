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


def printDevInfo(dict_dev):
	if not dict_dev:
		return
	mode = 'bold'
	fore = 'black'
	fore_error = 'white'
	back = 'green'
	back_default = 'green'
	back_error = 'red'
	back_change = 'yellow'
	x = 1
	y = 3

	for k in dict_dev:
		string, index, state = dict_dev[k]
		if state == 1:
			back = back_change
		elif state == -1:
			back = back_error
			fore = fore_error
		else:
			back = back_default
		string  = info_template % (k, string)
		myprint.printHLine(x, y+index, myprint.terminal_width, ' ', mode, fore, back, False)
		myprint.printString(x, y+index, string, mode, fore, back, False)
	sys.stdout.flush()

def printUnknowIP(unknow_ip, len_dev):
	mode = 'bold'
	fore = 'white'
	back = 'blue'
	x = 1
	y = len_dev + 3
	for index, info in enumerate(unknow_ip):
		string = "%s : %s" % info
		myprint.printHLine(x, y+index, myprint.terminal_width, ' ', mode, fore, back, False)
		myprint.printString(x, y+index, string, mode, fore, back, False)
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

def init(num_dev, num_uip, time_interval, cnt_test, change=True):
	if change:
		myprint.clearScreen()
	printTitle(num_dev, time_interval, cnt_test)
	# printInfo(None, None, True)
	if change:
		initOutput(num_dev + num_uip + 4)


if __name__ == '__main__':
	init(10, "0.5s")
	printOutput("Start Test!")
	print ''



