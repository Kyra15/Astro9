import streamlit as st
import pandas as pd

import base64


@st.cache_resource()
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
      background-image: url("data:image/png;base64,%s");
      background-size: cover;
    }
    </style>
    ''' % bin_str

    st.markdown(page_bg_img, unsafe_allow_html=True)
    return


set_png_as_page_bg('background.jpg')


st.markdown(
    """
    <style>
    .stMainBlockContainer {
        background-color: #0B1D51;
        padding: 40px;
        border-radius: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("On the search for a new Earth")
st.header("Astro 9 Group 2")
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")

tab1, tab2 = st.tabs(["Based on Values Only", "Based on Lightcurves"])

with tab1:
    st.subheader("Input values")
    st.write("\* indicates a required input")
    st.number_input("Planetary Radius* (km): ", key="vo_rad")
    st.number_input("Orbital Radius* (km): ", key="vo_orbrad")
    st.number_input("Orbital Period (sec): ", key="vo_per")
    st.number_input("Stellar Luminosity* (L$_☉$)", key="vo_lum")
    st.selectbox("Star Type*", ["O", "B", "A", "F", "G", "K", "M"], key="vo_type")

with tab2:
    st.subheader("Input values")
    st.write("\* indicates a required input")
    st.number_input("Stellar Luminosity* (L$_☉$)", key="lc_lum")
    st.selectbox("Star Type*", ["O", "B", "A", "F", "G", "K", "M"], key="lc_type")
    st.file_uploader("Upload lightcurve as csv")

st.subheader("Output")
st.write("Is this planet habitable? (give probability)")

