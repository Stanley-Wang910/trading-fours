import mysql.connector
from mysql.connector import Error
import mysql.connector.pooling

import os


try:
    connection = mysql.connector.pooling.MySQLConnectionPool(
        host=os.environ.get('MYSQL_HOST'),
        port=os.environ.get('MYSQL_PORT'),
        user=os.environ.get('MYSQL_USER'),
        password=os.environ.get('MYSQL_PASSWORD'),
        database=os.environ.get('MYSQL_DATABASE'),
        pool_name="pool",
        pool_size=5
    )
    print("MySQL connection successful")
except Error as e:
    print("Error while connecting to MySQL", e)
    raise
