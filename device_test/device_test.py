#!/usr/bin/env python
# this is the udp broadcast server
import sys
import socket, traceback
import json
import time
import logging
import mytelnet
import interface
# import printInerface

host = '' # Bind to all interfaces
portS = 6030
portC = 6031
port_brocast_to = 6023
port_udp_to = 8801

# device_id = 'EP163106'
# devices_id = ['epepepep']
devices_id = []
file_deviceid = r'device_id.txt'
device_types = ["judgement", "reverb", "recorder"]

buf_size = 1024
time_out = 1.0

num_test_pre_reboot = 10
cnt_test = 0
cnt_error = 0
time_interval = 0.5
num_pm_test = 100
time_pm_interval = 0.05
stat_dict = {}
test_items = ['Total', 'ScanIP', 'Mixture', 'Status', 'Gain', 'PowerMeter', 'ReverbSW']

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
	if not logger:
		logger = getLogger()
	logger.info(string)
	interface.printOutput(string)


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


def verifyDeviceInfo(dev_info):
	if not dev_info:
		return False
	for dev_type in device_types:
		if not dev_info.has_key(dev_type):
			return False
	return True


def testBase(socket_udp, addr, dev_type, dev_id, cmd, value=None, channel=None, status=None):
	if status:
		send = cmdMix = '{"cmd":"%s","status":"%s","deviceID":"%s"}'%(cmd, status, dev_id)
	elif channel:
		send = cmdMix = '{"cmd":"%s", "channel":"%s","value":"%s","deviceID":"%s"}'%(cmd, channel, value, dev_id)
	elif value:
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
	if jsondata['cmd'] != cmd \
		or jsondata['deviceType'] != dev_type:
		outputInfo("Error: cmd or deviceType don't match")
		return None
	return jsondata


def testMixture(socket_udp, dev_info, value, dev_id):
	cmd = "reqMix"
	dev_type = 'reverb'
	value = "0.%d" % (value+1)
	outputInfo("*** Test Mixture")
	if not dev_info or not dev_info.has_key(dev_type):
		return False
	data = testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
		dev_id, cmd, value)
	if not data or not data.has_key('value'):
		return False
	if data['value'] != value:
		outputInfo("Error: value don't match")
		return False
	return True


def testStatus(socket_udp, dev_info, dev_id):
	cmd = "reqStatus"
	ret = True
	for dev_type in device_types:
		outputInfo("*** Test Status: %s" % dev_type)
		if not dev_info or not dev_info.has_key(dev_type):
			return False
		data = testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
			dev_id, cmd)
		if not data or not data.has_key('status') or data['status'] != 'nomal':
			ret = False
			outputInfo("Error: near status")
	return ret


def testGain(socket_udp, dev_info, value, dev_id):
	cmd = "reqGain"
	dev_type = "judgement"
	channels = ["left", "right"]
	value = "%d" % (value - (num_test_pre_reboot / 2))
	outputInfo("*** Test Gain")
	if not dev_info or not dev_info.has_key(dev_type):
		return False
	for channel in channels:
		data = testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
			dev_id, cmd, value, channel)
		if not data or not data.has_key('value') or data['value'] != value:
			outputInfo("Error: near gain")
			return False
	return True


def testPowerMeter(socket_udp, dev_info, dev_id):
	cmd = "reqPowerMeter"
	dev_type = "recorder"
	outputInfo("*** Test PowerMeter")
	if not dev_info or not dev_info.has_key(dev_type):
		return False

	interface.initOutput(len(devices_id)+8, -4)
	interface.printPowerMater_init()
	# exit(1)
	cnt_error = 0
	value_left_bak = '0'
	value_right_bak = '0'
	for i in range(num_pm_test):
		data = testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
				dev_id, cmd)
		if not data or not data.has_key('value_left') or not data.has_key('value_right'):
			outputInfo("Error: near power meter")
			cnt_error += 1
			continue
		if data['value_left'] == "-inf" or data['value_right'] == "-inf":
			cnt_error += 1
			continue
		# value_left = float(data['value_left'])
		# value_right = float(data['value_right'])
		value_left = data['value_left']
		value_right = data['value_right']
		if value_left == value_left_bak or value_right == value_left_bak:
			cnt_error += 1
		value_left_bak = value_left
		value_right_bak = value_right
		# if int(value_left) == 0 or int(value_right) == 0:
		# 	outputInfo("Error: near power meter")
		# 	return False
		interface.printPowerMater(value_left, value_right)
		# exit(1)
		time.sleep(time_pm_interval)
	interface.initOutput(len(devices_id)+8)
	if cnt_error > (num_pm_test / 2):
		return False
	return True


def testReverbSW(socket_udp, dev_info, dev_id):
	cmd = "reqReverbSW"
	dev_type = "reverb"
	status_list = ["on", "off"]
	outputInfo("*** Test ReverbSW")
	if not dev_info or not dev_info.has_key(dev_type):
		return False
	for status in status_list:
		data = testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
			dev_id, cmd, status=status)
		if not data or not data.has_key('status') or data['status'] != status:
			outputInfo("Error: near ReverbSW")
			return False
		time.sleep(time_interval)
	return True


def testOneDevice(socket_broadcast, socket_udp, cnt, dev_id):
	res = True

	dev_info = getDeviceInfo(socket_broadcast, dev_id)
	if not verifyDeviceInfo(dev_info):
		# stat_dict[dev_id]['Total'] += 1
		stat_dict[dev_id]['ScanIP'] += 1
		# return False
		res = False

	if not testMixture(socket_udp, dev_info, cnt, dev_id):
		res = False
		stat_dict[dev_id]['Mixture'] += 1

	if not testStatus(socket_udp, dev_info, dev_id):
		res = False
		stat_dict[dev_id]['Status'] += 1

	if not testGain(socket_udp, dev_info, cnt, dev_id):
		res = False
		stat_dict[dev_id]['Gain'] += 1

	if not testPowerMeter(socket_udp, dev_info, dev_id):
		res = False
		stat_dict[dev_id]['PowerMeter'] += 1

	if not testReverbSW(socket_udp, dev_info, dev_id):
		res = False
		stat_dict[dev_id]['ReverbSW'] += 1

	if not res:
		stat_dict[dev_id]['Total'] += 1

	return res




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


def initStatDict():
	global stat_dict
	for dev_id in devices_id:
		stat = {}
		# stat['Total'] = 0
		for item in test_items:
			stat[item] = 0
		stat_dict[dev_id] = stat


def checkArgv():
	import re
	dev_id = ''
	if len(sys.argv) == 2:
		dev_id = sys.argv[1]
	else:
		print 'Error: too many parameters'
		exit(1)
	if re.match('^EP[\d]{6}$', dev_id):
		return dev_id
	if re.match('^[\d]{6}$', dev_id):
		dev_id = 'EP' + dev_id
		return dev_id
	else:
		print "Error: device_id[%s] invalid." % dev_id
		exit(1)



def main():
	global devices_id
	if (len(sys.argv) != 1):
		dev_id = checkArgv()
		devices_id.append(dev_id)
	else:
		devices_id = loadDeviceID(file_deviceid)
	initStatDict()

	socket_broadcast = getBroadcastSocket(host, portS)
	socket_udp = getUDPSocket(host, portC)
	cnt_reboot = 0
	dev_error = []
	cnt_test = 0

	interface.init(len(devices_id))
	interface.printTitle(len(devices_id), len(dev_error), cnt_test, cnt_reboot)
	interface.printInfo_plus(devices_id, -1, test_items, stat_dict)
	outputInfo("*** Start Test")
	# exit(0)
	while True:
		for i in range(num_test_pre_reboot):
			cnt_test += 1
			for index, dev_id in enumerate(devices_id):
				ret = testOneDevice(socket_broadcast, socket_udp, i, dev_id)
				if not ret and dev_id not in dev_error:
					dev_error.append(dev_id)
				interface.printTitle(len(devices_id), len(dev_error), cnt_test, cnt_reboot)
				interface.printInfo_plus(devices_id, index, test_items, stat_dict)
				time.sleep(time_interval)
		# mytelnet.reboot(dev_info)
		time.sleep(20)
		cnt_reboot += 1


if __name__ == '__main__':
	main()