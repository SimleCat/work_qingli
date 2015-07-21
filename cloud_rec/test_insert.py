import sql_opt


def insert(job_id, status, path_in):
	exec_string = 'INSERT INTO %s(JOBID, STATUS, PATH_REC) VALUES("%s", "%s", "%s")' % \
		(sql_opt.tb_name, job_id, status, path_in)
	return sql_opt.base(exec_string)

def main():
	job_id_base = 111111
	status = sql_opt.status_wait
	path_in_temp = "./fold/job%d.mp3"

	for i in range(10):
		job_id = str(job_id_base + i)
		path_in = path_in_temp % (i+1)
		insert(job_id, status, path_in)


if __name__ == "__main__":
	main()

