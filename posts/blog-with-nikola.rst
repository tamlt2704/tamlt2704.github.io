.. title: blog with nikola
.. slug: blog-with-nikola
.. date: 2018-03-31 14:30:33 UTC+08:00
.. tags: tools
.. category: 
.. link: 
.. description: 
.. type: text


1. **Why nikola**

	I used to use jekyll for blogging but I always have troubles with installing ruby and their dependencies. Futhermore, modifying the blog in a language that I'm not familiar is not a good idea. Since I already have python in my system, adding nikola is just one line of code. Start with something I know gives me the power to overcome the procastination j.

2. **Start blogging with nikola and publish to github**

	**Create a repository on github follow the name convention <username>.github.io**

	**Clone repository**

		.. code-block:: shell

			git clone http://github.com/<username>/<username>.github.io

	**Install nikola**

		.. code-block:: shell

			pip install nikola

	**Init new blog**

		.. code-block:: python

			nikola init .

	**Create new post**

		.. code-block:: python

			nikola new_post
			<edit your post>

	**Create new page**

		.. code-block:: python

			nikola new_page

	**View your blog**

		.. code-block:: python

			nikola build && nikola serve

	**Publish to github**

		.. code-block:: python

			nikola github_deploy

Enjoy your blog at http://<username>.github.io and happy blogging!

