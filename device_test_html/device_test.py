#!/usr/bin/env python
# this is the udp broadcast server
# _*_ coding:utf-8 _*_
import sys
import socket, traceback
import json
import time
import logging
import threading
import my_websocket


host = '' # Bind to all interfaces
# portS = 6030
# portC = 6031
portS = 7050
portC = 8050
port_brocast_to = 6023
port_udp_to = 8801

# device_id = 'EP163106'
# devices_id = ['epepepep']
device_types = ["judgement", "reverb", "recorder"]

buf_size = 1024
time_out = 1

time_interval = 0.1
num_pm_test = 50
time_pm_interval = 0.05
stat_dict = {}
test_items = ['Total', 'ScanIP', 'Mixture', 'Status', 'Gain', 'PowerMeter', 'ReverbSW']

threads_num = 10

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
	# 	logger = getLogger()
	# logger.info(string)

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


class MyThread_Test(threading.Thread):
	def __init__(self, conn, socket_broadcast, socket_udp, devices_id, index, name=''):
		threading.Thread.__init__(self)
		self.name = name
		self.conn = conn
		self.socket_broadcast = socket_broadcast
		self.socket_udp = socket_udp
		self.devices_id = devices_id
		self.index = index
		self.ifdo = True

	def run(self):
		if self.index != None:
			dev_id = self.devices_id[0]
			try:
				self.testOneDevice(self.socket_broadcast, self.socket_udp, self.index, dev_id, self.conn)
			except socket.error:
				return
			return

		for index, dev_id in enumerate(self.devices_id):
			try:
				self.testOneDevice(self.socket_broadcast, self.socket_udp, index, dev_id, self.conn)
			except socket.error:
				break


	def stop(self):
		self.ifdo = False


	def testBase(self, socket_udp, addr, dev_type, dev_id, cmd, value=None, channel=None, status=None, wait=False):
		if not self.ifdo:
			exit(1)
		if wait:
			time.sleep(time_interval)

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


	def testMixture(self, socket_udp, dev_info, value, dev_id):
		cmd = "reqMix"
		dev_type = 'reverb'
		# value = "0.%d" % (value+1)
		value = '0.5'
		outputInfo("*** Test Mixture")
		if not dev_info or not dev_info.has_key(dev_type):
			return False
		data = self.testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
			dev_id, cmd, value, wait=True)
		if not data or not data.has_key('value'):
			return False
		if data['value'] != value:
			outputInfo("Error: value don't match")
			return False
		return True


	def testStatus(self, socket_udp, dev_info, dev_id):
		cmd = "reqStatus"
		ret = True
		for dev_type in device_types:
			outputInfo("*** Test Status: %s" % dev_type)
			if not dev_info or not dev_info.has_key(dev_type):
				return False
			data = self.testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
				dev_id, cmd, wait=True)
			if not data or not data.has_key('status') or data['status'] != 'nomal':
				ret = False
				outputInfo("Error: near status")
		return ret


	def testGain(self, socket_udp, dev_info, value, dev_id):
		cmd = "reqGain"
		dev_type = "judgement"
		channels = ["left", "right"]
		# value = "%d" % value
		value = '0'
		outputInfo("*** Test Gain")
		if not dev_info or not dev_info.has_key(dev_type):
			return False
		for channel in channels:
			data = self.testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
				dev_id, cmd, value, channel, wait=True)
			if not data or not data.has_key('value') or data['value'] != value:
				outputInfo("Error: near gain")
				return False
		return True


	def testPowerMeter(self, socket_udp, dev_info, dev_id, dev_index, conn):
		cmd = "reqPowerMeter"
		dev_type = "recorder"
		outputInfo("*** Test PowerMeter")
		if not dev_info or not dev_info.has_key(dev_type):
			return False

		cnt_error = 0
		value_left_bak = '0'
		value_right_bak = '0'
		stat = {"dev_id":dev_id, "dev_index":dev_index, "item": 'pm_data', "result": None}
		for i in range(num_pm_test):
			data = self.testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
					dev_id, cmd)
			if not data or not data.has_key('value_left') or not data.has_key('value_right'):
				outputInfo("Error: near power meter")
				# cnt_error += 1
				# continue
				cnt_error = num_pm_test
				break
			if data['value_left'] == "-inf" or data['value_right'] == "-inf":
				cnt_error += 1
				continue

			value_left = data['value_left']
			value_right = data['value_right']
			if value_left == value_left_bak or value_right == value_left_bak:
				cnt_error += 1
			value_left_bak = value_left
			value_right_bak = value_right

			stat['result'] = (value_left, value_right)
			my_websocket.send_data(conn, json.dumps(stat))

			time.sleep(time_pm_interval)

		if cnt_error > (num_pm_test / 2):
			return False
		return True


	def testReverbSW(self, socket_udp, dev_info, dev_id):
		cmd = "reqReverbSW"
		dev_type = "reverb"
		status_list = ["off", "on"]
		outputInfo("*** Test ReverbSW")
		if not dev_info or not dev_info.has_key(dev_type):
			return False
		for status in status_list:
			data = self.testBase(socket_udp, (dev_info[dev_type], port_udp_to), dev_type, \
				dev_id, cmd, status=status, wait=True)
			if not data or not data.has_key('status') or data['status'] != status:
				outputInfo("Error: near ReverbSW")
				return False
		return True


	def testOneDevice(self, socket_broadcast, socket_udp, dev_index, dev_id, conn):
		res = True
		stat = {"dev_id":dev_id, "dev_index":dev_index, "item": '', "result": 'T'}

		stat['item'] = 'flag'
		stat['result'] = 'start'
		my_websocket.send_data(conn, json.dumps(stat))

		dev_info = getDeviceInfo(socket_broadcast, dev_id)
		if not verifyDeviceInfo(dev_info):
			res = False
			stat['result'] = 'F'
		else:
			stat['result'] = 'T'
		stat['item'] = 'ScanIP'
		my_websocket.send_data(conn, json.dumps(stat))

		if not self.testMixture(socket_udp, dev_info, dev_index, dev_id):
			res = False
			stat['result'] = 'F'
		else:
			stat['result'] = 'T'
		stat['item'] = 'Mixture'
		my_websocket.send_data(conn, json.dumps(stat))

		if not self.testStatus(socket_udp, dev_info, dev_id):
			res = False
			stat['result'] = 'F'
		else:
			stat['result'] = 'T'
		stat['item'] = 'Status'
		my_websocket.send_data(conn, json.dumps(stat))

		if not self.testGain(socket_udp, dev_info, dev_index, dev_id):
			res = False
			stat['result'] = 'F'
		else:
			stat['result'] = 'T'
		stat['item'] = 'Gain'
		my_websocket.send_data(conn, json.dumps(stat))

		if not self.testPowerMeter(socket_udp, dev_info, dev_id, dev_index, conn):
			res = False
			stat['result'] = 'F'
		else:
			stat['result'] = 'T'
		stat['item'] = 'PowerMeter'
		my_websocket.send_data(conn, json.dumps(stat))

		if not self.testReverbSW(socket_udp, dev_info, dev_id):
			res = False
			stat['result'] = 'F'
		else:
			stat['result'] = 'T'
		stat['item'] = 'ReverbSW'
		my_websocket.send_data(conn, json.dumps(stat))

		if not res:
				stat['result'] = 'F'
		else:
			stat['result'] = 'T'
		stat['item'] = 'Total'
		my_websocket.send_data(conn, json.dumps(stat))

		return res


def initStatDict(dev_id):
	global stat_dict

	stat_dict['device_id'] = dev_id
	stat = {}
	for item in test_items:
		stat[item] = 'T'
	stat_dict['result'] = stat
	stat_dict['data'] = {'pm_left': [], 'pm_right': []}
	stat_dict['ret'] = 'success'


def checkArgv():
	import re
	dev_id = ''
	if len(sys.argv) == 1:
		print 'Error: no parameter'
		exit(1)
	elif len(sys.argv) == 2:
		dev_id = sys.argv[1].upper()
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


def getDevicesID(raw):
	import re
	raw = raw.upper()
	tmp_list = raw.split(',')
	id_list = []
	for dev_id in tmp_list:
		dev_id = dev_id.strip()
		if not dev_id:
			continue
		if re.match('^EP[\d]{6}$', dev_id):
			id_list.append(dev_id)
		elif re.match('^[\d]{6}$', dev_id):
			id_list.append('EP' + dev_id)
		else:
			id_list.append(dev_id)
	return id_list


def thread_func(port_brocast, port_udp, conn):
	print 'exec thread_func'
	print 'port_brocast: %d, port_udp: %d' % (port_brocast, port_udp)
	socket_broadcast = getBroadcastSocket(host, port_brocast)
	socket_udp = getUDPSocket(host, port_udp)

	devices_id_bak = None
	thread = None

	while True:
		print 'Start recv dev_id'
		recv_data = my_websocket.recv_data(conn)
		if not recv_data or recv_data == '\x03\xe9':
			break
		devices_id = getDevicesID(recv_data)
		outputInfo("Devices list: %s" % str(devices_id))
		index = None
		if not devices_id:
			continue
		elif len(devices_id) == 1:
			dev_id = devices_id[0]
			index = 0
			if devices_id_bak and len(devices_id_bak) > 1:
				for i, line in enumerate(devices_id_bak):
					if line == dev_id:
						index = i
						break
		else:
			devices_id_bak = devices_id

		if thread and thread.isAlive():
			thread.stop()
			thread.join()
		thread = MyThread_Test(conn = conn,
							socket_broadcast = socket_broadcast,
							socket_udp = socket_udp,
							devices_id = devices_id,
							index = index)
		thread.start()

	if thread and thread.isAlive():
		thread.stop()
		thread.join()

	conn.close()
	socket_udp.close()
	socket_broadcast.close()


def thread_func_test(socket_broadcast, socket_udp, conn, devices_id, index):
	if index != None:
		dev_id = devices_id[0]
		try:
			testOneDevice(socket_broadcast, socket_udp, index, dev_id, conn)
		except socket.error:
			return
		return

	for index, dev_id in enumerate(devices_id):
		try:
			testOneDevice(socket_broadcast, socket_udp, index, dev_id, conn)
		except socket.error:
			break


def getFreeThreads(threads):
	for i in range(len(threads)):
		if threads[i] == None or not threads[i].isAlive():
			return i
	return None


def startTest(threads, conn):
	thr_index = getFreeThreads(threads)
	if thr_index == None:
		msg = {'item': 'waiting', 'result': 'The connection has reached its limit'}
		print msg
		my_websocket.send_data(conn, json.dumps(msg))
		conn.close()
		return
	threads[thr_index] = threading.Thread(target = thread_func,
									args = (portS+thr_index, portC+thr_index, conn))
	print '[%d] thread can use, start' % thr_index
	threads[thr_index].start()




def main():

	threads = [None] * threads_num


	web_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		web_sock.bind((my_websocket.HOST, my_websocket.PORT))
		web_sock.listen(threads_num)
		print "Bind %s, ready to use" % my_websocket.PORT
	except:
		print("Port[%d] wes used, quit" % my_websocket.PORT)
		sys.exit(1)

	while True:
		print "waiting accept..."
		conn, addr = web_sock.accept()
		print "Got connection from ", addr
		if my_websocket.handshake(conn):
			print "handshake success"
		else:
			print "handshake failue"
			conn.close()
		startTest(threads, conn)


if __name__ == '__main__':
	main()