import streamlit as st

pg = st.navigation([st.Page("tool.py", title="Habitability Tool"), st.Page("research.py", title="Research Process")])
pg.run()