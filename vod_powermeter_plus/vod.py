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
# port_brocast_to = 6023
port_brocast_to = 6023
port_udp_to = 8801

device_id = 'EP163106'
# devices_id = ['epepepep']
device_ip = "192.168.1.104"
scan_info = False


buf_size = 1024
time_out = 3.0

cnt_test = 0
cnt_error = 0
time_interval = 0.04

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
	if not logger:
		logger = getLogger()
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



def testBase(socket_udp, addr, dev_type, dev_id, cmd, value=None):
	if value:
		send = cmdMix = '{"cmd":"%s","value":"%s","deviceID":"%s"}'%(cmd, value, dev_id)
	else:
		send = cmdMix = '{"cmd":"%s","deviceID":"%s"}'%(cmd, dev_id)
	outputInfo("Send [%s] to [%s]" % (send, str(addr)))
	try:
		socket_udp.sendto(send, addr)
	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		traceback.print_exc()

	try:
		socket_udp.settimeout(time_out)
		data, addr = socket_udp.recvfrom(buf_size)
		outputInfo("Receive [%s] from [%s]" % (data, addr))
	except socket.timeout:
		outputInfo('Error: Request timed out!')
		return None
	jsondata = json.loads(data)
	cmd = "res" + cmd[3:]
	# if jsondata['cmd'] != cmd \
	# 	# or jsondata['deviceType'] != dev_type \
	# 	or (value and jsondata['value'] != value):
	if jsondata['cmd'] != cmd \
		or (value and jsondata['value'] != value):
		print "Receive: cmd = %s, deviceType = %s" % (jsondata['cmd'], jsondata['cmd'])
		print "Error: cmd or deviceType don't match."
		return None
	return jsondata


def testMix(socket_udp, dev_info, cnt, dev_id):
	cmd = "reqMix"
	dev_type = 'reverb'
	value = "0.%d" % cnt
	print "[Test Mix]"
	return testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
		dev_id, cmd, value)


def testGain(socket_udp, dev_info, cnt, dev_id):
	cmd = "reqGain"
	dev_type = "judgement"
	value = "%d" % (i-5)
	outputInfo("[Test Gain]")
	return testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
		dev_id, cmd, value)

def testStatus(socket_udp, dev_info, dev_id):
	cmd = "reqStatus"
	dev_types = ["judgement", "reverb", "recorder"]
	ret = True
	for dev_type in dev_types:
		outputInfo("[Test Status]: Device(%s)." % dev_type )
		if not testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
			dev_id, cmd):
			ret = None
	return ret

def testPowerMeter(socket_udp, dev_info, dev_id):
	cmd = "reqPowerMeter"
	dev_type = "recorder"
	outputInfo("[Test PowerMeter]")
	ret = testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
			dev_id, cmd)
	# if ret:
		# print "value = %s" % ret
	return ret

dev_info = None
def testOneDevice(socket_broadcast, socket_udp, cnt, dev_id):
	global dev_info
	global device_ip
	global scan_info
	result = {}
	if not dev_info:
		dev_info = {}
		if scan_info:
			dev_info = getDeviceInfo(socket_broadcast, dev_id)
		else:
			dev_info["recorder"] = device_ip
	if not dev_info:
		return None
	result["dev_info"] = dev_info
	ret = testPowerMeter(socket_udp, dev_info, dev_id)
	result["res_powermater"] = ret
	return result

def testStart():
	global cnt_test
	global cnt_error
	global device_id

	socket_broadcast = getBroadcastSocket(host, portS)
	socket_udp = getUDPSocket(host, portC)
	dev_id = device_id
	value_left = None
	value_right = None
	while True:
		cnt_test += 1
		outputInfo ("[%02d] device ID : %s   %s"
		% (cnt_test, dev_id, time.strftime("%Y-%m-%d %H:%M:%S", \
			time.localtime())))
		result = testOneDevice(socket_broadcast, socket_udp, cnt_test, dev_id)
		dev_info = None
		if result:
			dev_info = result["dev_info"]
			value_left = result["res_powermater"]["value_left"]
			value_right = result["res_powermater"]["value_right"]
		else:
			cnt_error += 1
		printInerface.printTitle(cnt_test)
		printInerface.printInfo(value_left, value_right)

		time.sleep(time_interval)

def checkArg():
	import re
	import sys
	global device_id
	global device_ip
	global scan_info

	if len(sys.argv) == 1:
		print "Error: No argument."
		exit(1)
	elif len(sys.argv) == 2:
		device_id = sys.argv[1]
		scan_info = True
	else:
		device_id = sys.argv[1]
		device_ip = sys.argv[2]
		scan_info = False
	if re.match('^EP[\d]{6}$', device_id):
		return
	if re.match('^[\d]{6}$', device_id):
		device_id = 'EP' + device_id
	else:
		print "Error: device_id[%s] invalid." % device_id
		exit(1)


if __name__ == '__main__':
	global device_id
	global device_ip
	checkArg()
	printInerface.init(device_id, time_interval)
	testStart()
