from streamlit_authenticator import Authenticate
import streamlit as st
import yaml
from yaml.loader import SafeLoader

config_file = "configs/config.yaml"


def main():
    with open(config_file) as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    # reset password
    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"]):
                with open(config_file, 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)


if __name__ == "__main__":
    main()
