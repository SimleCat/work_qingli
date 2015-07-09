#! /usr/bin/python
# -*- coding: utf-8

import myprint
from myprint import OverScolling

title_template = "Test PowerMeter: Device ID[%s], Time Interval[%s], Error[%d/%d]"

info_template = "value_left: %s, value_right: %s"

cup_scale = [-1, -2, -3, -6, -9, -12, -15, -18, -21, -24, -30, -40, -50, -60]


def printTitle(dev_id, time_interval, num_test_error, num_test_total):
	mode = 'bold'
	fore = 'white'
	back = 'green'
	title = title_template % (dev_id, time_interval, num_test_error, num_test_total)
	myprint.printHLine(1, 1, myprint.terminal_width, ' ', mode, fore, back)
	myprint.printString_Center(1, title, mode, fore, back)

def printCup(x, y, value):
	ch = ' '
	mode = ''
	fore = 'white'
	back = 'green'	
	hight = len(cup_scale)
	hight_have = None
	if value is None:
		value = cup_scale[-1]
	else:
		value = float(value)
	# value = -20.0
	for i in range(hight):
		myprint.printString(x, y+i, "%-d" % cup_scale[i])
		if hight_have is None and cup_scale[i] < value:
			hight_have = i
	myprint.printVLine(x+3, y, hight, ch, mode, fore, fore)
	if hight_have is not None:
		myprint.printVLine(x+3, y+hight_have, hight-hight_have, ch, mode, fore, back)


def printInfo(value_left, value_right):
	mode = ''
	fore = ''
	back = ''
	x = 1
	y = 3
	cup1_x = len("value_left: ")
	cup1_y = 5
	cup2_x = len("value_left: xxxx, value_right: ")
	cup2_y = 5

	myprint.printHLine(x, y, myprint.terminal_width, ' ', mode, fore, back)
	string = info_template % (str(value_left), str(value_right))
	myprint.printString(x, y, string, mode, fore, back)
	printCup(cup1_x, cup1_y, value_left)
	printCup(cup2_x, cup2_y, value_right)

scoll = None

def printOutput(string):
	global scoll
	mode = ''
	fore = ''
	back = ''
	x1 = 1
	y1 = len(cup_scale) + 6
	x2 = myprint.terminal_width
	y2 = myprint.terminal_hight
	if not scoll:
		scoll = OverScolling(x1, y1, x2, y2, mode, fore, back)
	scoll.addString(string)

def init(dev_id, time_interval):
	myprint.clearScreen()
	printTitle(dev_id, time_interval, 0, 0)
	printInfo(None, None)
	printOutput("Start Test!")	

if __name__ == '__main__':
	init("EP123456", "0.5s")
	print ''



