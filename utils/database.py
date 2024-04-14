from typing import List, Dict
import mysql.connector
import yaml
from yaml.loader import SafeLoader

# TODO: path is changed between develop and deploy with docker
config_file = "configs/configs_docker.yaml"

with open(config_file) as file:
    configs = yaml.load(file, Loader=SafeLoader)

service_account_key_path = configs["service_account_key_path"]
INSTANCE_CONNECTION_NAME = str(configs["database_configs"]["INSTANCE_CONNECTION_NAME"])
DB_USER = str(configs["database_configs"]["DB_USER"])
DB_PASS = str(configs["database_configs"]["DB_PASS"])
DB_NAME = str(configs["database_configs"]["DB_NAME"])
embeddings_path = str(configs["database_configs"]["embeddings_path"])
papers_path = str(configs["database_configs"]["papers_path"])

host = INSTANCE_CONNECTION_NAME
user = DB_USER
password = DB_PASS
database = DB_NAME


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
    # print(query, value)
    my_cursor.execute(query, (value,))
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


def get_session_item_by_session_id_paper_id(session_id, paper_id):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()
    query = f"SELECT * FROM session_item WHERE `Session ID` = %s and `Paper ID` = %s"
    my_cursor.execute(query, (session_id, paper_id))
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
    my_cursor.execute(delete_query, (session_id,))

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


def update_session_item_by_change(change: Dict):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()
    update_query = f"UPDATE session_item SET `Appropriate` = %s WHERE `Session ID` = %s and `Paper ID` = %s"
    my_cursor.execute(update_query, (change["Appropriate"], change["Session ID"], change["Paper ID"]))
    mydb.commit()
    my_cursor.close()
    mydb.close()


def update_session_item_by_changes_v2(changes: List[Dict]):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    my_cursor = mydb.cursor()
    session_id = changes[0]["Session ID"]
    delete_query = f"DELETE FROM session_item WHERE `Session ID` = %s"
    my_cursor.execute(delete_query, (session_id,))
    for change in changes:
        query = f"INSERT INTO session_item (`Session ID`, `Paper ID`, `Date`, `Appropriate`) VALUES (%s, %s, %s, %s)"
        my_cursor.execute(query, (change["Session ID"], change["Paper ID"], change["Date"], change["Appropriate"]))

    mydb.commit()
    my_cursor.close()
    mydb.close()