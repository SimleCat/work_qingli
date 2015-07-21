import MySQLdb
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

sql_host = 'localhost'
sql_port = 3306
sql_user = 'root'
sql_passwd = '111'

db_name = 'dbCloudRec'
tb_name = 'TB_CloudRec'

status_wait = "waiting"
status_process = "process"
status_sucess = "sucess"
jobid_index = 1
pathrec_index = 12

def base(exec_string):
	ret = True
	conn = MySQLdb.connect(
		host = sql_host,
		port = sql_port,
		user = sql_user,
		passwd = sql_passwd,
		db = db_name)
	cur = conn.cursor()
	try:
		cur.execute(exec_string)
		conn.commit()
	except MySQLdb.Error, e:
		print "Error: MySQl[%s]" % e.args[1]
		ret = False
	cur.close()
	conn.close()
	return ret

def create():
	exec_string = "CREATE TABLE IF NOT EXISTS %s(ID INT PRIMARY KEY AUTO_INCREMENT, \
                                                                JOBID 		VARCHAR(32) NOT NULL, \
                                                                STATUS      VARCHAR(10), \
                                                                DURATION    VARCHAR(10), \
                                                                BPM         VARCHAR(10), \
                                                                GENDER      VARCHAR(10), \
                                                                GENRE       VARCHAR(20), \
																ACCOMSN		VARCHAR(32), \
																STARTFRAIN	VARCHAR(10), \
																ENDFRAIN	VARCHAR(10), \
                                                                TIME        INT, \
                                                                DELETED     INT, \
                                                                PATH_REC	VARCHAR(128))" % tb_name
	return base(exec_string)

def insert(job_id, status):
	exec_string = 'INSERT INTO %s(JOBID, STATUS) VALUES("%s", "%s")' % (tb_name, job_id, status)
	return base(exec_string)

def update(job_id, status):
	exec_string = 'update %s set STATUS = "%s" where JOBID = "%s"' % (tb_name, status, job_id)
	return base(exec_string)

def query():
	exec_string = 'SELECT * FROM %s WHERE STATUS="%s"' % (tb_name, status_wait)
	conn = MySQLdb.connect(
		host = sql_host,
		port = sql_port,
		user = sql_user,
		passwd = sql_passwd,
		db = db_name)
	cur = conn.cursor()
	try:
		num_wait = cur.execute(exec_string)
	except MySQLdb.Error, e:
		print "Error: MySQl[%s]" % e.args[1]
	res = cur.fetchall()
	cur.close()
	conn.close()
	res = map(lambda x: (x[jobid_index], x[pathrec_index]), res)
	res = list(set(res))
	print 'Number of waiting:', len(res)
	return res

