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

devices_id = []
device_types = ["judgement", "reverb", "recorder"]



buf_size = 1024
time_out = 0.5

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

def scan(socket_broadcast, cnt_test):
	cmd_scan = '{"cmd":"scanDev", "deviceID":"epepepep"}'
	outputInfo("Broadcast: [%s] port[%s] cnt[%d]." % (cmd_scan, port_brocast_to, cnt_test))
	socket_broadcast.sendto(cmd_scan,('<broadcast>', port_brocast_to))
	dict_ip = {}
	list_id = []
	while True:
		socket_broadcast.settimeout(time_out)
		try:
			data, addr = socket_broadcast.recvfrom(buf_size)
			outputInfo("Receive [%s] from [%s]" % (repr(data), addr))
		except socket.timeout:
			outputInfo('Error: Request timed out!')
			break
		jsondata = json.loads(data)
		dict_ip[jsondata['ip']] = jsondata['deviceType']
		if jsondata.has_key('deviceID'):
			list_id.append(jsondata['deviceID'])
	list_id = list(set(list_id))
	list_id.sort()
	return list_id, dict_ip


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
	list_ip = []
	for i in range(3):
		outputInfo("getDeviceInfo: %d" % (i+1))
		data = ''
		try:
			socket_broadcast.settimeout(time_out)
			data, addr = socket_broadcast.recvfrom(buf_size)
			outputInfo("Receive [%s] from [%s]" % (repr(data), addr))
		except socket.timeout:
			outputInfo('Error: Request timed out!')
			return devInfo, list_ip
		jsondata = json.loads(data)	
		if jsondata['cmd'] == "resinfo" :
			devType = jsondata['deviceType']
			outputInfo("devType: %s" % devType)
			if devInfo.has_key(devType):
				outputInfo( "Error: Have the same device type!")
				return None, None
			else :
				devInfo[devType] = jsondata['ip']
				list_ip.append(jsondata['ip'])
	outputInfo("Recieve IP address: %s" % json.dumps(devInfo))
	return devInfo, list_ip

def verifyDeviceInfo(dev_info, dev_id, list_id):
	if not dev_info:
		return -1
	for dev_type in device_types:
		if not dev_info.has_key(dev_type):
			return -1
	if dev_id not in list_id:
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

def getUnknowIP(know_ip, dict_ip):
	unknow_ip = []
	for ip in dict_ip:
		if ip not in know_ip:
			unknow_ip.append((ip, dict_ip[ip]))
	return unknow_ip

def start():
	cnt_test = 0
	socket_broadcast = getBroadcastSocket(host, portS)
	list_id_old = []
	unknow_ip_old = []
	printInerface.init(0, 0, time_interval, 0)
	while True:
		cnt_test += 1
		list_id, dict_ip = scan(socket_broadcast, cnt_test)
		dict_dev = {}
		know_ip = []
		for index, dev_id in enumerate(list_id):
			outputInfo ("[%02d] device ID : %s   %s"
			% (cnt_test, dev_id, time.strftime("%Y-%m-%d %H:%M:%S", \
				time.localtime())))
			dev_info, list_ip = getDeviceInfo(socket_broadcast, dev_id)
			know_ip += list_ip
			state = verifyDeviceInfo(dev_info, dev_id, list_id_old)
			dict_dev[dev_id] = (devinfoToStr(dev_info), index, state)
			# printInerface.printInfo(dev_id, devinfoToStr(dev_info), index, state)
			time.sleep(0.01)
		
		unknow_ip = getUnknowIP(know_ip, dict_ip)
		if len(list_id)+len(unknow_ip) != len(list_id_old)+len(unknow_ip_old):
			printInerface.init(len(list_id), len(unknow_ip), time_interval, cnt_test)
		else:
			printInerface.init(len(list_id), len(unknow_ip), time_interval, cnt_test, False)
		printInerface.printDevInfo(dict_dev)
		printInerface.printUnknowIP(unknow_ip, len(list_id))
		list_id_old = list_id
		unknow_ip_old = unknow_ip




if __name__ == '__main__':
	start()
	# printInerface.init(devices_id[0], time_interval)
	# testStart();
