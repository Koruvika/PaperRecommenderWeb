DB_NAME = "pseudo_database"
user_sql_path = "/home/duong/dumps/users.sql"
papers_sql_path = "/home/duong/dumps/papers.sql"
session_sql_path = "/home/duong/dumps/sessions.sql"
session_item_sql_path = "/home/duong/dumps/session_item.sql"
lines = []

with open(user_sql_path, "r") as f:
    lines += f.readlines()

with open(papers_sql_path, "r") as f:
    lines += f.readlines()

with open(session_sql_path, "r") as f:
    lines += f.readlines()

with open(session_item_sql_path, "r") as f:
    lines += f.readlines()




with open("./init_db.sql", "w") as f:
    f.close()

with open("./init_db.sql", "a") as f:
    f.write(f"use {DB_NAME};\n")
    for line in lines:
        f.write(line)
        f.write("\n")



print("debug")
