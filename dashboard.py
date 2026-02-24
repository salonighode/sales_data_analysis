import streamlit as st

st.set_page_config(page_title="Sales BI Tool", layout="wide")

# ----------------------
# SIMPLE LOGIN SYSTEM
# ----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Sales Intelligence Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Credentials ❌")

if not st.session_state.logged_in:
    login()
    st.stop()

st.title("🏠 Welcome to Sales Intelligence System")
st.write("Use the sidebar to navigate between pages.")