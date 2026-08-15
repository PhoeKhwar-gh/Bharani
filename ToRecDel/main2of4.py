import swisseph as swe

# Constants
SID_METHOD = swe.SIDM_LAHIRI  # Ayanamsa method

def to_dms(deg):
    """Convert decimal degrees to DMS format."""
    deg_int = int(deg)
    min_part = (deg - deg_int) * 60
    mins = int(min_part)
    secs = (min_part - mins) * 60
    return f"{deg_int}°{mins:02d}'{secs:07.4f}\""

def to_hms(hour):
    """Convert decimal hours to HMS format."""
    h = int(hour)
    m = int((hour - h) * 60)
    s = int(((hour - h) * 60 - m) * 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def main():
    # Input data:
    year = 2026
    month = 2
    day = 13
    longitude = 80 + 17 / 60.0   # Chennai
    latitude = 13 + 5 / 60.0
    hour = 7 + 30 / 60.0 - 5.5   # IST

    # Create SweDate object
    jd_ut = swe.julday(year, month, day, hour, swe.GREG_CAL)

    # Set sidereal mode:
    swe.set_sid_mode(SID_METHOD)

    # Print input details
    print(f"Date (YYYY/MM/DD): {year}/{month}/{day}, {to_hms(hour)}")
    print(f"Jul. day:  {jd_ut}")
    print(f"DeltaT:    {swe.deltat(jd_ut) * 24 * 3600:.2f} sec.")
    print(f"Location:  {to_dms(abs(longitude))}{'E' if longitude > 0 else 'W'} / "
          f"{to_dms(abs(latitude))}{'N' if latitude > 0 else 'S'}")

    # Get ayanamsa
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    print(f"Ayanamsa:  {to_dms(ayanamsa)} ({swe.get_ayanamsa_name(SID_METHOD)})")

    # Calculate houses
    cusps, ascmc = swe.houses(jd_ut, latitude, longitude, b'P')
    asc_deg = ascmc[0]
    asc_sign = int(asc_deg // 30) + 1
    print(f"Ascendant: {to_dms(asc_deg)}\n")

    # Planets to calculate
    planets = [
        swe.SUN, swe.MOON, swe.MARS, swe.MERCURY,
        swe.JUPITER, swe.VENUS, swe.SATURN, swe.TRUE_NODE
    ]

    flags = (
        swe.FLG_SWIEPH |
        swe.FLG_SIDEREAL |
        swe.FLG_NONUT |
        swe.FLG_SPEED
    )

    for planet_id in planets:
        name = swe.get_planet_name(planet_id)
        res, retflags = swe.calc_ut(jd_ut, planet_id, flags)

        if not res:
            print(f"Error calculating {name}")
            continue

        lon = res[0]
        speed_lon = res[3]

        sign_num = int(lon // 30) + 1
        house_pos = (sign_num + 12 - asc_sign) % 12 + 1
        retro = 'R' if speed_lon < 0 else 'D'

        pos_in_sign = lon % 30

        print(f"{name:<12}: {to_dms(lon)} {retro}; sign: {sign_num:2}; {to_dms(pos_in_sign)} in house {house_pos:2}")

    # Ketu (opposite of Rahu/True Node)
    rahu_res, _ = swe.calc_ut(jd_ut, swe.TRUE_NODE, flags)
    ketu_lon = (rahu_res[0] + 180) % 360
    sign_num_k = int(ketu_lon // 30) + 1
    house_pos_k = (sign_num_k + 12 - asc_sign) % 12 + 1
    retro_k = 'R' if rahu_res[3] < 0 else 'D'
    pos_in_sign_k = ketu_lon % 30

    print(f"{'Ketu (true)':<12}: {to_dms(ketu_lon)} {retro_k}; sign: {sign_num_k:2}; {to_dms(pos_in_sign_k)} in house {house_pos_k:2}")

if __name__ == "__main__":
    main()
