import datetime
from typing import List, Dict

import numpy as np
import polars as pl
import pandas as pd
import uuid
from .database import (get_items_by_column_value, insert_session_into_sessions, get_items_from_table,
                       delete_session_by_session_id, delete_session_item_by_session_id, get_sessions_by_name_user_id,
                       update_session_item_by_changes, insert_user_into_users, insert_paper_into_session, update_session_item_by_changes_v2,
                       get_items_by_column_values, get_items_by_column_contain_text, get_session_item_by_session_id_paper_id, update_session_item_by_change)
from .database import config_file, embeddings_path, papers_path
import streamlit as st


paper_columns = ["Paper ID", "Name", "Year", "Abstract"]
session_columns = ["Session ID", "Name", "User ID"]
embedding_columns = ["Paper ID"] + [str(i) for i in range(384)]
user_columns = ["User ID", "Username", "Password", "Name", "Email"]
session_paper_columns = ["Session ID", "Paper ID", "Date", "Appropriate"]


@st.cache_data(ttl=3600, show_spinner=False)
def get_user_by_username(username: str) -> dict:
    users = get_items_by_column_value("users", "Username", username)
    if len(users) == 0:
        return dict()
    else:
        return {
            "User ID": users[0][0],
            "Username": users[0][1],
            "Name": users[0][3],
            "Email": users[0][4]

        }


# @st.cache_data(show_spinner=False)
def get_sessions_by_user_id(user_id: str) -> pd.DataFrame:
    sessions = get_items_by_column_value("sessions", "User ID", user_id)
    results = pd.DataFrame(sessions, columns=session_columns)

    return results


def get_sessions() -> pd.DataFrame:
    results = get_items_from_table("sessions")
    results = pd.DataFrame(results, columns=session_columns)
    return results


@st.cache_data(ttl=3600, show_spinner=False)
def get_papers() -> pd.DataFrame:
    results = get_items_from_table("papers")
    results = pd.DataFrame(results, columns=paper_columns)
    return results


@st.cache_data(show_spinner=False)
def get_papers_polar() -> pl.DataFrame:
    results = pl.read_csv(papers_path)
    results = results.select(paper_columns)
    return results


@st.cache_data(ttl=3600, show_spinner=False)
def get_embeddings() -> pd.DataFrame:
    results = get_items_from_table("embeddings")
    results = pd.DataFrame(results, columns=embedding_columns)
    return results


@st.cache_data(show_spinner=False)
def get_embedding_polar() -> pl.DataFrame:
    results = pl.read_csv(embeddings_path)
    results = results.select(embedding_columns)
    return results


@st.cache_data(ttl=3600, show_spinner=False)
def get_users() -> pd.DataFrame:
    results = get_items_from_table("users")
    results = pd.DataFrame(results, columns=user_columns)
    return results


def get_papers_by_session_id(session_id: str) -> pd.DataFrame:
    results = get_items_by_column_value("session_item", "Session ID", session_id)
    results = pd.DataFrame(results, columns=session_paper_columns)
    # TODO: Update condition later
    if results["Appropriate"].dtype not in [np.int32, np.int64]:
        results["Appropriate"] = results["Appropriate"].apply(ord)
    return results


@st.cache_data(ttl=3600, show_spinner=False)
def get_papers_by_list_paper_ids(list_paper_ids: List[str]) -> pd.DataFrame:
    results = get_items_by_column_values("papers", "Paper ID", list_paper_ids)
    results = pd.DataFrame(results, columns=paper_columns)
    return results


@st.cache_data(show_spinner=False)
def get_papers_by_list_paper_ids_polar(list_paper_ids: List[str]) -> pl.DataFrame:
    results = get_papers_polar()
    results = results.filter(pl.col("Paper ID").is_in(list_paper_ids))
    return results


@st.cache_data(show_spinner=False)
def get_paper_by_paper_id(paper_id: str) -> dict:
    paper = get_items_by_column_value("papers", "Paper ID", paper_id)
    if len(paper) == 0:
        return dict()
    else:
        return {
            "Paper ID": paper[0][0],
            "Name": paper[0][1],
            "Year": paper[0][2],
            "Abstract": paper[0][3],

        }


@st.cache_data(show_spinner=False)
def get_paper_by_paper_id_polar(paper_id: str) -> dict:
    papers = get_papers_by_list_paper_ids_polar([paper_id])
    return papers.row(0, named=True)


@st.cache_data(ttl=3600, show_spinner=False)
def get_papers_by_text(text_search: str) -> pd.DataFrame:
    text_search = text_search.strip().lower()
    results = get_items_by_column_contain_text("papers", "Name", text_search)
    results = pd.DataFrame(results, columns=paper_columns)
    return results


@st.cache_data(show_spinner=False)
def get_papers_by_text_polar(text_search: str) -> pl.DataFrame:
    text_search = text_search.strip().lower()
    results = get_papers_polar()
    results = results.filter(results["Name"].str.contains(text_search))
    return results


def insert_new_session(name: str, user_id: str, session_names=None) -> str:
    sessions = get_sessions()

    if session_names is None:
        if name in sessions["Name"]:
            return "Name is exist"
    else:
        if name in session_names:
            return "Name is exist"

    session_id = uuid.uuid4()
    while session_id in sessions["Session ID"]:
        session_id = uuid.uuid4()

    try:
        insert_session_into_sessions(str(session_id), name, user_id)
        return "Inserted new session successfully"
    except Exception as e:
        return "Error while inserting new session: " + str(e)


def insert_new_user(name: str, email: str, username: str, password: str) -> (str, str):
    users = get_users()

    user_id = uuid.uuid4()
    while user_id in users["User ID"]:
        user_id = uuid.uuid4()

    try:
        insert_user_into_users(str(user_id), name, email, username, password)
        return "Inserted new user successfully", str(user_id)
    except Exception as e:
        return "Error while inserting new user: " + str(e), ""


def insert_new_paper_into_session(session_id: str, paper_id: str) -> str:
    now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    try:
        insert_paper_into_session(session_id, paper_id, now, True)
        return "Paper successfully inserted into session"
    except Exception as e:
        return "Error while inserting new paper: " + str(e)


def delete_session(name: str, user_id: str) -> str:
    try:
        sessions = get_sessions_by_name_user_id(name, user_id)
        if len(sessions) == 0:
            return "Session does not exist"
        session_id = sessions[0][0]

        delete_session_item_by_session_id(session_id)
        delete_session_by_session_id(session_id)
        return "Deleted session successfully"
    except Exception as e:
        return "Error while deleting session: " + str(e)


def update_session_item(changes):
    try:
        update_session_item_by_changes(changes)
        return "Updated session item successfully"
    except Exception as e:
        return "Error while updating session item: " + str(e)


def update_session_item_v2(changes: List[Dict]):

    try:
        update_session_item_by_changes_v2(changes)
        # for change in changes:
        #     session_id = change["Session ID"]
        #     paper_id = change["Paper ID"]
        #     dt = change["Date"]
        #     appropriate = change["Appropriate"]
        #     session_item = get_session_item_by_session_id_paper_id(session_id, paper_id)
        #     if len(session_item) > 0:  # exists
        #         update_session_item_by_change(change)
        #     else:  # not exists
        #         insert_paper_into_session(session_id, paper_id, dt, appropriate)
        return "Updated session item successfully"
    except Exception as e:
        return "Error while updating session item: " + str(e)
