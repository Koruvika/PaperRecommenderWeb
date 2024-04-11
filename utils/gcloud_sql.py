from typing import List, Dict
import sqlalchemy
from google.cloud.sql.connector import Connector
import os
import yaml
from yaml import SafeLoader

config_file = "configs/configs.yaml"

with open(config_file) as file:
    configs = yaml.load(file, Loader=SafeLoader)

service_account_key_path = configs["service_account_key_path"]
INSTANCE_CONNECTION_NAME = str(configs["database_configs"]["INSTANCE_CONNECTION_NAME"])
DB_USER = str(configs["database_configs"]["DB_USER"])
DB_PASS = str(configs["database_configs"]["DB_PASS"])
DB_NAME = str(configs["database_configs"]["DB_NAME"])
embeddings_path = str(configs["database_configs"]["embeddings_path"])
papers_path = str(configs["database_configs"]["papers_path"])

# Replace with the path to your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_key_path

# initialize Connector object
connector = Connector()


# function to return the database connection object
def get_connection():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pymysql",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn


def get_items_by_column_contain_text(table, column, text):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )
    with pool.connect() as conn:
        conn.commit()

        query = f"SELECT * FROM {table} WHERE LOWER(`{column}`) LIKE '%{text}%'"
        results = conn.execute(sqlalchemy.text(query)).fetchall()

    return results


def get_items_by_column_value(table, column, value):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )
    with pool.connect() as conn:
        conn.commit()

        query = f"SELECT * FROM {table} WHERE `{column}` = :value"
        params = {
            "value": value
        }
        results = conn.execute(sqlalchemy.text(query), params).fetchall()

    return results


def get_items_by_column_values(table: str, column: str, values: List[str]):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )
    with pool.connect() as conn:
        conn.commit()

        placeholder_str = ','.join([':value{}'.format(i) for i in range(len(values))])
        query = f"SELECT * FROM {table} WHERE `{column}` IN ({placeholder_str})"

        params = {f"value{i}": value for i, value in enumerate(values)}

        results = conn.execute(sqlalchemy.text(query), params).fetchall()

    return results


def get_sessions_by_name_user_id(name, user_id):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )
    with pool.connect() as conn:
        query = f"SELECT * FROM sessions WHERE `Name` = :name and `User ID` = :user_id"
        params = {
            "name": name,
            "user_id": user_id
        }
        results = conn.execute(sqlalchemy.text(query), params).fetchall()

    return results


def get_session_item_by_session_id_paper_id(session_id, paper_id):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )
    with pool.connect() as conn:
        query = f"SELECT * FROM session_item WHERE `Session ID` = :session_id and `Paper ID` = :paper_id"
        params = {
            "session_id": session_id,
            "paper_id": paper_id
        }
        results = conn.execute(sqlalchemy.text(query), params).fetchall()

    return results



def get_items_from_table(table):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )
    with pool.connect() as conn:
        query = f"SELECT * FROM {table}"
        results = conn.execute(sqlalchemy.text(query)).fetchall()

    return results


def insert_session_into_sessions(session_id, name, user_id):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )
    with pool.connect() as conn:
        query = f"INSERT INTO sessions (`Session ID`, `Name`, `User ID`) VALUES (:session_id, :name, :user_id)"
        params = {
            "session_id": session_id,
            "name": name,
            "user_id": user_id
        }

        conn.execute(sqlalchemy.text(query), params)
        conn.commit()


def insert_user_into_users(user_id, name, email, username, user_password):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )
    with pool.connect() as conn:
        query = f"INSERT INTO users (`User ID`, `Name`, `Email`, `Username`, `Password`) VALUES (:user_id, :name, :email, :username, :user_password)"
        params = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "username": username,
            "user_password": user_password
        }

        conn.execute(sqlalchemy.text(query), params)
        conn.commit()


def insert_paper_into_session(session_id, paper_id, dt, appropriate):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )

    with pool.connect() as conn:
        query = f"INSERT INTO session_item (`Session ID`, `Paper ID`, `Date`, `Appropriate`) VALUES (:session_id, :paper_id, :dt, :appropriate)"
        params = {
            "session_id": session_id,
            "paper_id": paper_id,
            "dt": dt,
            "appropriate": 1 if appropriate else 0
        }
        conn.execute(sqlalchemy.text(query), params)
        conn.commit()


def delete_session_by_session_id(session_id):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )

    with pool.connect() as conn:
        query = f"DELETE FROM sessions WHERE `Session ID` = :session_id"
        params = {
            "session_id": session_id
        }
        conn.execute(sqlalchemy.text(query), params)
        conn.commit()


def delete_session_item_by_session_id(session_id):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )

    with pool.connect() as conn:
        query = f"DELETE FROM session_item WHERE `Session ID` = :session_id"
        params = {
            "session_id": session_id
        }
        conn.execute(sqlalchemy.text(query), params)
        conn.commit()


def update_session_item_by_changes(changes):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )
    with pool.connect() as conn:
        for change in changes:
            query = f"UPDATE session_item SET `Appropriate` = :appropriate WHERE `Session Id` = :session_id AND `Paper ID` = :paper_id"
            params = {
                "appropriate": (change[2]),
                "session_id": change[0],
                "paper_id": change[1]
            }
            conn.execute(sqlalchemy.text(query), params)
            conn.commit()


def update_session_item_by_change(change: Dict):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )
    with pool.connect() as conn:
        query = f"UPDATE session_item SET `Appropriate` = :appropriate WHERE `Session Id` = :session_id AND `Paper ID` = :paper_id"
        params = {
            "session_id": change["Session ID"],
            "paper_id": change["Paper ID"],
            # "date": change["Date"],
            "appropriate": change["Appropriate"],
        }
        conn.execute(sqlalchemy.text(query), params)
        conn.commit()


def update_session_item_by_changes_v2(changes: List[Dict]):
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=get_connection,
    )
    with pool.connect() as conn:
        session_id = changes[0]["Session ID"]
        delete_query = f"DELETE FROM session_item WHERE `Session ID` = :session_id"
        params = {"session_id": session_id}
        conn.execute(sqlalchemy.text(delete_query), params)
        # conn.commit()
        for change in changes:
            query = f"INSERT INTO session_item (`Session ID`, `Paper ID`, `Date`, `Appropriate`) VALUES (:session_id, :paper_id, :dt, :appropriate)"
            params = {
                "session_id": change["Session ID"],
                "paper_id": change["Paper ID"],
                "dt": change["Date"],
                "appropriate": change["Appropriate"],
            }
            conn.execute(sqlalchemy.text(query), params)
            # conn.commit()
        conn.commit()


if __name__ == "__main__":
    delete_session_by_session_id("test_session_id_1")
