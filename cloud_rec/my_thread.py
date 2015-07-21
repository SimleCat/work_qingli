import threading

class MyThread(threading.Thread):
	def __init__(self, func, args, name=''):
		threading.Thread.__init__(self)
		self.name = name
		self.func = func
		self.args = args
		self.ret = None

	def run(self):
		self.ret = apply(self.func, self.args)