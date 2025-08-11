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

tab1, tab2, tab3 = st.tabs(["Based on Values Only", "Based on Target Pixel File", "NASA Results"])

with tab1:

    with st.form(key="vo_form", border=False, enter_to_submit=False):
        st.subheader("Input values")
        st.write("\* indicates a required input")

        s_type = st.selectbox("Star Type*", ["O", "B", "A", "F", "G", "K", "M"], key="vo_type")

        r = st.number_input("Planetary Radius (R$_E$)", key="vo_r", format="%0.4f")
        rs = st.number_input("Planetary Radius Uncertainty (R$_E$)", key="vo_r_sig", format="%0.4f")
        planet_radius = ufloat(r, rs)

        obr = st.number_input("Orbital Radius (AU)", key="vo_or", format="%0.4f")
        obrs = st.number_input("Orbital Radius Uncertainty (AU)", key="vo_or_sig", format="%0.4f")
        orb_radius = ufloat(obr, obrs)

        t = st.number_input("Star Effective Temperature* (K)", key="vo_t")
        ts = st.number_input("Temperature Uncertainty (K)", key="vo_t_sig")
        star_temp = ufloat(t, ts)

        l = st.number_input("Stellar Luminosity* (L$_☉$)", key="vo_lum", format="%0.6f")
        ls = st.number_input("Luminosity Uncertainty (L$_☉$)", key="vo_lum_sig", format="%0.6f")
        star_lum = ufloat(l, ls)

        submitted_vo = st.form_submit_button("Submit")


    if submitted_vo:
        if l == 0 or obr == 0 or r == 0 or t == 0:
            st.warning("Please fill out the required fields.")
            st.stop()
        
        message = st.success("Loading statistics...")

        st.subheader("Output")

        st.write(f"Orbital Radius (AU): {orb_radius.n:.4f} +/- {orb_radius.s:.4e}")

        hz_i, hz_o = f.find_hab_zone(star_lum)
        st.write(f"Inner Radius of Habitable Zone (AU): {hz_i.n:.4f} +/- {hz_i.s:.4e}")
        st.write(f"Outer Radius of Habitable Zone (AU): {hz_o.n:.4f} +/- {hz_o.s:.4e}")

        is_hz = f.is_habitable(orb_radius, hz_i, hz_o)

        st.write(f"Radius of Planet: {planet_radius.n:.4f} +/- {planet_radius.s:.4e}")

        is_rad = f.radius_ok(planet_radius)
        
        is_type = f.type_ok(s_type)

        is_temp = f.temp_ok(star_temp)

        if is_hz and is_rad and is_type and is_temp:
            st.subheader("This planet IS habitable :D")
        else:
            st.subheader("This planet IS NOT habitable :P")

        message.empty()
        
    
    


with tab2:

    with st.form(key="tpf_form", border=False, enter_to_submit=False):
        st.subheader("Input values")
        st.write("\* indicates a required input")

        s_type = st.selectbox("Star Type*", ["O", "B", "A", "F", "G", "K", "M"], key="lc_type")
        
        m = st.number_input("Star Mass* (M$_☉$)", key="lc_m", format="%0.6f")
        ms = st.number_input("Mass Uncertainty (M$_☉$)", key="lc_m_sig", format="%0.6f")
        star_mass = ufloat(m, ms)

        r = st.number_input("Star Radius (R$_☉$)", key="lc_r", format="%0.4f")
        rs = st.number_input("Radius Uncertainty (R$_☉$)", key="lc_r_sig", format="%0.4f")
        star_radius = ufloat(r, rs)

        t = st.number_input("Star Effective Temperature* (K)", key="lc_t")
        ts = st.number_input("Temperature Uncertainty (K)", key="lc_t_sig")
        star_temp = ufloat(t, ts)

        l = st.number_input("Stellar Luminosity* (L$_☉$)", key="lc_lum", format="%0.6f")
        ls = st.number_input("Luminosity Uncertainty (L$_☉$)", key="lc_lum_sig", format="%0.6f")
        star_lum = ufloat(l, ls)
        
        file = st.file_uploader("Upload Target Pixel File as .fits*", type="fits")

        if file:
            file.seek(0)

        submitted_lc = st.form_submit_button("Submit")



    if submitted_lc:
        if l == 0 or m == 0 or not file or t == 0:
            st.warning("Please fill out the required fields.")
            st.stop()
        
        message = st.success("Loading statistics...")

        with open("temp_tpf.fits", "wb") as fi:
            fi.write(file.getbuffer())

        # if star_mass and star_radius:
        #     star_grav = umath.log10(((G.value * star_mass * M_sun.value)/(star_radius * R_sun.value)**2) * 100)

        data = lk.read("temp_tpf.fits")

        lightcurve, values = lcf.finding_planet(data)
        per, t0, dur = values 

        flux, time = lcf.data_preprocessing(lightcurve, values)

        dip_depth, dip_sigma, dur = lcf.find_dip_depth(time, flux)


        # star_mass, star_radius, star_grav = f.star_checks(lightcurve, star_mass, star_radius, 
        #                                                   star_grav, s_type, star_temp)
        

        st.subheader("Output")

        # find orbital period
        # orb_pd = per
        # st.write(f"orbital period (days): {orb_pd:.4f}")
        
        # find orbital radius
        orb_rad = lcf.find_orbital_radius(per, star_mass)
        st.write(f"Orbital Radius (AU): {orb_rad.n:.4f} +/- {orb_rad.s:.4e}")

        hz_i, hz_o = f.find_hab_zone(star_lum)
        st.write(f"Inner Radius of Habitable Zone (AU): {hz_i.n:.4f} +/- {hz_i.s:.4e}")
        st.write(f"Outer Radius of Habitable Zone (AU): {hz_o.n:.4f} +/- {hz_o.s:.4e}")

        is_hz = f.is_habitable(orb_rad, hz_i, hz_o)

        # find planet radius
        p_radius = lcf.find_planet_radius(dip_depth, dip_sigma, star_radius)
        st.write(f"Radius of Planet: {p_radius.n:.4f} +/- {p_radius.s:.4e}")
        # this one is the only one thats bad :(

        is_rad = f.radius_ok(p_radius)

        is_type = f.type_ok(s_type)

        is_temp = f.temp_ok(star_temp)
        

        if is_hz and is_rad and is_type and is_temp:
            st.subheader("This planet IS habitable :D")
        else:
            st.subheader("This planet IS NOT habitable :P")
        
        # will look into adding more measures of habitability (comparing with other methods liek SEPHI, ESI, PHI, etc.)

        message.empty()
    
with tab3:
    sql_statement = '''SELECT pl_name,hostname,pl_rade,pl_orbper,st_teff,st_spectype,st_lum FROM pscomppars WHERE pl_rade between 0.5 and 2.0 and st_teff between 4800 and 6300 and (upper(st_spectype) like 'F%' or upper(st_spectype) like 'G%' or upper(st_spectype) like 'K%' or upper(st_spectype) like 'M%')'''
    
    web_statement = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=" + sql_statement.replace(" ", "+") + "&format=csv"

    # st.write(web_statement)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }

    response = requests.get(web_statement, headers=headers)

    df = pd.read_csv(StringIO(response.text))


    df["Stellar Luminosity [Ls]"] = 10 ** df["st_lum"]

    df = df.drop("st_lum", axis=1)
    
    df["pl_orbper"] = (df["pl_orbper"] / 365) ** (2/3)

    df["Habitable Zone Inner Radius [AU]"] = np.sqrt(df["Stellar Luminosity [Ls]"] / 1.1)

    df["Habitable Zone Outer Radius [AU]"] = np.sqrt(df["Stellar Luminosity [Ls]"] / 0.53)

    df = df.rename(columns={'pl_name': 'Planet Name', 'hostname': 'Host Star Name', 'pl_rade': 'Planet Radius [Re]', 'pl_orbper': 'Orbital Radius [AU]', 'st_teff': 'Star Effective Temperature [K]', 'st_spectype': 'Spectral Types'})

    df = df[['Planet Name', 'Host Star Name', 'Planet Radius [Re]', 'Orbital Radius [AU]', 'Habitable Zone Inner Radius [AU]', 'Habitable Zone Outer Radius [AU]', 'Star Effective Temperature [K]', 'Spectral Types']]

    hab_df = df[(0.95 * df["Habitable Zone Inner Radius [AU]"] < df["Orbital Radius [AU]"]) & (df["Orbital Radius [AU]"] < 1.05 * df["Habitable Zone Outer Radius [AU]"])]

    df_nh = df.drop(hab_df.index)

    hab_df = hab_df.reset_index(drop=True)

    near_hab_df = df_nh[(0.85 * df_nh["Habitable Zone Inner Radius [AU]"] < df_nh["Orbital Radius [AU]"]) & (df_nh["Orbital Radius [AU]"] < 1.15 * df_nh["Habitable Zone Outer Radius [AU]"])]

    near_hab_df = near_hab_df.reset_index(drop=True)

    st.subheader("Output")

    st.write("Table of Habitable Planets (within 5\% error)")
    st.dataframe(hab_df)

    st.write("Table of Planets Near the Habitable Zone (within 15\% error)")
    st.dataframe(near_hab_df)

    st.write("Full Table of Potential Exoplanets without Habitable Zone Calculations")
    st.dataframe(df)
