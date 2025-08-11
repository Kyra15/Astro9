from uncertainties import ufloat, umath

def find_hab_zone(lum):
    inner = umath.sqrt(lum / 1.1)
    outer = umath.sqrt(lum / 0.53)
    return inner, outer

def is_habitable(rad, inner, outer):
    if inner < rad < outer:
        return True
    return False

def radius_ok(rad):
    return 0.5 < rad < 2.0

def type_ok(type_s):
    return type_s in ["F", "G", "K", "M"]