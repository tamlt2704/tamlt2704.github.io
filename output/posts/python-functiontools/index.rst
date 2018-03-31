.. title: python functiontools
.. slug: python-functiontools
.. date: 2018-03-31 18:02:19 UTC+08:00
.. tags: 
.. category: python
.. link: 
.. description: 
.. type: text

python functiontools provides bunch of usefull tools to work with functions. In this post I will introduce some application of this module to make our life easier.

**1. wrap function**

Example if I want a program to read a file that contains multiple numbers, print True or Fasle if it is a prime number or not

It can be easily implementation as bellow:

.. listing:: functool_wrap_ex1.py python
	
If the file does not exists, the program will thrown an exception. We can avoid that by adding try catch as bellow


.. code-block:: python

	find_prime_number(filename):
		try:
			with open(filename, 'r') as f:
				for line in f:
					n = int(line)
					print n,is_prime_number(n)
		except Exception as e: 
			print e
			pass

- The code will print the exception instead of crashing now. 
- Imagine if we have to check exception for multiple functions in our code. It will not a good idea to have multiple try / catch. wraps is a nice built-in function to make it less frustruated.

.. listing:: functool_wrap_ex2.py python

- As you can see, we can even monitor the run time of the function without changing it internal code.



