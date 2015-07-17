#!/usr/bin/env python
# this is the udp broadcast server
import socket, traceback
import json
import time
import logging
# import telnet
import printInerface

host = '' # Bind to all interfaces
portS = 6030
portC = 6031
port_brocast_to = 6023
port_udp_to = 8801

devices_id = ['EP331058']
file_deviceid = r'device_id.txt'
device_types = ["judgement", "reverb", "recorder"]



buf_size = 1024
time_out = 1.0

cnt_test = 0
cnt_error = 0
time_interval = 0.5

#logger param
# LOG_FILE = 'log_%s.txt' % time.strftime("%Y%m%d-%H%M", time.localtime())
LOG_FILE = 'log.txt'
fmt = '[%(asctime)s] %(message)s'

logger = None

def getLogger():
	logger = logging.getLogger()
	handler = logging.FileHandler(LOG_FILE)
	formatter = logging.Formatter(fmt)

	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.setLevel(logging.NOTSET)
	return logger

def outputInfo(string):
	global logger
	# print string
	# if not logger:
		# logger = getLogger()
	# logger.info(string)
	printInerface.printOutput(string)

def getBroadcastSocket(host, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.bind((host, port))
	return s

def getUDPSocket(host, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((host, port))
	return s

def getDeviceInfo(socket_broadcast, dev_id):
	try:
		cmdSendScan = '{"cmd":"reqinfo","deviceID":"%s"}' % (dev_id)
		outputInfo("Broadcast: [%s] port[%s]" % (cmdSendScan, port_brocast_to))
		socket_broadcast.sendto(cmdSendScan,('<broadcast>', port_brocast_to))
	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		traceback.print_exc()

	devInfo = {}
	for i in range(3):
		outputInfo("getDeviceInfo: %d" % (i+1))
		data = ''
		try:
			socket_broadcast.settimeout(time_out)
			data, addr = socket_broadcast.recvfrom(buf_size)
			outputInfo("Receive [%s] from [%s]" % (repr(data), addr))
		except socket.timeout:
			outputInfo('Error: Request timed out!')
			return devInfo
		jsondata = json.loads(data)	
		if jsondata['cmd'] == "resinfo" :
			devType = jsondata['deviceType']
			outputInfo("devType: %s" % devType)
			if devInfo.has_key(devType) == True:
				outputInfo( "Error: Have the same device type!")
				return None
			else :
				devInfo[devType] = jsondata['ip']
	outputInfo("Recieve IP address: %s" % json.dumps(devInfo))
	return devInfo

def loadDeviceID(file_deviceid):
	import re
	f = open(file_deviceid, 'r')
	lines = f.readlines()
	if not lines:
		print('Error: "%s" is empty.' % file_deviceid)
		return None
	res = []
	pattern = re.compile(r'^EP[\d]{6}$')
	for i, line in enumerate(lines):
		line = line.strip()
		if not line:
			continue
		if pattern.match(line):
			if line in res:
				print('Warning: "%s" repeated [lineno: %d].' % (line, i+1))
			else:
				res.append(line)
		else:
			print('Warning: "%s" invalid [lineno: %d].' % (line, i+1))
	return res

def verifyDeviceInfo(dev_info, dev_info_old):
	if not dev_info:
		return -1
	for dev_type in device_types:
		if not dev_info.has_key(dev_type):
			return -1
	for dev_type in device_types:
		if dev_info_old and dev_info_old.has_key(dev_type):
			if cmp(dev_info[dev_type], dev_info_old[dev_type]) != 0:
				return 1
		else:
			return 1
	return 0

def devinfoToStr(dev_info):
	if not dev_info:
		return "None"
	res = "{"
	for index, dev_type in enumerate(device_types):
		res += "%s: %13s" % (dev_type, dev_info.get(dev_type, "None"))
		if index != len(device_types)-1:
			res += ", "
	res += "}"
	return res

def scan():
	devs_id = loadDeviceID(file_deviceid)
	if not devs_id:
		outputInfo("Error: No device id.")
		return None
	printInerface.init(len(devs_id), time_interval)
	printInerface.printOutput("Start Test!")
	# return 
	socket_broadcast = getBroadcastSocket(host, portS)
	# socket_udp = getUDPSocket(host, portC)
	cnt_test = 0
	dict_devinfo = {}
	for dev_id in devs_id:
		dict_devinfo[dev_id] = None

	while True:
		cnt_test += 1
		printInerface.printTitle(len(devs_id), time_interval, cnt_test)
		for index, dev_id in enumerate(devs_id):
			outputInfo ("[%02d] device ID : %s   %s"
			% (cnt_test, dev_id, time.strftime("%Y-%m-%d %H:%M:%S", \
				time.localtime())))
			dev_info = getDeviceInfo(socket_broadcast, dev_id)
			state = verifyDeviceInfo(dev_info, dict_devinfo[dev_id])
			printInerface.printInfo(dev_id, devinfoToStr(dev_info), index, state)
			dict_devinfo[dev_id] = dev_info
			time.sleep(0.01)

		time.sleep(time_interval)


if __name__ == '__main__':
	scan()
	# printInerface.init(devices_id[0], time_interval)
	# testStart();
