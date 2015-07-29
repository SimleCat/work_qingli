#encoding=utf-8

import telnetlib
import time
import json


def do_telnet(Host, username, password, finish, commands):
	# 连接Telnet服务器
	try:
		tn = telnetlib.Telnet(Host, port=23, timeout=3)
	except:
		now = time.strftime("%H:%M:%S", time.localtime()) 
		print '[%s] connet : Could not connect to host' % now
		exit()
	tn.set_debuglevel(0)
	 
	# 输入登录用户名
	log = tn.read_until('login: ')
	now = time.strftime("%H:%M:%S", time.localtime()) 
	print '[%s] login : user' % (now)
	tn.write(username + '\n')
	
	# 输入登录密码
	tn.read_until('Password: ')
	now = time.strftime("%H:%M:%S", time.localtime()) 
	print '[%s] login : passwd' % (now)
	tn.write(password + '\n')
	  
	# 登录完毕后执行命令
	tn.read_until(finish)
	for command in commands:
		tn.write('%s\n' % command)
		time.sleep(1)
		log = tn.read_very_eager()  #.replace('\n', '    ')
		now = time.strftime("%H:%M:%S", time.localtime()) 
		print '[%s] cmds : %s' % (now, log)
	
	#执行完毕后，终止Telnet连接（或输入exit退出）
#	tn.read_until(finish)
	tn.close() # tn.write('exit\n')

def reboot(Host):
#	Host = '192.168.1.101' # Telnet服务器IP
	devType = ["judgement", "reverb", "recorder"]
	for role in devType:
		if True == Host.has_key(role) :
			host = Host[role]
			print host
			username = 'root'   # 登录用户名
			password = 'ep_1234'  # 登录密码
			finish = '~ # '      # 命令提示符
			commands = ['cat /home/reverb/version.txt', 'reboot']
			do_telnet(host, username, password, finish, commands)
			time.sleep(1)
	


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
