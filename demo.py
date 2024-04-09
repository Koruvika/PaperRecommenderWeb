import sqlalchemy
from google.cloud.sql.connector import Connector
import os

service_account_key_path = "/home/duong/angular-land-419708-ae255fcab897.json"
INSTANCE_CONNECTION_NAME = "angular-land-419708:asia-southeast1:paper-recommender-system"
DB_USER = "duongdhk"
DB_PASS = "12345678"
DB_NAME = "paper_recommender_db"

# Replace with the path to your service account key file
os.environ["GOOGLE_APPLICATION_ CREDENTIALS"] = service_account_key_path

# initialize Connector object
connector = Connector()


# function to return the database connection object
def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pymysql",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn


# create connection pool with 'creator' argument to our connection object function
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

# connect to connection pool
with pool.connect() as db_conn:
    # commit transactions
    db_conn.commit()

    # query and fetch ratings table
    results = db_conn.execute(sqlalchemy.text("SELECT * FROM users")).fetchall()

    # show results
    for row in results:
        print(row)
