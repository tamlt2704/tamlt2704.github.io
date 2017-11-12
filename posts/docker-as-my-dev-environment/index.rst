.. title: docker as my dev environment
.. slug: docker-as-my-dev-environment
.. date: 2017-11-12 22:08:21 UTC+08:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text

Since I want to keep my laptop 'clean' docker is a good choice for me. 

Below are the steps that I use to setup my dev environment.


1. **pull docker image**
	
	.. code-block:: shell

		docker pull ubuntu

2. **create container**

	.. code-block:: shell
		
		docker run -it --name=ubuntu -p 8080:80 -p 2222:22 -v c:\devtools\home:/mnt/data --hostname=ubuntu ubuntu

3. **start container**

	.. code-block:: shell

		doker start ubuntu

4. **attach container (run it after 3)**

	.. code-block:: shell

		doker attach ubuntu

5. **Other docker commands**

	docker images --> list all images

	docker rmi <image_name> --> remove docker images

	docker ps --> list all container are running

	docker ps -a  --> list all docker 

	docker rm <container_name>

	docker rm -f <container_name>
