# import libraries
from uncertainties import ufloat
from scipy.signal import medfilt
from transitleastsquares import transitleastsquares
import matplotlib.pyplot as plt
import numpy as np
from astropy.constants import G, M_sun, R_earth, au, R_sun
from astropy import units as u


# use lightkurve to look for the max period amplitude and fold around it (would be a planet)
# returns period, time, and duration of dip (the transit)
def finding_planet(data):

    lc = data.to_lightcurve(method="pld").remove_outliers().flatten()
    
    bls = lc.to_periodogram(method="bls")
    
    pd = bls.period_at_max_power
    t0 = bls.transit_time_at_max_power
    dur = bls.duration_at_max_power

    lc = lc.fold(period=pd, epoch_time=t0)

    lc.scatter()
    plt.show()
    return lc, (pd.value, t0.value, dur.value)


# smoothing the data using a moving average
def data_preprocessing(lc, values):

    flux = lc.flux.value
    time = lc.time.value
    
    # apply a moving average    
    flux_smoothed = medfilt(flux, 25)
    flux_smoothed = flux_smoothed[12:-12]
    flux_smoothed /= np.median(flux_smoothed)
    time_trimmed = time[12:-12]

    return flux_smoothed, time_trimmed


# finding the dip and stats using transit least squares
def find_dip_depth(time, flux):
    # https://github.com/hippke/tls/blob/master/tutorials/02%20Starter's%20guide%20-%20K2-3b%2C%20a%20red%20dwarf%20with%20a%20planet.ipynb
    model = transitleastsquares(time, flux)
    results = model.power(oversampling_factor=5, duration_grid_step=1.02)

    depth = 1 - results.depth

    return depth, results.transit_depths_uncertainties, results.duration, (results.model_folded_phase, results.model_folded_model, results.folded_phase, results.folded_y)


# find planet radius from these dip values
def find_planet_radius(dip, dip_sig, s_rad):
    # https://www.youtube.com/watch?v=urIKWm3AB-4&t=220s
    # the relationship: delta flux = r_p ** 2 / r_s ** 2
    # so r_p = r_star * sqrt(delta flux)
    # trappist 1 radii is 0.121 solar radii
    dip_depth = ufloat(dip, dip_sig)
    s_rad_m = s_rad * R_sun.value
    radius_in_sol = s_rad_m * (dip_depth ** 0.5)
    return radius_in_sol / R_earth.value

# find orbital radius based on the period and stellar mass
def find_orbital_radius(pd_d, s_mass):
    mass = s_mass * M_sun.value
    pd = pd_d * 86400
    orb_rad = (((pd ** 2 * G.value * mass)/(4 * np.pi**2))**(1/3)) / au.value
    return orb_rad
