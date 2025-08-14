import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import base64
from uncertainties import ufloat, umath
import lcfunc as lcf
import func as f
import lightkurve as lk
import requests
import pandas as pd
from io import StringIO



# some css injection and cache manipulation to get a background image for the streamlit page
# not important to the project at all it just looks good
# https://discuss.streamlit.io/t/how-do-i-use-a-background-image-on-streamlit/5067
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


# start of page
st.title("On the Search for a New Earth  🪐")
st.subheader("A tool for determining habitability of exoplanets")
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")

# set tabs for tool page
tab1, tab2, tab3 = st.tabs(["Based on Values Only", "Based on Target Pixel File", "NASA Results"])

# values only tab
with tab1:

    # taking user input
    # im using the uncertainties library for everything so i can have sigma values
    with st.form(key="vo_form", border=False, enter_to_submit=False):
        st.subheader("Input values")
        st.write("\* indicates a required input")

        s_type = st.selectbox("Star Type*", ["O", "B", "A", "F", "G", "K", "M"], key="vo_type", index=4)

        r = st.number_input("Planetary Radius* (Rₑ)", key="vo_r", format="%0.4f", value=1.0)
        rs = st.number_input("Planetary Radius Uncertainty (Rₑ)", key="vo_r_sig", format="%0.4f")
        planet_radius = ufloat(r, rs)

        obr = st.number_input("Orbital Radius* (AU)", key="vo_or", format="%0.4f", value=1.0)
        obrs = st.number_input("Orbital Radius Uncertainty (AU)", key="vo_or_sig", format="%0.4f")
        orb_radius = ufloat(obr, obrs)

        t = st.number_input("Star Effective Temperature* (K)", key="vo_t", value=5780.0)
        ts = st.number_input("Temperature Uncertainty (K)", key="vo_t_sig")
        star_temp = ufloat(t, ts)

        l = st.number_input("Stellar Luminosity* (L$_☉$)", key="vo_lum", format="%0.6f", value=1.0)
        ls = st.number_input("Luminosity Uncertainty (L$_☉$)", key="vo_lum_sig", format="%0.6f")
        star_lum = ufloat(l, ls)

        submitted_vo = st.form_submit_button("Submit")


    # check if required fields are filled out
    if submitted_vo:
        if l == 0 or obr == 0 or r == 0 or t == 0:
            st.warning("Please fill out the required fields.")
            st.stop()
        
        message = st.success("Loading statistics...")

        st.subheader("Output")

        # write out results

        hz_i, hz_o = f.find_hab_zone(star_lum)

        is_rad = f.radius_ok(planet_radius)

        st.write(f"Radius of Planet (Rₑ): {planet_radius.n:.4f} +/- {planet_radius.s:.4e}<br>Fits criteria? {is_rad}", unsafe_allow_html=True)
        
        is_type = f.type_ok(s_type)

        st.write(f"Type of Star: {s_type}<br>Fits criteria? {is_type}", unsafe_allow_html=True)

        is_temp = f.temp_ok(star_temp)

        st.write(f"Star Effective Temperature (K): {star_temp.n:.4f} +/- {star_temp.s:.4e}<br>Fits criteria? {is_temp}", unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)
        is_hz = f.is_habitable(orb_radius, hz_i, hz_o)
        st.write(f"Orbital Radius (AU): {orb_radius.n:.4f} +/- {orb_radius.s:.4e}")
        st.write(f"Inner Radius of Habitable Zone (AU): {hz_i.n:.4f} +/- {hz_i.s:.4e}")
        st.write(f"Outer Radius of Habitable Zone (AU): {hz_o.n:.4f} +/- {hz_o.s:.4e}")
        st.write(f"Fits criteria? {is_hz}")

        # display final conclusion based on all previous checks
        if is_hz and is_rad and is_type and is_temp:
            st.subheader("This planet IS habitable")
        else:
            st.subheader("This planet IS NOT habitable")

        message.empty()
        
    
    

# lightcurve tab!
with tab2:

    # take in user input
    # same thing here, im using the uncertainties library for more statistical flexibility
    with st.form(key="tpf_form", border=False, enter_to_submit=False):

        st.subheader("Input values")
        st.write("\* indicates a required input")

        s_type = st.selectbox("Star Type*", ["O", "B", "A", "F", "G", "K", "M"], key="lc_type", index=6)
        
        m = st.number_input("Star Mass* (M$_☉$)", key="lc_m", format="%0.6f", value=0.0898)
        ms = st.number_input("Mass Uncertainty (M$_☉$)", key="lc_m_sig", format="%0.6f", value=0.0023)
        star_mass = ufloat(m, ms)

        r = st.number_input("Star Radius (R$_☉$)", key="lc_r", format="%0.4f", value=0.1192)
        rs = st.number_input("Radius Uncertainty (R$_☉$)", key="lc_r_sig", format="%0.4f", value=0.0013)
        star_radius = ufloat(r, rs)

        t = st.number_input("Star Effective Temperature* (K)", key="lc_t", value=2566.0)
        ts = st.number_input("Temperature Uncertainty (K)", key="lc_t_sig", value=26.0)
        star_temp = ufloat(t, ts)

        l = st.number_input("Stellar Luminosity* (L$_☉$)", key="lc_lum", format="%0.6f", value=0.000522)
        ls = st.number_input("Luminosity Uncertainty (L$_☉$)", key="lc_lum_sig", format="%0.6f", value=0.000022)
        star_lum = ufloat(l, ls)
        
        file = st.file_uploader("Upload Target Pixel File as .fits*", type="fits")

        if file:
            file.seek(0)

        submitted_lc = st.form_submit_button("Submit")


    # checking if required fields have been filled out
    if submitted_lc:
        if l == 0 or m == 0 or not file or t == 0:
            st.warning("Please fill out the required fields.")
            st.stop()
        
        message = st.success("Loading statistics...")

        with open("temp_tpf.fits", "wb") as fi:
            fi.write(file.getbuffer())

        # reading the target pixel file
        data = lk.read("temp_tpf.fits")

        # find the planet with a func from my other code
        lightcurve, values = lcf.finding_planet(data)
        per, t0, dur = values 

        # do a bit of preprocessing with splines and curve fitting 
        flux, time = lcf.data_preprocessing(lightcurve, values)

        # find the dip with tls
        dip_depth, dip_sigma, dur, plot_vals = lcf.find_dip_depth(time, flux)

        # plot everything
        x1, y1, x2, y2 = plot_vals

        fig, ((ax1), (ax2)) = plt.subplots(2, 1)
        ax1.plot(time, flux)
        ax1.set_title("Smoothed and Folded Lightcurve")
        ax1.set_xlabel("Phase")
        ax1.set_ylabel("Relative Flux")

        ax2.scatter(x2, y2, s=2)
        ax2.plot(x1, y1, color='red')
        ax2.set_title("Dip fitted with TLS")
        ax2.set_xlabel("Phase")
        ax2.set_ylabel("Relative Flux")

        fig.tight_layout()

        st.pyplot(fig)

        # print output results
        st.subheader("Output")

        # find orbital radius
        orb_rad = lcf.find_orbital_radius(per, star_mass)

        # find hab zone
        hz_i, hz_o = f.find_hab_zone(star_lum)

        # find planet radius
        p_radius = lcf.find_planet_radius(dip_depth, dip_sigma, star_radius)

        # write out results
        is_rad = f.radius_ok(planet_radius)

        st.write(f"Radius of Planet (Rₑ): {p_radius.n:.4f} +/- {p_radius.s:.4e}<br>Fits criteria? {is_rad}", unsafe_allow_html=True)
        
        is_type = f.type_ok(s_type)

        st.write(f"Type of Star: {s_type}<br>Fits criteria? {is_type}", unsafe_allow_html=True)

        is_temp = f.temp_ok(star_temp)

        st.write(f"Star Effective Temperature (K): {star_temp.n:.4f} +/- {star_temp.s:.4e}<br>Fits criteria? {is_temp}", unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)

        st.write(f"Orbital Radius (AU): {orb_rad.n:.4f} +/- {orb_rad.s:.4e}")
        st.write(f"Inner Radius of Habitable Zone (AU): {hz_i.n:.4f} +/- {hz_i.s:.4e}")
        st.write(f"Outer Radius of Habitable Zone (AU): {hz_o.n:.4f} +/- {hz_o.s:.4e}")
        is_hz = f.is_habitable(orb_rad, hz_i, hz_o)
        st.write(f"Fits criteria? {is_hz}")
        
        # print result based on previous criteria
        if is_hz and is_rad and is_type and is_temp:
            st.subheader("This planet IS habitable")
        else:
            st.subheader("This planet IS NOT habitable")

        message.empty()
    
# nasa exoplanet archive tab
with tab3:
    # my sql query (im just more used to this form of sql)
    sql_statement = '''SELECT pl_name,hostname,pl_rade,pl_orbper,st_teff,st_spectype,st_lum FROM pscomppars WHERE pl_rade between 0.5 and 2.0 and st_teff between 4800 and 6300 and (upper(st_spectype) like 'F%' or upper(st_spectype) like 'G%' or upper(st_spectype) like 'K%' or upper(st_spectype) like 'M%')'''
    
    # turn into a TAP query
    web_statement = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=" + sql_statement.replace(" ", "+") + "&format=csv"

    # define headers for request (i get an SLS error otherwise)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }

    # get the csv from the website
    response = requests.get(web_statement, headers=headers)

    # read and convert to dataframe
    df = pd.read_csv(StringIO(response.text))


    # do some conversions for different axises
    df["Stellar Luminosity [Ls]"] = 10 ** df["st_lum"]

    df = df.drop("st_lum", axis=1)
    
    df["pl_orbper"] = (df["pl_orbper"] / 365) ** (2/3)

    # add some columns for easier use and visualization
    df["Habitable Zone Inner Radius [AU]"] = np.sqrt(df["Stellar Luminosity [Ls]"] / 1.1)

    df["Habitable Zone Outer Radius [AU]"] = np.sqrt(df["Stellar Luminosity [Ls]"] / 0.53)

    df = df.rename(columns={'pl_name': 'Planet Name', 'hostname': 'Host Star Name', 'pl_rade': 'Planet Radius [Rₑ]', 'pl_orbper': 'Orbital Radius [AU]', 'st_teff': 'Star Effective Temperature [K]', 'st_spectype': 'Spectral Types'})

    df = df[['Planet Name', 'Host Star Name', 'Planet Radius [Rₑ]', 'Orbital Radius [AU]', 'Habitable Zone Inner Radius [AU]', 'Habitable Zone Outer Radius [AU]', 'Star Effective Temperature [K]', 'Spectral Types']]

    # filter to find rows that fit all criteria
    hab_df = df[(0.95 * df["Habitable Zone Inner Radius [AU]"] < df["Orbital Radius [AU]"]) & (df["Orbital Radius [AU]"] < 1.05 * df["Habitable Zone Outer Radius [AU]"])]

    df_nh = df.drop(hab_df.index)

    hab_df = hab_df.reset_index(drop=True)

    # filter to find other rows that almost fit
    near_hab_df = df_nh[(0.85 * df_nh["Habitable Zone Inner Radius [AU]"] < df_nh["Orbital Radius [AU]"]) & (df_nh["Orbital Radius [AU]"] < 1.15 * df_nh["Habitable Zone Outer Radius [AU]"])]

    near_hab_df = near_hab_df.reset_index(drop=True)

    # write output
    st.subheader("Output")

    st.write("Table of Habitable Planets (within 5\% error)")
    st.dataframe(hab_df)

    st.write("Table of Planets Near the Habitable Zone (within 15\% error)")
    st.dataframe(near_hab_df)

    st.write("Full Table of Potential Exoplanets without Habitable Zone Calculations")
    st.dataframe(df)
