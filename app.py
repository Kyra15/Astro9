import streamlit as st

st.set_page_config(initial_sidebar_state="collapsed")

pg = st.navigation([st.Page("tool.py", title="Habitability Tool"), st.Page("research.py", title="Research Process")])
pg.run()