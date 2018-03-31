import sys

def is_prime_number(n):
	if any([n % i == 0 for i in range(2, n/2)]):
		return False
	return True 

def find_prime_number(filename):
		with open(filename, 'r') as f:
			for line in f:
				n = int(line)
				print n,is_prime_number(n)

if __name__ == "__main__":
	find_prime_number(sys.argv[1])

"""
INPUT		Output	
	3 	3 True
	10 	10 False
	15	15 False
	17	17 True
""" 
