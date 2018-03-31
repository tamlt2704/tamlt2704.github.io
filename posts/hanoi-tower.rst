.. title: hanoi tower
.. slug: hanoi-tower
.. date: 2018-03-31 17:24:38 UTC+08:00
.. tags: algorithm
.. category: 
.. link: 
.. description: 
.. type: text


	**Objective: To move N disks from column one (C1) to colum three (C3).**

	.. image:: /galleries/hn_tw_1.PNG


	**1. First we have to find a way to move top N-1 disks from C1 to C2 using C3 as a temporary column.**
	
	.. image:: /galleries/hn_tw_2.PNG

	**2. Now there are one disk left at C1, move it directly from C1 to C3**

	.. image:: /galleries/hn_tw_3.PNG

	**3. Next Step is to move N-1 disks from C2 to C3 using C1 as temporary column**

	.. image:: /galleries/hn_tw_4.PNG
	 

.. listing:: hanoi_tower.py python
