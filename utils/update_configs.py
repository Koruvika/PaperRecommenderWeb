import yaml
from .controller import get_users


def update_configs(login_config_file):
    with open(login_config_file, 'r') as f:
        login_config = yaml.load(f, Loader=yaml.SafeLoader)

    users = get_users()

    for i, row in users.iterrows():
        login_config["credentials"]["usernames"][row["Username"]] = {
            "name": row["Name"],
            "email": row["Email"],
            "password": row["Password"],
            "failed_login_attempts": 0,
            "logged_in": False
        }

    with open(login_config_file, 'w') as f:
        yaml.dump(login_config, f)


