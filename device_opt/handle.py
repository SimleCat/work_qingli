#!/usr/bin/env python
# this is the udp broadcast server
import re
import sys
import copy
import socket, traceback
import json
import time
from output import openOutput
from output import closeOutput
from output import outputInfo
import mytelnet

host = '' # Bind to all interfaces
port_brocast = 6030
port_udp = 6031
port_brocast_to = 6023
port_udp_to = 8801

device_types = ["judgement", "reverb", "recorder"]

buf_size = 1024
time_out = 1


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


def getDeviceInfo(socket_broadcast, dev_id, allow_repeat=False):
	try:
		cmdSendScan = '{"cmd":"reqinfo","deviceID":"%s"}' % (dev_id)
		outputInfo("Broadcast: [%s] port[%s]" % (cmdSendScan, port_brocast_to))
		socket_broadcast.sendto(cmdSendScan,('<broadcast>', port_brocast_to))
	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		traceback.print_exc()

	devInfo = {}
	for i in range(len(device_types)):
		outputInfo("getDeviceInfo: %d" % (i+1))
		data = ''
		try:
			socket_broadcast.settimeout(time_out)
			data, addr = socket_broadcast.recvfrom(buf_size)
			outputInfo("Receive [%s] from [%s]" % (repr(data), addr))
		except socket.timeout:
			outputInfo('Error: Request timed out!', 'error')
			return devInfo
		jsondata = json.loads(data)
		if jsondata['cmd'] == "resinfo" :
			devType = jsondata['deviceType']
			outputInfo("devType: %s" % devType)
			if devInfo.has_key(devType):
				outputInfo( "Error: Have the same device type!", 'error')
				if not allow_repeat:
					return None
				devInfo[devType+'repeat'] = jsondata['ip']
			else :
				devInfo[devType] = jsondata['ip']
	outputInfo("Recieve IP address: %s" % json.dumps(devInfo))
	return devInfo




def scanIP(dev_id):
	outputInfo("*** Scan IP")
	socket_broadcast = getBroadcastSocket(host, port_brocast)
	dev_info = getDeviceInfo(socket_broadcast, dev_id, allow_repeat=True)
	info = copy.deepcopy(dev_info)

	status = True

	string = "%s: " % dev_id
	if not info:
		string += 'None'
		status = False
	else:
		string += '{'
		# keys = info.keys()
		for dev_type in device_types:
			string += '%s: ' % dev_type
			if not info.has_key(dev_type):
				string += '%s, ' % 'None'
				status = False
			else:
				dev_ip = info.pop(dev_type)
				string += '%s, ' % dev_ip
		for eachKey in info:
			string += '%s: %s, ' % (eachKey, info[eachKey])
		string = string[:-2]
		string += '}'
	# outputInfo('=' * len(string))
	if status:
		outputInfo(string, 'info')
	else:
		outputInfo(string, 'info_error')
	# outputInfo('=' * len(string))

	socket_broadcast.close()

	return dev_info


def optBase(addr, dev_type, dev_id, cmd, value=None, channel=None, status=None):
	if not addr[0]:
		closeOutput()
		dev_info = scanIP(dev_id)
		openOutput()
		if not dev_info or not dev_info.has_key(dev_type):
			outputInfo("Error: cannot found ip of %s" % dev_type, 'error')
			return None
		addr = (dev_info[dev_type], addr[1])

	socket_udp = getUDPSocket(host, port_udp)

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
		outputInfo('Error: Request timed out!', 'error')
		socket_udp.close()
		return None

	jsondata = json.loads(data)
	cmd = "res" + cmd[3:]
	if jsondata['cmd'] != cmd \
		or jsondata['deviceType'] != dev_type:
		outputInfo("Error: cmd or deviceType don't match", 'error')
		socket_udp.close()
		return None
	socket_udp.close()
	return jsondata


def setMixture(dev_id, value, reverb_ip=None):
	cmd = "reqMix"
	dev_type = 'reverb'
	outputInfo("*** Set Mixture: {value: %s}" % value)

	data = optBase((reverb_ip, port_udp_to), dev_type, dev_id, cmd, value=value)
	if not data or not data.has_key('value'):
		return False

	if data['value'] != value:
		outputInfo("Error: value don't match", 'error')
		return False

	outputInfo("Set the value of mixture to %s" % value, 'info')

	return True


def getStatus(dev_id):
	cmd = "reqStatus"
	ret = True

	closeOutput()
	dev_info = scanIP(dev_id)
	openOutput()

	res = []
	for dev_type in device_types:
		outputInfo("*** Get Status: %s" % dev_type)
		if not dev_info or not dev_info.has_key(dev_type):
			ret = False
			res.append((False, "not found ip"))
			continue
		data = optBase((dev_info[dev_type], port_udp_to), dev_type, dev_id, cmd)
		if not data or not data.has_key('status') or data['status'] != 'nomal':
			ret = False
			res.append((False, data))
			continue
		res.append((True, data))

	outputInfo('Status:', 'info')
	for dev_type, status in zip(device_types, res):
		string = "\t%-9s: " % dev_type
		if status[0]:
			string += status[1]['status']
			outputInfo(string, 'info')
		elif isinstance(status[1], str):
			string += status[1]
			outputInfo(string, 'info_error')
		else:
			string += status[1]['status']
			outputInfo(string, 'info_error')

	return ret


def setGain(dev_id, channel, value, judgement_ip=None):
	cmd = "reqGain"
	dev_type = 'judgement'
	outputInfo("*** Set Gain: {channel: %s,value: %s}" % (channel, value))

	data = optBase((judgement_ip, port_udp_to), dev_type, dev_id, cmd, value=value, channel=channel)
	if not data or not data.has_key('value') or not data.has_key('channel'):
		return False

	if data['value'] != value:
		outputInfo("Error: value don't match", 'error')
		return False
	if data['channel'] != channel:
		outputInfo("Error: channel don't match", 'error')
		return False

	outputInfo("Set the %s channel gain to %s" % (channel, value), 'info')

	return True


def getPowerMeter(dev_id, recorder_ip=None):
	cmd = "reqPowerMeter"
	dev_type = 'recorder'
	outputInfo("*** Get Power Meter")

	data = optBase((recorder_ip, port_udp_to), dev_type, dev_id, cmd)
	if not data:
		return False
	if not data.has_key("value_left") or not data.has_key("value_right"):
		outputInfo("Error: do not received the value of value_left or value_right", 'error')
		return False

	string = "Get PowerMeter: {value_left: %s, value_right: %s}" % (data['value_left'], data['value_right'])
	outputInfo(string, 'info')
	return True


def setReverbSW(dev_id, status, reverb_ip=None):
	cmd = "reqReverbSW"
	dev_type = 'reverb'
	outputInfo("*** Set ReverbSW: {status: %s}" % status)

	data = optBase((reverb_ip, port_udp_to), dev_type, dev_id, cmd, status=status)
	if not data or not data.has_key('status'):
		return False

	if data['status'] != status:
		outputInfo("Error: status don't match", 'error')
		return False

	outputInfo("Turn %s the reverb" % status, 'info')

	return True


def getVersion(dev_id):
	closeOutput()
	dev_info = scanIP(dev_id)
	openOutput()

	ret = True
	res = []
	for dev_type in device_types:
		if not dev_info or not dev_info.has_key(dev_type):
			ret = False
			res.append((False, "not found ip"))
			continue
		version = mytelnet.getVersion(dev_type, dev_info[dev_type])
		res.append((True, version))

	outputInfo('Version:', 'info')
	for item, dev_type in zip(res, device_types):
		string = '\t%-9s: ' % dev_type
		string += item[1]
		if item[0]:
			outputInfo(string, 'info')
		else:
			outputInfo(string, 'info_error')
	return ret


def reboot(dev_id):
	closeOutput()
	dev_info = scanIP(dev_id)
	openOutput()

	ret = True
	res = []
	for dev_type in device_types:
		if not dev_info or not dev_info.has_key(dev_type):
			ret = False
			res.append((False, "not found ip"))
			continue
		ret_info = mytelnet.reboot(dev_info[dev_type])
		if ret_info == mytelnet.t_finish:
			res.append((True, 'ongoing...'))
		else:
			ret = False
			res.append((False, 'failure'))

	outputInfo('Reboot:', 'info')
	for item, dev_type in zip(res, device_types):
		string = '\t%-9s: ' % dev_type
		string += item[1]
		if item[0]:
			outputInfo(string, 'info')
		else:
			outputInfo(string, 'info_error')
	return ret



opt_list = [scanIP, setMixture, getStatus, setGain, getPowerMeter, setReverbSW, getVersion, reboot]
opt_name_list = map(lambda x: x.__name__, opt_list)


def printHelp():
	import inspect
	outputInfo("usage: %s device_id options args" % sys.argv[0], 'info_error')
	outputInfo("options:", 'info')
	for opt in opt_list:
		str_opt = "\t%s" % opt.__name__
		outputInfo(str_opt, 'info')
		args = inspect.getargspec(opt)[0]
		if len(args) == 1:
			continue
		defaults = inspect.getargspec(opt)[-1]
		len_ignore = 0
		str_args = "\t\targs: "
		if defaults:
			len_ignore = len(defaults)
		if args and len(args) > 1:
			if args[0] == 'dev_id':
				args.pop(0)
			for i in range(len(args)-len_ignore):
				str_args += '%s ' % args[i]
			for i in range(len(args)-len_ignore, len(args)):
				str_args += '[%s] ' % args[i]
		print str_args
	print "example:"
	print "\t%s EP123456 setReverbSW on" % sys.argv[0]


def checkDeviceid(dev_id):
	if re.match('^EP[\d]{6}$', dev_id):
		return dev_id
	if re.match('^[\d]{6}$', dev_id):
		dev_id = 'EP' + dev_id
		return dev_id
	else:
		outputInfo("Error: device's id[%s] invalid" % dev_id, 'error')
		return None


def checkOpt(dev_opt):
	dev_opt_tmp = dev_opt.lower()
	opt_name_list_tmp = map(lambda x: x.lower(), opt_name_list)
	if dev_opt_tmp not in opt_name_list_tmp:
		outputInfo("Error: Invalid operation[%s]" % dev_opt, 'error')
		return -1
	return opt_name_list_tmp.index(dev_opt_tmp)


# def checkIP(dev_ip):
# 	if re.match(r'^[\d]{3}\.[\d]{3}\.[\d]{1,3}\.[\d]{1,3}$', dev_ip):
# 		return dev_ip
# 	return None


def checkArgv():
	if len(sys.argv) == 1:
		print "Error: No parameters"
		print "You can exec '%s -h' to get help" % sys.argv[0]
		exit(1)
	if len(sys.argv) == 2:
		if sys.argv[1] == '-h' or sys.argv[1] == '--help':
			printHelp()
		else:
			print "Error: Too few parameters"
			print "You can exec '%s -h' to get help" % sys.argv[0]
		exit(1)

	dev_id = sys.argv[1]
	dev_id = checkDeviceid(dev_id)
	if not dev_id:
		exit(1)

	dev_opt = sys.argv[2]
	opt_index = checkOpt(dev_opt)
	if opt_index < 0:
		exit(1)

	args = [dev_id]
	if len(sys.argv) > 3:
		args += sys.argv[3:]

	return (opt_index, args)



def main():
	opt_index, args = checkArgv()
	opt_fun = opt_list[opt_index]
	apply(opt_fun, args)


if __name__ == '__main__':
	main()
	# scanIP("EP982491")
	# setMixture('EP982491', '0.3')
	# getStatus('EP982491')
	# setGain('EP982491', 'left', '10')
	# setReverbSW('EP982491', 'on')
	# print checkIP('192.168.1.123')
	# import inspect
	# print inspect.getargspec(setReverbSW)
	# print len(inspect.getargspec(setReverbSW)[-1])
