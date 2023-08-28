import streamlit as st

class SessionState:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    @staticmethod
    def get(**kwargs):
        if "key" in kwargs:
            if kwargs["key"] not in st.session_state:
                st.session_state[kwargs["key"]] = SessionState(**kwargs)
            return st.session_state[kwargs["key"]]
        else:
            return SessionState(**kwargs)
