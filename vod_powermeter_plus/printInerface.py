#! /usr/bin/python
# -*- coding: utf-8

import myprint
import sys
from myprint import OverScolling


title_template = "Test PowerMeter: Device ID[%s], Time Interval[%s], Count[%d]"
title_template_ = "Test PowerMeter: Device ID[%s], Time Interval[%s], Count"

info_template = "value_left: %s, value_right: %s            "

cup_scale_min = -100
cup_scale_max = 0
len_f_left_old = 0
len_f_right_old = 0

len_title = 0

def initTitle(dev_id, time_interval, num_test):
	global len_title
	mode = 'bold'
	fore = 'white'
	back = 'green'
	title = title_template_ % (dev_id, time_interval)
	len_title = len(title)
	title = title_template % (dev_id, time_interval, num_test)
	myprint.printHLine(1, 1, myprint.terminal_width, ' ', mode, fore, back)
	myprint.printString(1, 1, title, mode, fore, back)


def printTitle(num_test):
	mode = 'bold'
	fore = 'white'
	back = 'green'
	s = "[%d]" % num_test
	myprint.printString(len_title+1, 1, s, mode, fore, back)

def printScale(y):
	len_old = -2
	for i in range(cup_scale_min, cup_scale_max+1):
		len_f = float((i - cup_scale_min)) / (cup_scale_max - cup_scale_min) * myprint.terminal_width
		len_f = int(len_f)
		if len_f == 0:
			len_f = 1
		if len_f-len_old > 1:
			myprint.printString(len_f, y+1, str(i)[-1])
			if len(str(i)) > 2:
				myprint.printString(len_f, y, str(i)[-2])
			len_old = len_f

def printCup(y, value, len_f_old, init=False):
	ch = ' '
	mode = ''
	fore = 'white'
	back = 'green'	
	len_f = 0

	if init:
		myprint.printHLine(1, y, myprint.terminal_width, ch, mode, fore, fore, False)

	hight_have = None
	if value is None:
		len_f = 0
	else:
		value = float(value)
		if value <= cup_scale_min:
			len_f = 0
		elif value >= cup_scale_max:
			len_f = myprint.terminal_width
		else:
			len_f = float((value - cup_scale_min)) / (cup_scale_max - cup_scale_min) * myprint.terminal_width
			len_f = int(len_f)
	if len_f > len_f_old:
		myprint.printHLine(len_f_old+1, y, len_f-len_f_old, ch, mode, fore, back, False)
	elif len_f < len_f_old:
		myprint.printHLine(len_f+1, y, len_f_old-len_f, ch, mode, fore, fore, False)
	return len_f


def printInfo(value_left, value_right, show_other=False):
	global len_f_left_old
	global len_f_right_old
	mode = ''
	fore = ''
	back = ''
	x = 1
	y = myprint.terminal_hight - 6
	cup1_y = myprint.terminal_hight - 1
	cup2_y = myprint.terminal_hight
	string = info_template % (str(value_left), str(value_right))
	myprint.printString(x, y, string, mode, fore, back, False)
	if show_other:
		printScale(cup1_y-2)
	len_f_left_old = printCup(cup1_y, value_left, len_f_left_old, show_other)
	len_f_right_old = printCup(cup2_y, value_right, len_f_right_old, show_other)
	myprint.moveCursor(1, 4)
	sys.stdout.flush()


scoll = None

def printOutput(string):
	global scoll
	mode = ''
	fore = ''
	back = ''
	x1 = 1
	y1 = 3
	x2 = myprint.terminal_width
	y2 = myprint.terminal_hight - 10
	if not scoll:
		scoll = OverScolling(x1, y1, x2, y2, mode, fore, back)
	scoll.addString(string)

def init(dev_id, time_interval):
	myprint.clearScreen()
	initTitle(dev_id, time_interval, 0)
	printInfo(None, None, True)
	printOutput("Start Test!")

if __name__ == '__main__':
	init("EP123456", "0.5s")
	printInfo(-40, -40)
	print ''



