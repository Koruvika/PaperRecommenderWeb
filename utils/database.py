import uuid
from typing import List

import pandas as pd
import yaml
from tqdm import tqdm
from yaml.loader import SafeLoader
import mysql.connector


config_file = "configs/config.yaml"
# user_db_file = "/mnt/data1/paper_recommend_system/data/users.csv"
# session_db_file = "/mnt/data1/paper_recommend_system/data/session.csv"
# session_paper_db_file = "/mnt/data1/paper_recommend_system/data/session_item.csv"
# paper_db_file = "/mnt/data1/paper_recommend_system/data/papers.csv"

# user_df = pd.read_csv(user_db_file)
# session_df = pd.read_csv(session_db_file)
# paper_df = pd.read_csv(paper_db_file)
# session_item_df = pd.read_csv(session_paper_db_file)

with open(config_file) as file:
    config = yaml.load(file, Loader=SafeLoader)


host = "localhost"
user = "duong"
password = "12345678"
database = "pseudo_database"


def get_items_by_column_contain_text(table, column, text):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()
    query = f"SELECT * FROM {table} WHERE LOWER(`{column}`) LIKE '%{text}%'"
    my_cursor.execute(query)
    results = my_cursor.fetchall()
    my_cursor.close()
    mydb.close()
    return results



def get_items_by_column_value(table, column, value):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()
    query = f"SELECT * FROM {table} WHERE `{column}` = %s"
    #print(query, value)
    my_cursor.execute(query, (value, ))
    results = my_cursor.fetchall()
    my_cursor.close()
    mydb.close()
    return results



def get_items_by_column_values(table: str, column: str, values: List[str]):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    values = tuple(values)
    my_cursor = mydb.cursor()
    query = f"SELECT * FROM {table} WHERE `{column}` IN ({','.join(['%s'] * len(values))})"
    my_cursor.execute(query, values)
    results = my_cursor.fetchall()
    my_cursor.close()
    mydb.close()
    return results



def get_sessions_by_name_user_id(name, user_id):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()
    query = f"SELECT * FROM sessions WHERE `Name` = %s and `User ID` = %s"
    my_cursor.execute(query, (name, user_id))
    results = my_cursor.fetchall()
    my_cursor.close()
    mydb.close()
    return results


def get_items_from_table(table):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()
    query = f"SELECT * FROM {table}"
    my_cursor.execute(query)
    results = my_cursor.fetchall()
    my_cursor.close()
    mydb.close()
    return results


def insert_session_into_sessions(session_id, name, user_id):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()
    value = (session_id, name, user_id)
    query = f"INSERT INTO sessions (`Session ID`, `Name`, `User ID`) VALUES (%s, %s, %s)"
    my_cursor.execute(query, value)
    mydb.commit()
    my_cursor.close()
    mydb.close()


def insert_user_into_users(user_id: str, name: str, email: str, username: str, _password: str):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()
    value = (user_id, username, _password, name, email)
    query = f"INSERT INTO users (`User ID`, `Username`, `Password`, `Name`, `Email`) VALUES (%s, %s, %s, %s, %s)"
    my_cursor.execute(query, value)
    mydb.commit()
    my_cursor.close()
    mydb.close()


def insert_paper_into_session(session_id: str, paper_id: str, dt, appropriate):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()
    appropriate = 1 if appropriate else 0
    value = (session_id, paper_id, dt, appropriate)
    query = f"INSERT INTO session_item (`Session ID`, `Paper ID`, `Date`, `Appropriate`) VALUES (%s, %s, %s, %s)"
    my_cursor.execute(query, value)
    mydb.commit()
    my_cursor.close()
    mydb.close()


def delete_session_by_session_id(session_id):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()

    delete_query = f"DELETE FROM sessions WHERE `Session ID` = %s"

    # Execute the query with the values to delete as a tuple
    my_cursor.execute(delete_query, (session_id,))

    # Commit the changes
    mydb.commit()

    # Close the cursor and connection
    my_cursor.close()
    mydb.close()


def delete_session_by_name_user_id(name, user_id):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()

    delete_query = f"DELETE FROM sessions WHERE `Name` = %s AND `User ID` = %s"

    # Execute the query with the values to delete as a tuple
    my_cursor.execute(delete_query, (name, user_id))

    # Commit the changes
    mydb.commit()

    # Close the cursor and connection
    my_cursor.close()
    mydb.close()


def delete_session_item_by_session_id(session_id):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()

    delete_query = f"DELETE FROM session_item WHERE `Session ID` = %s"

    # Execute the query with the values to delete as a tuple
    my_cursor.execute(delete_query, (session_id, ))

    # Commit the changes
    mydb.commit()

    # Close the cursor and connection
    my_cursor.close()
    mydb.close()


def update_session_item_by_changes(changes):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()
    for change in changes:
        update_query = f"UPDATE session_item SET `Appropriate` = %s WHERE `Session ID` = %s and `Paper ID` = %s"
        my_cursor.execute(update_query, (bool(change[2]), change[0], change[1]))
        mydb.commit()

    my_cursor.close()
    mydb.close()

