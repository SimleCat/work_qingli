import logging
import myprint
# LOG_FILE = 'log_%s.txt' % time.strftime("%Y%m%d-%H%M", time.localtime())
LOG_FILE = 'log.txt'
fmt = '[%(asctime)s] %(message)s'

logger = None

flag_output = True
str_style = {
				'debug'		: {'mode': ''		, 'fore': ''		, 'back': ''},
				'info'		: {'mode': 'bold'	, 'fore': 'green'	, 'back': ''},
				'info_error': {'mode': 'bold'	, 'fore': 'red'		, 'back': ''},
				'warning'	: {'mode': ''		, 'fore': 'yellow'	, 'back': ''},
				'error'		: {'mode': ''		, 'fore': 'red'		, 'back': ''}
}


def closeOutput():
	global flag_output
	flag_output = False


def openOutput():
	global flag_output
	flag_output = True


def getLogger():
	logger = logging.getLogger()
	handler = logging.FileHandler(LOG_FILE)
	formatter = logging.Formatter(fmt)

	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.setLevel(logging.NOTSET)
	return logger


def outputInfo(string, level='debug'):
	global logger
	global flag_output

	level = level.strip()
	level = level.lower()

	if not str_style.has_key(level):
		level = 'debug'
	style = str_style[level]
	string = myprint.useStyle(string, style['mode'], style['fore'], style['back'])
	if flag_output:
		print string

	# if not logger:
		# logger = getLogger()
	# logger.info(string)
