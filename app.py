import datetime

import pandas as pd
import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from yaml.loader import SafeLoader

from utils.controller import (get_user_by_username, get_sessions_by_user_id, insert_new_session, delete_session,
                              update_session_item, get_papers, get_papers_by_session_id, insert_new_user, get_embeddings,
                              insert_new_paper_into_session, get_papers_by_list_paper_ids, get_paper_by_paper_id, get_papers_by_text)
from utils.controller import config_file
from utils.models import recommend_by_similarity
from google.cloud import firestore


# configs
with open(config_file) as file:
    configs = yaml.load(file, Loader=SafeLoader)

# login configs
login_config_path = configs['login_config']
# firebase secret key
fb_key_path = configs['firebase_configs']['secret_key_path']
with open(fb_key_path) as f:
    secret_key = yaml.load(f, Loader=SafeLoader)
firebase_db = firestore.Client.from_service_account_info(secret_key)


def register(authenticator, config):
    # register
    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user \
            = authenticator.register_user("sidebar", pre_authorization=False)
        if email_of_registered_user:
            # write to config
            with open(login_config_path, 'w') as fl:
                yaml.dump(config, fl, default_flow_style=False)

            # syn config to db
            password = config["credentials"]['usernames'][username_of_registered_user].get("password")
            register_message, user_id = insert_new_user(name_of_registered_user, email_of_registered_user,
                                                        username_of_registered_user, password)

            # create default session
            insert_message = insert_new_session("default", user_id)

            st.toast(register_message)
            st.toast(insert_message)

    except Exception as e:
        st.error(e)


def recommendation(appropriate_papers, embeddings, embedding_columns, session_id):
    recommended_papers = []
    recommended_paper_ids, recommended_paper_similarities = recommend_by_similarity(appropriate_papers, embeddings,
                                                                                    embedding_columns, 30)
    for idx, similarity in zip(recommended_paper_ids, recommended_paper_similarities):
        paper = get_paper_by_paper_id(idx)
        if len(paper.keys()) != 0:
            paper["Similarity"] = similarity
            recommended_papers.append(paper)
    recommended_papers = pd.DataFrame(recommended_papers)
    recommended_papers.insert(0, "Appropriate", False)

    # show results
    for _, (index, row) in enumerate(recommended_papers.iterrows()):
        paper_id = row["Paper ID"]

        if "session_papers" in st.session_state:
            if paper_id in st.session_state["session_papers"]:
                continue

        if "rec_session_papers" not in st.session_state:
            st.session_state["rec_session_papers"] = []
        else:
            st.session_state["rec_session_papers"].append(paper_id)

        link = "https://paperswithcode.com/paper/" + paper_id

        item_container = st.container()
        col1, col2 = item_container.columns([7, 1])
        with col1:
            st.write(f"**{row['Name']}**")
            st.write(f"Score: {row['Similarity']}")
            st.write(f"Year: {int(row['Year'])}")
            st.write(f"Link: {link}")
            st.write(row["Abstract"])

        with col2:
            add_button = st.button("Add to session", key=f"rec {session_id} {paper_id}", on_click=click_add_button,
                                   args=(session_id, paper_id, 0))
        st.divider()


def search(text_search, session_id):
    searched_papers = get_papers_by_text(text_search).iloc[:50]

    # show results
    for index, row in searched_papers.iterrows():
        paper_id = row["Paper ID"]

        if "session_papers" in st.session_state:
            if paper_id in st.session_state["session_papers"]:
                continue

        if "search_session_papers" not in st.session_state:
            st.session_state["search_session_papers"] = []
        else:
            st.session_state["search_session_papers"].append(paper_id)

        link = "https://paperswithcode.com/paper/" + paper_id

        item_container = st.container()
        col1, col2 = item_container.columns([7, 1])
        with col1:
            st.write(f"**{row['Name']}**")
            st.write(f"Year: {int(row['Year'])}")
            st.write(f"Link: {link}")
            st.write(row["Abstract"])

        with col2:
            add_button = st.button("Add to session", key=f"search {session_id} {paper_id}", on_click=click_add_button,
                                   args=(session_id, paper_id, 1))
        st.divider()


def click_add_button(session_id, paper_id, ros):
    insert_message = insert_new_paper_into_session(session_id, paper_id)

    data = {
        "session_id": session_id,
        "appropriate_papers": [],
        "not_appropriate_papers": [],
        "result": paper_id,
        "recommend_or_search": ros
    }

    if "session_papers" in st.session_state:
        for idx in st.session_state["session_papers"]:
            if f"{session_id} {idx}" in st.session_state:
                if st.session_state[f"{session_id} {idx}"]:
                    data["appropriate_papers"].append(idx)
                else:
                    data["not_appropriate_papers"].append(idx)

    doc_ref = firebase_db.collection("tracking_data").document()
    doc_ref.set(data)

    if "session_papers" not in st.session_state:
        st.session_state["session_papers"] = [paper_id]
    else:
        st.session_state["session_papers"].append(paper_id)


def change_session():
    if "session_papers" in st.session_state:
        del st.session_state["session_papers"]


def submitted_add():
    st.session_state.submitted_add = True


def reset_add():
    st.session_state.submitted_add = False


def submitted_del():
    st.session_state.submitted_del = True


def reset_del():
    st.session_state.submitted_del = False


@st.cache_data(ttl=3600, show_spinner=False)
def load_database():
    # papers = get_papers()
    embeddings = get_embeddings()
    embedding_columns = [str(i) for i in range(0, 384)]

    return embeddings, embedding_columns


def main():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )
    with open(login_config_path) as fl:
        config = yaml.load(fl, Loader=SafeLoader)

    authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    name, authentication_status, username = authenticator.login()
    if authentication_status:

        st.write(f'Welcome *{name}*')
        st.write(f"If you have any feedback, please contact me at duongdanghuynhkhanh@gmail.com")
        user = get_user_by_username(username)
        sessions = get_sessions_by_user_id(user["User ID"])

        embeddings, embedding_columns = load_database()

        # Paper list
        option = st.sidebar.selectbox(
            'Choose the working session',
            sessions["Name"],
            on_change=change_session
        )

        # show list paper
        paper_container = st.sidebar.container(height=600)
        current_papers, filtered_df, session_id = None, None, None
        if len(sessions) == 0:
            print("No session for this user")
        else:
            session = sessions.loc[sessions["Name"] == option]
            session_id = session.iloc[0]["Session ID"]
            current_papers = get_papers_by_session_id(session_id)
            if not current_papers.empty:
                filtered_df = get_papers_by_list_paper_ids(current_papers["Paper ID"].values)

            else:
                filtered_df = pd.DataFrame([])

            for index, row in filtered_df.iterrows():
                if "session_papers" not in st.session_state:
                    st.session_state["session_papers"] = [row["Paper ID"]]
                else:
                    if row["Paper ID"] not in st.session_state["session_papers"]:
                        st.session_state["session_papers"].append(row["Paper ID"])

                # process the properties
                paper_id = row["Paper ID"]
                paper_name = row["Name"]
                paper_abstract = row["Abstract"]

                y, mo, d, h, mi, s = current_papers.loc[current_papers["Paper ID"] == paper_id, "Date"].iloc[0].split("_")
                delta_time = (datetime.datetime.now() -
                              datetime.datetime(int(y), int(mo), int(d), int(h), int(mi), int(s)))

                if delta_time.days >= 1:
                    delta_time = str(delta_time.days) + " day"
                else:
                    seconds = delta_time.seconds
                    minutes = int(seconds / 60)
                    hours = int(minutes / 60)

                    if hours >= 1:
                        delta_time = str(hours) + " hour"
                    else:
                        if minutes >= 1:
                            delta_time = str(minutes) + " minute"
                        else:
                            delta_time = "now"

                item_container = paper_container.container()
                col1, col2 = item_container.columns([1, 6])
                with col1:
                    st.toggle(
                        ' ',
                        key=f"{session_id} {paper_id}",
                        value=bool(current_papers.loc[current_papers["Paper ID"] == paper_id, "Appropriate"].iloc[0]),
                    )
                    st.write(f"*{delta_time}*")
                with col2:
                    st.write(f"**{paper_name}**")
                    st.write(paper_abstract)
        # main tabs
        tab1, tab2 = st.tabs(["Recommendation", "Search"])

        # recommendation tab
        with tab1:
            st.title('Scientific Paper Recommendation')

            # filter appropriate session papers
            appropriate_papers = []
            if "session_papers" in st.session_state:
                for paper_id in st.session_state["session_papers"]:
                    if f"{session_id} {paper_id}" in st.session_state and st.session_state[f"{session_id} {paper_id}"]:
                        appropriate_papers.append(paper_id)

            if len(appropriate_papers) == 0:
                st.toast("No papers were found in the session")
            else:
                # run recommender
                recommendation(appropriate_papers, embeddings, embedding_columns, session_id)

        # search tab
        with tab2:
            st.title('Scientific Paper Searching')
            text_search = st.text_input("Search paper for researching", value="")

            if text_search:
                search(text_search, session_id)


        # session utils
        col1, col2, col3 = st.sidebar.columns(3)

        add_session_button = col1.button('append session')
        delete_session_button = col2.button('delete session')
        save_session_button = col3.button('save and reload')

        if add_session_button:
            add_expander = st.sidebar.expander('Add new session')
            add_form = add_expander.form(key="Add new session")
            add_form.text_input(label="Session Name", key="session_name")
            add_form.form_submit_button(label="Submit", on_click=submitted_add)

        if 'submitted_add' in st.session_state:
            if st.session_state.submitted_add:
                insert_message = insert_new_session(st.session_state.session_name, user["User ID"], sessions["Name"])
                st.toast(insert_message)
                reset_add()

        if delete_session_button:
            del_expander = st.sidebar.expander('Delete session')
            del_form = del_expander.form(key="Delete new session")
            del_form.text_input(label="Session Name", key="delete_session_name")
            del_form.form_submit_button(label="Submit", on_click=submitted_del)

        if 'submitted_del' in st.session_state:
            if st.session_state.submitted_del:
                delete_message = delete_session(st.session_state.delete_session_name, user["User ID"])
                st.toast(delete_message)
                reset_del()

        if save_session_button:
            if current_papers is not None and filtered_df is not None:
                changes = []
                for _, (index, row) in enumerate(filtered_df.iterrows()):
                    paper_id = row["Paper ID"]
                    is_appropriate = st.session_state[f"{session_id} {paper_id}"]
                    changes.append([session_id, paper_id, int(is_appropriate),
                                    datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")])

                update_message = update_session_item(changes)
                st.toast(update_message)

        authenticator.logout('logout', 'sidebar')

    elif not authentication_status:
        register(authenticator, config)
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')


if __name__ == '__main__':
    main()
