#! /usr/bin/python
# -*- coding: utf-8

import sys
import myprint
from myprint import OverScolling

title_temp = "Test Devices[%d/%d] Count[%d] Reboot[%d]"

info_template = "value_left: %s, value_right: %s            "

cup_scale_min = -96
cup_scale_max = 0
len_f_left_old = 0
len_f_right_old = 0


def printTitle(dev_num, dev_error_num, cnt, reboot):
	x = 1
	y = 1
	mode = 'bold'
	fore = 'white'
	back = 'green'
	title = title_temp % (dev_error_num, dev_num, cnt, reboot)
	myprint.printHLine(x, y, myprint.terminal_width, ' ', mode, fore, back, False)
	myprint.printString(x + 2, y, title, mode, fore, back)


def printInfo(devices_id, num, test_items, stat_dict):
	x = 1
	y = 3
	mode = 'bold'
	fore = 'white'
	back = 'blue'
	fore_error = 'red'
	dev_id = devices_id[num]
	dev_stat = stat_dict[dev_id]
	string = ''

	str_dev = dev_id
	total_error = dev_stat['Total']
	if total_error > 0:
		str_dev += '[%d]' % total_error
		str_dev = myprint.useStyle(str_dev, mode, fore_error, back)
	else:
		str_dev = myprint.useStyle(str_dev, mode, fore, back)
	string += str_dev + '\t'

	for item in test_items:
		str_tmp = item
		cnt_error = dev_stat[item]
		if cnt_error > 0:
			str_tmp += '[%d]' % cnt_error
			str_tmp	= myprint.useStyle(str_tmp, mode, fore_error, back)
		else:
			str_tmp = myprint.useStyle(str_tmp, mode, fore, back)
		string += str_tmp + '\t'

	myprint.printHLine(x, y+num, myprint.terminal_width, ' ', mode, fore, back, False)
	myprint.printString(x, y+num, string)
	myprint.moveCursor(0, myprint.terminal_hight)
	sys.stdout.flush()


def printInfo_plus(devices_id, num, test_items, stat_dict, stat_dict_old):
	x = 1
	y = 3
	y_cur = y
	mode = 'bold'
	fore = 'white'
	fore_title = fore
	fore_error = 'red'
	fore_select = fore
	back = 'blue'
	back_title = 'green'
	back_error = back
	back_select = 'yellow'

	title_devid = 'DeviceID'

	num_next = num + 1
	if num >= len(devices_id)-1:
		num_next = 0

	dev_id = devices_id[num]
	dev_stat = stat_dict[dev_id]

	len_max_devid = max(len(title_devid), len(dev_id)) + 2
	list_len_max = map(lambda x: len(x)+2, test_items)
	list_len_max = [len_max_devid] + list_len_max

	str_row = '+'
	for line in list_len_max:
		str_row += '-' * line + '+'
	str_row = myprint.useStyle(str_row, mode, fore_title, back_title)

	title_list = [title_devid] + test_items
	str_title = '|'
	for field, len_max in zip(title_list, list_len_max):
		field = ' ' + str(field) + ' '
		str_title += str(field).ljust(len_max) + '|'
	str_title = myprint.useStyle(str_title, mode, fore_title, back_title)

	myprint.printString(x, y_cur, str_row)
	y_cur += 1
	myprint.printString(x, y_cur, str_title)
	y_cur += 1
	myprint.printString(x, y_cur, str_row)
	y_cur += 1

	for index, dev_id in enumerate(devices_id):
		dev_stat = stat_dict[dev_id]
		line = ''
		str_node_out = ''
		fore_cur = fore
		back_cur = back
		if index == num_next:
			str_node_out = myprint.useStyle('|', mode, fore_select, back_select)
			# str_node = myprint.useStyle('|', mode, fore_select, back_select)
			fore_cur = fore_select
			back_cur = back_select
		else:
			str_node_out = myprint.useStyle('|', mode, fore_title, back_title)
		str_node = myprint.useStyle('|', mode, fore_cur, back_cur)
		line += str_node_out

		str_tmp = ' ' + str(dev_id) + ' '
		str_tmp = str_tmp.ljust(len_max_devid)
		if dev_stat['Total'] > 0:
			str_tmp = myprint.useStyle(str_tmp, mode, fore_error, back_cur)
		else:
			str_tmp = myprint.useStyle(str_tmp, mode, fore_cur, back_cur)
		line += str_tmp + str_node

		for i, item in enumerate(test_items):
			cnt_error = dev_stat[item]
			len_max = list_len_max[i+1]
			str_tmp = ' ' + str(cnt_error) + ' '
			str_tmp = str_tmp.ljust(len_max)
			if cnt_error == 0 or (stat_dict_old[dev_id][item] == cnt_error):
			# if cnt_error > 0:
				str_tmp = myprint.useStyle(str_tmp, mode, fore_cur, back_cur)
			else:
				str_tmp = myprint.useStyle(str_tmp, mode, fore_error, back_cur)
			line += str_tmp
			if i != len(test_items)-1:
				line += str_node
		line += str_node_out
		myprint.printString(x, y_cur, line)
		y_cur += 1

	myprint.printString(x, y_cur, str_row)
	myprint.moveCursor(0, myprint.terminal_hight)
	sys.stdout.flush()



scoll = None

def initOutput(y1, y2=None):
	global scoll
	mode = ''
	fore = ''
	back = ''
	x1 = 1
	# y1 = len(cup_scale) + 6
	x2 = myprint.terminal_width
	if not y2:
		y2 = myprint.terminal_hight
	elif y2 <= 0:
		y2 = myprint.terminal_hight + y2
	scoll = OverScolling(x1, y1, x2, y2, mode, fore, back)


def printOutput(string):
	global scoll
	scoll.addString(string)


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


def printPowerMater(value_left, value_right):
	global len_f_left_old
	global len_f_right_old
	mode = ''
	fore = ''
	back = ''
	x = 1
	y = myprint.terminal_hight - 2
	cup1_y = y + 1
	cup2_y = y + 2
	string = info_template % (str(value_left), str(value_right))
	myprint.printString(x, y, string, mode, fore, back, False)
	myprint.hideCursor()
	len_f_left_old = printCup(cup1_y, value_left, len_f_left_old)
	len_f_right_old = printCup(cup2_y, value_right, len_f_right_old)
	myprint.showCursor()
	# myprint.moveCursor(1, y-1)
	sys.stdout.flush()


def printPowerMater_init():
	global len_f_left_old
	global len_f_right_old
	len_f_left_old = 0
	len_f_right_old = 0
	mode = ''
	fore = ''
	back = ''
	fore_cup = 'white'
	back_cup = fore_cup
	x = 1
	y = myprint.terminal_hight - 2
	cup1_y = y + 1
	cup2_y = y + 2
	myprint.printHLine(x, y-1, myprint.terminal_width, ' ', mode, fore, back, False)
	myprint.printHLine(x, y, myprint.terminal_width, ' ', mode, fore, back, False)
	myprint.printHLine(x, cup1_y, myprint.terminal_width, ' ', mode, fore_cup, back_cup, False)
	myprint.printHLine(x, cup2_y, myprint.terminal_width, ' ', mode, fore_cup, back_cup)
	# printPowerMater(None, None)

def init(num_dev):
	myprint.clearScreen()
	printTitle(num_dev, 0, 0, 0)
	# printInfo(None, None, True)
	initOutput(num_dev + 8)


if __name__ == '__main__':
	init(10)
	printOutput("Start Test!")
	print ''