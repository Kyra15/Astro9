import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
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
        height: fit-content;
    }

    .stAppHeader {
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)



st.title("On the Search for a New Earth  🪐")
st.subheader("A tool for determining habitability of exoplanets")
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
    st.file_uploader("Upload Lightcurve as .csv*")

    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax.plot(x, y)
    ax.set_title("Sine Wave")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")

    st.pyplot(fig)


st.subheader("Output")
st.write("statistics")
