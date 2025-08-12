from uncertainties import ufloat, umath

# find hab zone based off of hw fomulas
def find_hab_zone(lum):
    inner = umath.sqrt(lum / 1.1)
    outer = umath.sqrt(lum / 0.53)
    return inner, outer

# find if within zone
def is_habitable(rad, inner, outer):
    if inner < rad < outer:
        return True
    return False

# checks if radius within our limits
def radius_ok(rad):
    return 0.5 <= rad <= 2.0

# checks if the type is within our approved types
def type_ok(type_s):
    return type_s in ["F", "G", "K", "M"]

# checks if temp is within our temp range
def temp_ok(temp):
    return 4800 <= temp <= 6300

