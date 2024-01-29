import mysql.connector
from mysql.connector import Error
import yaml
import os


def get_db_config():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'config', 'db_config.yml')
        with open (config_path, 'r') as stream:
            config = yaml.safe_load(stream)
        return config['database']
    except FileNotFoundError:
        return "Error: The database configuration file 'db_config.yaml' was not found."
    except yaml.YAMLError as exc:
        return f"Error parsing 'db_config.yaml': {exc}"
    except Exception as exc:
        return f"An unexpected error occurred: {exc}"

def db_connect():
    try:
        db_config = get_db_config()


        conn = mysql.connector.connect(
            user=db_config['username'],
            password=str(db_config['password']),
            host=db_config['host'],
            database=db_config['dbname'],
            port = str(db_config['port'])
            )

        if conn.is_connected():
            return conn

    except Error as e:
        print("Error while connecting to MySQL", e)

#finally:
#    if connection.is_connected():
#        connection.close()
#        print("MySQL connection is closed")

def get_record(end_name, end_url, port):

    try :
        query_conditions = []
        conn = db_connect()    
        cursor = conn.cursor()
        query = "SELECT * FROM map_table"
        if end_name:
            query_conditions.append (f"end_name ='{end_name}'")
        if end_url:
            query_conditions.append(f"end_url LIKE '%{end_url}%'")
        if port:
            port = int(port)
            query_conditions.append(f"port={port}")
        query += " WHERE " + " OR ".join(query_conditions) 
        cursor.execute(query)
        fetched_result = cursor.fetchall()
        cursor.close()
        conn.close()
        if fetched_result:
            return fetched_result
        else:
            return 0

    except Error as e:
        print (f"Error: {e}")


def insert_record(end_name, end_url, port):
    
    try:
        conn = db_connect()
        cursor = conn.cursor()
        query = "INSERT INTO map_table (end_name, end_url, port) VALUES (%s,%s,%s)"
        cursor.execute(query,(end_name, end_url, port))
        conn.commit()
        cursor.close()
        conn.close()
        return 1

    except Error as e:
        return e



def delete_record(end_name):
    try:
        conn=db_connect()
        cursor = conn.cursor()
        query = f"DELETE FROM map_table where end_name = %s"

        cursor.execute(query,(end_name,))
        conn.commit()
        cursor.close()
        conn.close()
        return 1
    except Error as e:
        print("========================================================")
        print ("cannot_execute")
        print("========================================================")