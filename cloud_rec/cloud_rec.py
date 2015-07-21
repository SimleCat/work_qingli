import os
import time
import sql_opt
from my_thread import MyThread

num_thread = 5
exec_string = "./test.sh %s %s"
scan_interval = 1


def init():
	print "=" * 50
	print "Host\t:", sql_opt.sql_host
	print "Port\t:", sql_opt.sql_port
	print "User\t:", sql_opt.sql_user
	print "Passwd\t:", sql_opt.sql_passwd
	print "db_name\t:", sql_opt.db_name
	print "tb_name\t:", sql_opt.tb_name
	print "=" * 50
	print ''

	print "#Create"
	print "ret:", sql_opt.create()
	print ''

	# print "#Insert"
	# print "ret:", sql_opt.insert('123458', 'waiting')
	# print ''

	# print "#Update"
	# print "ret:", sql_opt.update('123456', 'process')
	# print ''

	# print "#Query"
	# print sql_opt.query()
	# print ''

def func(job_id, path_in):
	if not sql_opt.update(job_id, sql_opt.status_process):
		return False
	tmp = path_in.split('/')
	tmp2 = tmp[-1].split('.')
	tmp2[-1] = 'wav'
	tmp[-1] = 'out_' + '.'.join(tmp2)
	path_out = '/'.join(tmp)
	print "path_in:", path_in
	print "path_out:", path_out

	ret = os.system(exec_string % (path_in, path_out))

	if ret != 0:
		sql_opt.update(job_id, sql_opt.status_waiting)
		return False

	sql_opt.update(job_id, sql_opt.status_sucess)
	return True

def getFreeThreads(threads):
	res = []
	for i in range(len(threads)):
		if threads[i] == None or not threads[i].isAlive():
			res.append(i)
	return res

def main():
	init()
	threads = [None] * num_thread;
	while True:
		print ''
		time.sleep(scan_interval)
		free_th_indexs = getFreeThreads(threads)
		print "free_th_indexs:", free_th_indexs
		if not free_th_indexs:
			continue
		wait_jobs = sql_opt.query()
		print "wait_jobs: ", wait_jobs
		if not wait_jobs:
			continue
		for i in range(len(free_th_indexs)):
			if i >= len(wait_jobs):
				break
			threads[free_th_indexs[i]] = MyThread(func, wait_jobs[i])
			threads[free_th_indexs[i]].start()



if __name__ == '__main__':
	main()

