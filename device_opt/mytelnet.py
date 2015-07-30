#encoding=utf-8

import telnetlib
import time
from output import outputInfo

t_username = 'root'
t_password = 'ep_1234'
t_timeout = 3
t_finish = '~ # '

def do_telnet(host, username, password, finish, command):
	# 连接Telnet服务器
	try:
		tn = telnetlib.Telnet(host, timeout=t_timeout)
	except:
		now = time.strftime("%H:%M:%S", time.localtime())
		outputInfo('[%s] connet : Could not connect to host' % now)
		exit()
	tn.set_debuglevel(0)

	# 输入登录用户名
	log = tn.read_until('login: ')
	now = time.strftime("%H:%M:%S", time.localtime())
	outputInfo('[%s] login: user' % (now))
	tn.write(username + '\n')

	# 输入登录密码
	tn.read_until('Password: ')
	now = time.strftime("%H:%M:%S", time.localtime())
	outputInfo('[%s] login: passwd' % (now))
	tn.write(password + '\n')

	# 登录完毕后执行命令
	tn.read_until(finish)

	tn.write('%s\n' % command)
	time.sleep(0.5)
	log = tn.read_very_eager()  #.replace('\n', '    ')
	# log = tn.read_some()
	now = time.strftime("%H:%M:%S", time.localtime())
	outputInfo('[%s] cmd: %s' % (now, repr(log)))

	#执行完毕后，终止Telnet连接（或输入exit退出）
	tn.close() # tn.write('exit\n')

	return log.split('\n')[1]


def getVersion(dev_type, host):
	cmd = 'cat /home/%s/version.txt' % dev_type
	return do_telnet(host, t_username, t_password, t_finish, cmd)


def reboot(host):
	cmd = 'reboot'
	return do_telnet(host, t_username, t_password, t_finish, cmd)


if __name__ == '__main__':
	host = '192.168.1.127'
	# cmd = 'cat /home/reverb/version.txt'
	# print do_telnet(host, t_username, t_password, t_finish, cmd)
	reboot(host)

"""
if __name__=='__main__':
	count = 1
	while 1 :
		# 配置选项
		Host = '192.168.1.101' # Telnet服务器IP
		username = 'root'   # 登录用户名
		password = 'ep_1234'  # 登录密码
		finish = '~ # '      # 命令提示符
		#commands = ['ls /home -l']
		commands = ['cat /home/reverb/version.txt', 'reboot']
		do_telnet(Host, username, password, finish, commands, count)
		time.sleep(20)
		count += 1
"""
