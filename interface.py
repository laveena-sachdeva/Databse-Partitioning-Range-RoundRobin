#!/usr/bin/python2.7
import psycopg2
DATABASE_NAME = 'database_partitioning_1'

def getopenconnection(user='postgres', password='abcd', dbname='postgres'):
    return psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='localhost' password='" + password + "'")

def create_db(dbname):
    """
    We create a DB by connecting to the default user and database of Postgres
    The function first checks if an existing database exists for a given name, else creates it.
    :return:None
    """
    # Connect to the default database
    con = getopenconnection(dbname='postgres')
    con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    # Check if an existing database with the same name exists
    cur.execute('SELECT COUNT(*) FROM pg_catalog.pg_database WHERE datname=\'%s\'' % (dbname,))
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute('CREATE DATABASE %s' % (dbname,))  # Create the database
    else:
        print 'A database named {0} already exists'.format(dbname)

    # Clean up
    cur.close()
    con.close()

def loadratings(table_name,filepath,conn):

	print("Load Ratings started")
	cur=conn.cursor()

	#Create a temporary table to load all the columns of the file
	cur.execute("drop table if exists " + table_name + "_full_file")
	cur.execute("create table " + table_name + "_full_file (UserId INT, Sep1 VARCHAR(10), MovieId INT, Sep2 VARCHAR(10), Rating REAL, Sep3 VARCHAR(10), Timestamp INT) ")
		
	print("Before file read")
	#Load data into this temporary table
	with open(filepath,'r') as f:
		cur.copy_from(f,table_name + "_full_file",sep=':')
	
	#Create the ratings table with required schema
	cur.execute("drop table if exists " + table_name)
	cur.execute("create table " + table_name + " (UserId INT, MovieId INT, Rating REAL)")
	
	#Insert required columns in the ratings table
	cur.execute("insert into " + table_name + " select UserId, MovieId, Rating from " + table_name + "_full_file ")
	cur.execute("drop table if exists " + table_name + "_full_file")
	print("RATINGS TABLE LOADED")
		
	conn.commit()
	cur.close()
	
def rangepartition(table_name, no_of_partitions, conn):
	
	cur = conn.cursor()
	
	range=5.0/no_of_partitions
	lower=0
    	part=0
	
	#Create a meta table meta_range_part_info to store the number of partitionss
	cur.execute("drop table if exists meta_range_part_info")
	cur.execute("create table meta_range_part_info (no_of_partitions INT)")
	cur.execute("truncate table meta_range_part_info")	
	cur.execute("insert into meta_range_part_info values (" + str(no_of_partitions) + ") "  )

	#Insert records into different partitions based on the rating value
    	while lower<5.0:
		if lower == 0:
		    	cur.execute("drop table if exists range_part"+str(part))
			cur.execute("create table range_part"+str(part)+ " as select * from "+table_name+" where rating>="+str(lower)+ " and Rating<="+str(lower+range)+";")
			lower = lower + range
		    	part=part + 1
		else:
	    		cur.execute("drop table if exists range_part"+str(part))
			cur.execute("create table range_part"+str(part)+" as select * from "+table_name+" where rating>"+str(lower)+ " and rating<="+str(lower+range)+";")
	    		lower=lower + range
			part=part + 1
	    
	
	conn.commit()
    	cur.close()
         
		 
def roundrobinpartition(table_name, no_of_partitions, conn):

	cur = conn.cursor()

	list_partitions = list(range(no_of_partitions))

	#Create a meta table to store the number of partitions and the last partition where data was inserted
	cur.execute("drop table if exists meta_rrobin_part_info")
	cur.execute("create table meta_rrobin_part_info (partition_number INT, no_of_partitions INT)")

	
	last=-1
	#Insert into rrobin_partitions based on the row_numbers 
	for part in list_partitions:
		cur.execute("drop table if exists rrobin_part" + str(part))
		cur.execute("create table rrobin_part" + str(part) + " as select userid,movieid,rating from  (select userid,movieid,rating,row_number() over() as row_num from " + str(table_name) + ") a where (a.row_num -1 + " + str(no_of_partitions) + ")% " + str(no_of_partitions) + " = " + str(part) )
		last=part
		
	
	#Update the meta-data table to store the last partition where data was inserted, and the total number of partitions
	cur.execute("truncate table meta_rrobin_part_info")	
	cur.execute("insert into meta_rrobin_part_info values (" + str(last) + "," + str(no_of_partitions) +") "  )
	
	cur.close()

	

def roundrobininsert(table_name, user_id, item_id, rating, conn):
	
	cur = conn.cursor()
	
	#Select the partition number where data was last inserted and the total number of partitions
	cur.execute("select partition_number,no_of_partitions from meta_rrobin_part_info")
	f = cur.fetchone()
	part = f[0]
	no_of_partitions = f[1]
	

	#Insert into the correct rrobin_partition  and then into the main ratings table as well	
	cur.execute("insert into rrobin_part" + str((part + 1)%no_of_partitions) + " values( " + str(user_id) + "," + str(item_id) + "," + str(rating) + ") ")
	cur.execute("insert into ratings values( " + str(user_id) + "," + str(item_id) + "," + str(rating) + ") ")
	part = (part + 1)%no_of_partitions

	#Update the partition number in the meta table
	cur.execute("truncate table meta_rrobin_part_info")	
	cur.execute("insert into meta_rrobin_part_info values (" + str(part) + "," + str(no_of_partitions) +") "  )

	cur.close()

def rangeinsert(table_name, user_id, item_id, rating, conn):
	
	cur = conn.cursor()


	#Select the total number of range partitions from the meta table	
	cur.execute("select no_of_partitions from meta_range_part_info")
	no_of_partitions = cur.fetchone()[0]
	
	range = 5.0/no_of_partitions
	low=0
	high=range
	part=0
	
	#Determine the correct partition
	while low<5.0:
		if low==0:
			if rating >= low and rating <= high:
				break
			part = part + 1
			low = high
			high = high + range
					
		else:
			if rating > low and rating <= high:
				break
			part  = part + 1
			low = high
			high = high + range
			
	#Insert into the partition and main ratings table
	cur.execute("insert into range_part" + str(part) + " values (" + str(user_id) + "," + str(item_id) + "," + str(rating) + ") ")
	cur.execute("insert into ratings values( " + str(user_id) + "," + str(item_id) + "," + str(rating) + ") ")
	cur.close()