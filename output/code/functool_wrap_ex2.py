import sys
from functools import wraps
from datetime import datetime

def exception_wrapper(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		try:
			f(args, **kwargs)
		except Exeption as e:
			print e
			pass
	return wrapper 


def running_time(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		t1 = datetime.now()
		f(args, **kwargs)
		print 'function', f.__name__ , 'ran in ', datetime.now() - t1
	return wrapper 

def is_prime_number(n):
	if any([n % i == 0 for i in range(2, n/2)]):
		return False
	return True 

@running_time
@exception_wrapper
def find_prime_number(filename):
	try:
		with open(filename, 'r') as f:
			for line in f:
				n = int(line)
				print n,is_prime_number(n)
	except: 
		pass

if __name__ == "__main__":
	find_prime_number(sys.argv[1])

"""
INPUT		Output	
	3 	3 True
	10 	10 False
	15	15 False
	17	17 True
""" 
