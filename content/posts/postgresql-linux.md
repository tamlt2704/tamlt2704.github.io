title: Postgres basic command 
date: 2017-02-05


1. Install postgresql
	apt-get install postgresql postgresql-client

2. Start postgresql
	/etc/init.d/postgresql start or
	/usr/sbin/service postgresql start

3. Check status
	/etc/init.d/postgresql status
	/usr/sbin/service postgresql status

4. Change postgres password
	passwd postgres

5. Accessing postgresql 
	su - postgres
	psql

6. Exit psql
	\q

7. Create new database
	su - postgres

	# createdb
	createdb flaskdb

	# list all databses
	psql
	\l		

8. Accessing postgresql and database
	su - postgresql
	psql

	# which database i'm using
	\connect or \c

	# switch database
	\c flaskdb

9. Create table 
	CREATE TABLE "user" ( 
		_id INT Serial,
		username varchar(40),
		age INT
	);

10. View table detail
	\d+ "user"

11. Drop table
	DROP TABLE "user";


