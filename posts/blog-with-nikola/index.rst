.. title: blog with nikola
.. slug: blog-with-nikola
.. date: 2017-11-12 22:40:30 UTC+08:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text

Simple steps to have a github page with nikola


1. **Setup environmenti**

	virtualenv venv && source venv/bin/active

	pip install nikola

2. **create new site**

	nikola init mysite

3. **create new post**

	nikola new_post
	
	edit post in: post/<post-name>

	learn about restructured text here_ 
	
.. _here: http://getnikola.com/handbook.html/


4. **deploy to github**

	git init .

	git remote add origin https://github.io/<github_name>/<github_name>.github.io
	
	# deploy

	nikola github_deploy

Enjoy!
