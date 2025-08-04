# this is some of the most diabolically horrible code ive ever written

# import libraries
import matplotlib.pyplot as plt
import numpy as np
from uncertainties import ufloat, umath
import lcfunc as f
import pandas as pd
import lightkurve as lk
from astropy.constants import G, M_sun, R_sun


# search MAST database for WASP-18b lightcurves (limit amt returned to 1)
target_pixel = lk.search_targetpixelfile("Trappist-1")[1].download()
target_pixel.to_fits("my_tpf.fits", overwrite=True)

s_type = "M"
star_radius = ufloat(0.1192, 0.0013) # trappist 1 radii
star_mass = ufloat(0.0898, 0.0023)
star_temp = ufloat(2566, 26)
star_grav = umath.log10(((G.value * star_mass * M_sun.value)/(star_radius * R_sun.value)**2) * 100)

def main(path, s_type, s_mass=None, s_rad=None, s_grav=None):

    data = lk.read(path)

    lightcurve, values = f.finding_planet(data)
    per, t0, dur = values 

    flux, time = f.data_preprocessing(lightcurve, values)

    dip_depth, dip_sigma, dur = f.find_dip_depth(time, flux)


    star_mass, star_radius, star_grav = f.star_checks(lightcurve, s_mass, s_rad, s_grav, 
                                         s_type, star_temp)
    
    # find planet radius
    p_radius = f.find_planet_radius(dip_depth, dip_sigma, star_radius)
    print(f"radius of planet: {p_radius.n} +/- {p_radius.s}")
    # this one is the only one thats bad :(

    # find orbital period
    orb_pd = per
    print(f"orbital period (days): {orb_pd}")
    
    # find orbital radius
    orb_rad = f.find_orbital_radius(per, star_mass)
    print(f"orbital radius (AU): {orb_rad.n} +/- {orb_rad.s}")
    # must be trappist1 b!!!



if __name__ == "__main__":
    main("my_tpf.fits", s_type, star_mass, star_radius, star_grav)