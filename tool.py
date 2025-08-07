import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import base64
from uncertainties import ufloat, umath
import lcfunc as lcf
import func as f
import lightkurve as lk
from astropy.constants import G, M_sun, R_sun


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

tab1, tab2 = st.tabs(["Based on Values Only", "Based on Target Pixel File"])

with tab1:

    with st.form(key="vo_form", border=False, enter_to_submit=False):
        st.subheader("Input values")
        st.write("\* indicates a required input")

        st.selectbox("Star Type*", ["O", "B", "A", "F", "G", "K", "M"], key="vo_type")
        st.number_input("Planetary Radius* (km): ", key="vo_rad")
        st.number_input("Orbital Radius* (km): ", key="vo_orbrad")
        st.number_input("Orbital Period (sec): ", key="vo_per")
        st.number_input("Stellar Luminosity* (L$_☉$)", key="vo_lum")

        submitted_vo = st.form_submit_button("Submit")

    st.subheader("Output")
    
    


with tab2:

    with st.form(key="tpf_form", border=False, enter_to_submit=False):
        st.subheader("Input values")
        st.write("\* indicates a required input")

        # s_type = st.selectbox("Star Type*", ["O", "B", "A", "F", "G", "K", "M"], key="lc_type")
        
        m = st.number_input("Star Mass* (M$_☉$)", key="lc_m", format="%0.6f")
        ms = st.number_input("Mass Uncertainty (M$_☉$)", key="lc_m_sig", format="%0.6f")
        star_mass = ufloat(m, ms)

        r = st.number_input("Star Radius (R$_☉$)", key="lc_r", format="%0.4f")
        rs = st.number_input("Radius Uncertainty (R$_☉$)", key="lc_r_sig", format="%0.4f")
        star_radius = ufloat(r, rs)

        # t = st.number_input("Star Effective Temperature* (K)", key="lc_t")
        # ts = st.number_input("Temperature Uncertainty (K)", key="lc_t_sig")
        # star_temp = ufloat(t, ts)

        l = st.number_input("Stellar Luminosity* (L$_☉$)", key="lc_lum", format="%0.6f")
        ls = st.number_input("Luminosity Uncertainty (L$_☉$)", key="lc_lum_sig", format="%0.6f")
        star_lum = ufloat(l, ls)
        
        file = st.file_uploader("Upload Target Pixel File as .fits*", type="fits")

        if file:
            file.seek(0)

        submitted_lc = st.form_submit_button("Submit")



    if submitted_lc:
        if l == 0 or star_mass == 0 or not file:
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

        if 0.5 < p_radius < 1.5:
            is_rad = True
            st.write(f"Radius IS within 0.5 and 1.5 Earth Radii")
        else:
            st.write(f"Radius IS NOT within 0.5 and 1.5 Earth Radii")
            is_rad = False
        

        if is_hz and is_rad:
            st.subheader("This planet IS habitable :D")
        else:
            st.subheader("This planet IS NOT habitable :P")
        
        # will look into adding more measures of habitability (comparing with other methods liek SEPHI, ESI, PHI, etc.)

        message.empty()
