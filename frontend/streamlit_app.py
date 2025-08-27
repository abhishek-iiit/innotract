import streamlit as st
import requests
import os

BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Chatbot")
st.title("Requirement Assistant")

if "session_id" not in st.session_state:
    st.session_state.session_id=None
if "messages" not in st.session_state:
    st.session_state.messages=[]

user_id=st.sidebar.text_input("User ID","u1")
if st.sidebar.button("New Chat"):
    r=requests.post(f"{BACKEND}/session/new",json={"user_id":user_id})
    if r.status_code==200:
        sid=r.json()["session_id"]
        st.session_state.session_id=sid
        st.session_state.messages=[]
    else:
        st.error(f"Error creating session: {r.status_code}")

if st.session_state.session_id:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.write(m["content"])
    if q:=st.chat_input("Your message"):
        st.session_state.messages.append({"role":"user","content":q})
        with st.chat_message("user"): st.write(q)
        r=requests.post(f"{BACKEND}/chat",json={"user_id":user_id,"session_id":st.session_state.session_id,"message":q})
        if r.status_code==200:
            data=r.json()
            msg=data["messages"][0]["content"]
            st.session_state.messages.append({"role":"assistant","content":msg})
            with st.chat_message("assistant"): st.write(msg)
        else:
            error_msg = f"Error {r.status_code}"
            try:
                error_detail = r.json().get("detail", r.text)
                error_msg += f": {error_detail}"
            except:
                error_msg += f": {r.text}"
            st.error(error_msg)
