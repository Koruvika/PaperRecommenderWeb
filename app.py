import datetime
import time
from typing import Dict, List
import pandas as pd
import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from yaml.loader import SafeLoader

from utils.controller import (get_user_by_username, get_sessions_by_user_id, insert_new_session, delete_session,
                              get_papers_by_list_paper_ids_polar, update_session_item, get_papers,
                              get_papers_by_session_id, insert_new_user, get_embeddings, get_embedding_polar,
                              insert_new_paper_into_session, get_papers_by_list_paper_ids, get_paper_by_paper_id,
                              get_papers_by_text, get_paper_by_paper_id_polar, update_session_item_v2)
from utils.controller import config_file, embedding_columns
from utils.models import recommend_by_similarity, recommend_by_similarity_v2
from utils.update_configs import update_configs
from google.cloud import firestore
import polars as pl

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


def recommendation(appropriate_papers):
    if "run_recommender" not in st.session_state:
        st.session_state["run_recommender"] = False

    if st.session_state["run_recommender"]:
        if len(appropriate_papers) == 0:
            st.write("You have to add papers to the group first to make recommendations")
            return

        recommended_paper_ids, recommended_paper_similarities = recommend_by_similarity_v2(appropriate_papers,
                                                                                           embedding_columns, 30)
        recommended_papers = get_papers_by_list_paper_ids_polar(recommended_paper_ids)
        recommended_papers = recommended_papers.with_columns(
            Similarity=pl.Series(recommended_paper_similarities)).to_pandas()

        st.session_state['recommended_papers'] = recommended_papers
    else:
        if len(appropriate_papers) == 0:
            st.write("You have to add papers to the group first to make recommendations")
            return
        if "recommended_papers" in st.session_state:
            recommended_papers = st.session_state['recommended_papers']
        else:
            recommended_papers = pd.DataFrame()

    available_papers = st.session_state["current_papers"]["Paper ID"].tolist()
    # show results
    for i, row in recommended_papers.iterrows():
        paper_id = row["Paper ID"]
        if "current_papers" in st.session_state:
            if paper_id in available_papers:
                continue

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
            st.button("Add to group", key=f"rec {st.session_state['session_id']} {paper_id}", on_click=click_add_button,
                      args=(st.session_state['session_id'], paper_id, 0))
        st.divider()


def search(text_search):
    searched_papers = get_papers_by_text(text_search).sort_values(by=["Year", "Name"], ascending=False).iloc[:50]

    # show results
    available_papers = st.session_state["current_papers"]["Paper ID"].tolist()
    for index, row in searched_papers.iterrows():
        paper_id = row["Paper ID"]

        if "current_papers" in st.session_state:
            if paper_id in available_papers:
                continue
        # if "session_papers" in st.session_state:
        #     if paper_id in st.session_state["session_papers"]:
        #         continue

        # if "search_session_papers" not in st.session_state:
        #     st.session_state["search_session_papers"] = []
        # else:
        #     st.session_state["search_session_papers"].append(paper_id)

        link = "https://paperswithcode.com/paper/" + paper_id

        item_container = st.container()
        col1, col2 = item_container.columns([7, 1])
        with col1:
            st.write(f"**{row['Name']}**")
            st.write(f"Year: {int(row['Year'])}")
            st.write(f"Link: {link}")
            st.write(row["Abstract"])

        with col2:
            st.button("Add to group", key=f"search {st.session_state['session_id']} {paper_id}", on_click=click_add_button,
                      args=(st.session_state['session_id'], paper_id, 1))
        st.divider()


def click_add_button(session_id, paper_id, ros):
    # not use insert here to save time to connect database
    # insert_message = insert_new_paper_into_session(session_id, paper_id)

    # send to firebase cloud
    data = {
        "session_id": session_id,
        "appropriate_papers": [],
        "not_appropriate_papers": [],
        "result": paper_id,
        "recommend_or_search": ros
    }

    if "current_papers" in st.session_state:
        for i, row in st.session_state["current_papers"].iterrows():
            if row["Appropriate"]:
                data["appropriate_papers"].append(row["Paper ID"])
            else:
                data["not_appropriate_papers"].append(row["Paper ID"])


    # if "session_papers" in st.session_state:
    #     for idx in st.session_state["session_papers"]:
    #         if f"{session_id} {idx}" in st.session_state:
    #             if st.session_state[f"{session_id} {idx}"]:
    #                 data["appropriate_papers"].append(idx)
    #             else:
    #                 data["not_appropriate_papers"].append(idx)

    doc_ref = firebase_db.collection("tracking_data").document()
    doc_ref.set(data)

    # update session state
    if "current_papers" not in st.session_state:
        st.session_state["current_papers"] = get_papers_by_session_id(session_id)

    st.session_state["current_papers"].loc[len(st.session_state["current_papers"].index)] = {
        "Session ID": session_id,
        "Paper ID": paper_id,
        "Date": datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
        "Appropriate": 1
    }

    st.session_state["filtered_df"] = get_papers_by_list_paper_ids_polar(
        st.session_state["current_papers"]["Paper ID"].values)

    # if "session_papers" not in st.session_state:
    #     st.session_state["session_papers"] = [paper_id]
    # else:
    #     st.session_state["session_papers"].append(paper_id)

    st.session_state["run_recommender"] = False


def change_session():
    # if

    if "current_papers" in st.session_state:
        del st.session_state["current_papers"]
    if "filtered_df" in st.session_state:
        del st.session_state["filtered_df"]
    # if "session_papers" in st.session_state:
    #     del st.session_state["session_papers"]

    st.session_state["run_recommender"] = False


def submitted_add(user, sessions):
    current_session_name = st.session_state["session_option"] if "session_option" in st.session_state else None

    st.session_state["run_recommender"] = False

    insert_message = insert_new_session(st.session_state.session_name.lower().strip(), user["User ID"],
                                        sessions["Name"])
    st.toast(insert_message)
    st.session_state["sessions"] = get_sessions_by_user_id(user["User ID"])

    if current_session_name is not None:
        st.session_state["session_option"] = current_session_name


def reset_add():
    st.session_state.submitted_add = False
    st.session_state["run_recommender"] = False


def submitted_del(user):
    st.session_state["run_recommender"] = False

    delete_message = delete_session(st.session_state.delete_session_name.lower().strip(), user["User ID"])
    st.toast(delete_message)
    st.session_state["sessions"] = get_sessions_by_user_id(user["User ID"])

def reset_del():
    st.session_state["run_recommender"] = False


def change_toggle(paper_id):
    st.session_state["run_recommender"] = False
    st.session_state["run_sidebar"] = False
    if "current_papers" in st.session_state:
        st.session_state["current_papers"].loc[st.session_state["current_papers"]["Paper ID"] == paper_id, "Appropriate"] = 1 - st.session_state["current_papers"].loc[st.session_state["current_papers"]["Paper ID"] == paper_id, "Appropriate"]


def save_button_click():
    if "current_papers" not in st.session_state or "filtered_df" not in st.session_state or "session_id" not in st.session_state:
        return
    else:
        if st.session_state["current_papers"] is None:
            return
        if st.session_state["filtered_df"] is None:
            return
        if st.session_state["session_id"] is None or st.session_state["session_id"] == "":
            return
        changes = []
        for i, row in st.session_state["current_papers"].iterrows():
            paper_id = row["Paper ID"]
            is_appropriate = row["Appropriate"]
            changes.append({
                "Session ID": st.session_state["session_id"],
                "Paper ID": paper_id,
                "Date": datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),
                "Appropriate": int(is_appropriate)
            })
        # print(changes)
        update_message = update_session_item_v2(changes)
        st.toast(update_message)

    st.session_state["run_recommender"] = True


@st.cache_data(ttl=3600, show_spinner=False)
def load_database():
    # papers = get_papers()
    embeddings = get_embedding_polar()

    return embeddings


def main():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )
    update_configs(login_config_path)
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
        st.write("Switch to the tab 'Search' to search for the papers you need and add them to the paper group")
        st.write("Switch to the tab 'Recommendation' and click the button 'Save & Recommend' to make a recommendation")
        st.write(f"If you have any feedback, please contact me at 102200251@sv.dut.udn.vn")

        user = get_user_by_username(username)
        if "sessions" in st.session_state and st.session_state["sessions"] is not None:
            sessions = st.session_state["sessions"]
        else:
            sessions = get_sessions_by_user_id(user["User ID"])
            st.session_state["sessions"] = sessions



        # Paper list
        option = st.sidebar.selectbox(
            'Choose the group of papers',
            sessions["Name"],
            on_change=change_session,
            key="session_option"
        )

        # show list paper
        paper_container = st.sidebar.container(height=600)
        if len(sessions) == 0:
            print("No session for this user")
        else:
            session = sessions.loc[sessions["Name"] == option]
            st.session_state["session_id"] = session_id = session.iloc[0]["Session ID"]
            if "current_papers" not in st.session_state:
                current_papers = get_papers_by_session_id(session_id)
                st.session_state["current_papers"] = current_papers
            else:
                current_papers = st.session_state["current_papers"]
            if not current_papers.empty:
                if "filtered_df" not in st.session_state:
                    filtered_df = get_papers_by_list_paper_ids_polar(current_papers["Paper ID"].values)
                    st.session_state["filtered_df"] = filtered_df
                else:
                    filtered_df = st.session_state["filtered_df"]
            else:
                filtered_df = pl.DataFrame([])
                st.session_state["filtered_df"] = filtered_df

            for row in filtered_df.rows(named=True):
                # if "session_papers" not in st.session_state:
                #     st.session_state["session_papers"] = [row["Paper ID"]]
                # else:
                #     if row["Paper ID"] not in st.session_state["session_papers"]:
                #         st.session_state["session_papers"].append(row["Paper ID"])

                # process the properties
                paper_id = row["Paper ID"]
                paper_name = row["Name"]
                paper_abstract = row["Abstract"]

                y, mo, d, h, mi, s = current_papers.loc[current_papers["Paper ID"] == paper_id, "Date"].iloc[0].split(
                    "_")
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
                    # print(f"{paper_name}: {current_papers.loc[current_papers['Paper ID'] == paper_id, 'Appropriate'].iloc[0]}")
                    st.toggle(
                        ' ',
                        key=f"{session_id} {paper_id}",
                        value=current_papers.loc[current_papers["Paper ID"] == paper_id, "Appropriate"].iloc[0],
                        on_change=change_toggle, args=(paper_id,)
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
            if "current_papers" in st.session_state:
                for i, row in st.session_state["current_papers"].iterrows():
                    if row["Appropriate"]:
                        appropriate_papers.append(row["Paper ID"])

            # if "session_papers" in st.session_state:
            #     for paper_id in st.session_state["session_papers"]:
            #         if f"{session_id} {paper_id}" in st.session_state and st.session_state[f"{session_id} {paper_id}"]:
            #             appropriate_papers.append(paper_id)

            recommendation(appropriate_papers)

        # search tab
        with tab2:
            st.title('Scientific Paper Searching')
            text_search = st.text_input("Search paper for researching", value="")

            if text_search:
                search(text_search)

        # session utils
        st.sidebar.write("*Remember to click 'Save & Recommend' before switch to another group or refresh page*")
        col1, col2, col3 = st.sidebar.columns([3, 3, 4])

        add_session_button = col1.button('Create Group')
        delete_session_button = col2.button('Delete Group')

        col3.button('Save & Recommend', on_click=save_button_click)

        if add_session_button:
            add_expander = st.sidebar.expander('Add new group')
            add_form = add_expander.form(key="Add new session")
            add_form.text_input(label="Session Name", key="session_name")
            add_form.form_submit_button(label="Submit", on_click=submitted_add, args=(user, sessions))


        if delete_session_button:
            del_expander = st.sidebar.expander('Delete group')
            del_form = del_expander.form(key="Delete group")
            del_form.text_input(label="Session Name", key="delete_session_name")
            del_form.form_submit_button(label="Submit", on_click=submitted_del, args=(user, ))

        authenticator.logout('Logout', 'sidebar')

    elif not authentication_status:
        register(authenticator, config)
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')


if __name__ == '__main__':
    # ngrok_tunnel = ngrok.connect("localhost:8501")
    # print('Public URL:', ngrok_tunnel.public_url)
    # print(ngrok_tunnel.config)
    # print(ngrok_tunnel.pyngrok_config)
    main()
