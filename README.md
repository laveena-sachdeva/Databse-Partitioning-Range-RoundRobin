DATABASE PARTITIONING

The required task is to simulate data partitioning approaches on-top of an open source relational database management system (i.e., PostgreSQL). Each student must generate a set of Python functions that load the input data into a relational table, partition the table using different horizontal fragmentation approaches, and insert new tuples into the right fragment.

Input Data: The input data is a Movie Rating data set collected from the MovieLens website (http://movielens.org).  The raw data is available in the file rating.dat.

The rating.dat file contains 10 million ratings and 100,000 tag applications applied to 10,000 movies by 72,000 users. Each line of this file represents one rating of one movie by one user, and has the following format:
                                                  UserID::MovieID::Rating::Timestamp

Ratings are made on a 5-star scale, with half-star increments. Timestamps represent seconds since midnight Coordinated Universal Time (UTC) of January 1, 1970. A sample of the file contents is given below:

                                                          1::122::5::838985046

                                                          1::185::5::838983525

                                                          1::231::5::838983392

loadratings():
Implement a Python function LoadRatings() that takes a file system absolute path that contains the rating.dat file as input. LoadRatings() then loads the rating.dat content into a table (saved in PostgreSQL) named Ratings that has the following schema:
UserID (int) – MovieID (int) – Rating (float)

rangepartition():
Implement a Python function Range_Partition() that takes as input: (1) the Ratings table stored in PostgreSQL and (2) an integer value N; that represents the number of partitions. Range_Partition() then generates N horizontal fragments of the Ratings table and store them in PostgreSQL. The algorithm should partition the ratings table based on N uniform ranges of the Rating attribute.

roundrobinpartition ():
Implement a Python function RoundRobin_Partition() that takes as input: (1) the Ratings tabletored in PostgreSQL and (2) an integer value N; that represents the number of partitions. The function then generates N horizontal fragments of the Ratings table and stores them in PostgreSQL. The algorithm should partition the ratings table using the round robin partitioning approach.

roundrobininsert():
Implement a Python function RoundRobin_Insert() that takes as input: (1) Ratings table stored in PostgreSQL, (2) UserID, (3) ItemID, (4) Rating. RoundRobin_Insert() then inserts a new tuple to the Ratings table and the right fragment based on the round robin approach.

rangeinsert():
Implement a Python function Range_Insert() that takes as input: (1) Ratings table stored in Post-greSQL (2) UserID, (3) ItemID, (4) Rating. Range_Insert() then inserts a new tuple to the Ratings able and the correct fragment (of the partitioned ratings table) based upon the Rating value.



Question with respect to Partitioning:

The number of partitions here refer to the number of tables to be created.

For rating values in [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]

Case N = 1,
One table containing all the values.

Case N = 2,
Two tables,

Partition 0 has values [0, 2.5]
Partition 1 has values (2.5, 5]

Case N = 3,

Three tables,

Partition 0 has values [0, 1.67]

Partition 1 has values (1.67, 3.34]
Partition 2 has values (3.34, 5]

Uniform range means a region is divided uniformly, I hope the example gives a clear picture. 


ABOUT THE CODE:

databasePartitioningMain.py: This has the entry function. It imports Interface.py and testHelper.py which has all the functions described above.  You will have to adjust/change the global variables declared at the top of this file according to your input.

testHelper.py:  This has other utility functions to test the correctness of the partitioning created using the functions described above.

Interface.py: Implementation of the above described functions.

