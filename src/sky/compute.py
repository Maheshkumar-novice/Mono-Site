"""Compute tonight's visible stars and planets from Tamil Nadu."""

import math
from datetime import datetime, timedelta, timezone
from skyfield.api import load, Star, wgs84
from skyfield.data import hipparcos
from skyfield.magnitudelib import planetary_magnitude

LAT = 11.0
LON = 79.0
LOCATION_NAME = "Tamil Nadu, India"

IST = timezone(timedelta(hours=5, minutes=30))

STAR_NAMES = {
    7588: 'Achernar', 11767: 'Polaris', 21421: 'Aldebaran',
    24436: 'Rigel', 24608: 'Capella', 25336: 'Bellatrix',
    26311: 'Alnilam', 26727: 'Alnitak', 27366: 'Saiph',
    27989: 'Betelgeuse', 30438: 'Canopus', 31681: 'Wezen',
    32349: 'Sirius', 33579: 'Adhara', 34444: 'Miaplacidus',
    36850: 'Alhena', 37279: 'Procyon', 37826: 'Pollux',
    39953: 'Naos', 42913: 'Alphard', 44816: 'Alsuhail',
    46390: 'Avior', 49669: 'Regulus', 54061: 'Alioth',
    57632: 'Denebola', 59803: 'Muhlifain', 60718: 'Acrux',
    61084: 'Gacrux', 62434: 'Mimosa', 62956: 'Mizar',
    65474: 'Spica', 68702: 'Hadar',
    69673: 'Arcturus', 71683: 'Rigil Kentaurus (α Centauri A)', 71681: 'Alpha Centauri B',
    76267: 'Kaus Australis', 80763: 'Antares', 84012: 'Shaula',
    85927: 'Sargas', 86032: 'Kaus Media', 90185: 'Nunki',
    91262: 'Vega', 97649: 'Altair', 100751: 'Peacock',
    102098: 'Deneb', 107315: 'Fomalhaut', 109268: 'Alnair',
}

STAR_INFO = {
    'Sirius': {'color': '#aaccff', 'desc': 'Brightest star in the night sky, in Canis Major'},
    'Canopus': {'color': '#ffffcc', 'desc': 'Second brightest star, in Carina'},
    'Arcturus': {'color': '#ffcc88', 'desc': 'Red giant in Boötes, 4th brightest star'},
    'Rigil Kentaurus': {'color': '#ffffcc', 'desc': 'Closest star system to Earth, in Centaurus'},
    'Rigil Kentaurus (α Centauri A)': {'color': '#ffffcc', 'desc': 'Closest star system to Earth, brightest of the pair'},
    'Alpha Centauri B': {'color': '#ffcc88', 'desc': 'Companion to Alpha Centauri A, in Centaurus'},
    'Toliman': {'color': '#ffcc88', 'desc': 'Alpha Centauri B, companion to Rigil Kentaurus'},
    'Vega': {'color': '#aaccff', 'desc': 'Bright blue star in Lyra, former pole star'},
    'Capella': {'color': '#ffffcc', 'desc': 'Yellow giant in Auriga'},
    'Rigel': {'color': '#aaccff', 'desc': 'Blue supergiant, Orion\'s left foot'},
    'Procyon': {'color': '#ffffee', 'desc': 'In Canis Minor, 8th brightest star'},
    'Betelgeuse': {'color': '#ff8844', 'desc': 'Red supergiant, Orion\'s right shoulder — may go supernova'},
    'Altair': {'color': '#ffffff', 'desc': 'In Aquila, part of the Summer Triangle'},
    'Aldebaran': {'color': '#ff8844', 'desc': 'Red giant, the eye of Taurus the Bull'},
    'Antares': {'color': '#ff6644', 'desc': 'Red supergiant, heart of Scorpius — rival of Mars'},
    'Spica': {'color': '#aaccff', 'desc': 'Blue giant in Virgo'},
    'Pollux': {'color': '#ffcc88', 'desc': 'Brightest star in Gemini'},
    'Fomalhaut': {'color': '#aaccff', 'desc': 'Lonely bright star in Piscis Austrinus'},
    'Deneb': {'color': '#ffffff', 'desc': 'Distant supergiant in Cygnus, part of the Summer Triangle'},
    'Regulus': {'color': '#aaccff', 'desc': 'Heart of Leo the Lion'},
    'Acrux': {'color': '#aaccff', 'desc': 'Brightest star in the Southern Cross'},
    'Mimosa': {'color': '#aaccff', 'desc': 'Second brightest in the Southern Cross'},
    'Gacrux': {'color': '#ff8844', 'desc': 'Red giant in the Southern Cross'},
    'Hadar': {'color': '#aaccff', 'desc': 'Blue giant in Centaurus, pointer to the Southern Cross'},
    'Achernar': {'color': '#aaccff', 'desc': 'Flattest known star, in Eridanus'},
    'Bellatrix': {'color': '#aaccff', 'desc': 'Orion\'s left shoulder'},
    'Alnilam': {'color': '#aaccff', 'desc': 'Middle star of Orion\'s Belt'},
    'Polaris': {'color': '#ffffcc', 'desc': 'The North Star, in Ursa Minor'},
    'Jupiter': {'color': '#ffeecc', 'desc': 'Largest planet, visible to the naked eye'},
    'Venus': {'color': '#ffffee', 'desc': 'Brightest planet, the morning/evening star'},
    'Mars': {'color': '#ff8866', 'desc': 'The Red Planet'},
    'Saturn': {'color': '#ffddaa', 'desc': 'Ringed planet, visible to the naked eye'},
    'Mercury': {'color': '#dddddd', 'desc': 'Smallest planet, close to the Sun'},
}


def get_night_hours():
    """Get observation times for 24 hours starting from 6 PM IST."""
    now = datetime.now(IST)
    today = now.date()
    if now.hour < 6:
        today -= timedelta(days=1)

    times = []
    for hour in range(18, 42):  # 6 PM today to 5 PM next day
        h = hour % 24
        day = today if hour < 24 else today + timedelta(days=1)
        times.append(datetime(day.year, day.month, day.day, h, 0, tzinfo=IST))
    return times


def is_dark_hour(dt):
    """Check if an hour is dark enough for stargazing (before 6 AM or after 7 PM)."""
    return dt.hour >= 19 or dt.hour < 6


def compute_moon_phase(eph, ts, t):
    """Compute moon phase as percentage illumination and phase name."""
    sun = eph['sun']
    moon = eph['moon']
    earth = eph['earth']

    e = earth.at(t)
    s = e.observe(sun).apparent()
    m = e.observe(moon).apparent()

    # Elongation angle between sun and moon
    elongation = s.separation_from(m)
    phase_angle = 180 - elongation.degrees

    # Illumination percentage
    illumination = round((1 + math.cos(math.radians(phase_angle))) / 2 * 100, 1)

    # Phase name
    if illumination < 3:
        name = 'New Moon'
        emoji = '🌑'
    elif illumination < 25:
        name = 'Waxing Crescent'
        emoji = '🌒'
    elif illumination < 45:
        name = 'First Quarter'
        emoji = '🌓'
    elif illumination < 75:
        name = 'Waxing Gibbous'
        emoji = '🌔'
    elif illumination < 97:
        name = 'Waning Gibbous' if phase_angle < 0 else 'Full Moon'
        emoji = '🌕'
    else:
        name = 'Full Moon'
        emoji = '🌕'

    # Check if waning (moon past full)
    # Simple check: compute moon position tomorrow
    t2 = ts.from_datetime(t.utc_datetime() + timedelta(hours=24))
    e2 = earth.at(t2)
    s2 = e2.observe(sun).apparent()
    m2 = e2.observe(moon).apparent()
    elong2 = s2.separation_from(m2)
    if elong2.degrees < elongation.degrees and illumination > 50:
        if illumination >= 97:
            name = 'Full Moon'
            emoji = '🌕'
        elif illumination >= 75:
            name = 'Waning Gibbous'
            emoji = '🌖'
        elif illumination >= 45:
            name = 'Last Quarter'
            emoji = '🌗'
        elif illumination >= 25:
            name = 'Waning Crescent'
            emoji = '🌘'

    # Visibility impact
    if illumination > 75:
        impact = 'Bright moonlight — faint stars harder to see'
    elif illumination > 40:
        impact = 'Moderate moonlight — some impact on faint stars'
    else:
        impact = 'Dark sky — great conditions for stargazing'

    return {
        'illumination': illumination,
        'name': name,
        'emoji': emoji,
        'impact': impact,
    }


def compute_sky():
    ts = load.timescale()
    eph = load('de421.bsp')
    earth = eph['earth']
    observer = earth + wgs84.latlon(LAT, LON)

    night_hours = get_night_hours()
    t_list = [ts.from_datetime(dt) for dt in night_hours]
    hour_labels = [dt.strftime('%I %p').lstrip('0') for dt in night_hours]

    results = {}

    # --- Planets ---
    planet_names = {
        'mercury': 'Mercury',
        'venus': 'Venus',
        'mars': 'Mars',
        'jupiter barycenter': 'Jupiter',
        'saturn barycenter': 'Saturn',
    }

    for key, name in planet_names.items():
        body = eph[key]
        best_alt = -90
        best_data = None
        positions = []

        for t, dt in zip(t_list, night_hours):
            astrometric = observer.at(t).observe(body)
            apparent = astrometric.apparent()
            alt, az, _ = apparent.altaz()

            dark = is_dark_hour(dt)
            pos = {'alt': round(alt.degrees, 1), 'az': round(az.degrees, 1), 'visible': bool(alt.degrees > 5), 'dark': dark}
            positions.append(pos)

            if alt.degrees > best_alt and dark:
                best_alt = alt.degrees
                try:
                    mag = round(float(planetary_magnitude(astrometric)), 1)
                except Exception:
                    mag = '?'
                info = STAR_INFO.get(name, {})
                best_data = {
                    'name': name,
                    'type': 'Planet',
                    'magnitude': mag,
                    'altitude': round(alt.degrees, 1),
                    'azimuth': round(az.degrees, 1),
                    'direction': az_to_direction(az.degrees),
                    'best_time': dt.strftime('%I %p').lstrip('0'),
                    'color': info.get('color', '#ffffcc'),
                    'desc': info.get('desc', ''),
                    'positions': positions,
                }

        # If no dark-hour peak found, pick overall best (daytime visibility)
        if best_alt < -80 and best_data is None:
            for t, dt in zip(t_list, night_hours):
                astrometric = observer.at(t).observe(body)
                apparent = astrometric.apparent()
                alt, az, _ = apparent.altaz()
                if alt.degrees > best_alt:
                    best_alt = alt.degrees
                    try:
                        mag = round(float(planetary_magnitude(astrometric)), 1)
                    except Exception:
                        mag = '?'
                    info = STAR_INFO.get(name, {})
                    best_data = {
                        'name': name, 'type': 'Planet', 'magnitude': mag,
                        'altitude': round(alt.degrees, 1), 'azimuth': round(az.degrees, 1),
                        'direction': az_to_direction(az.degrees),
                        'best_time': dt.strftime('%I %p').lstrip('0'),
                        'color': info.get('color', '#ffffcc'), 'desc': info.get('desc', ''),
                        'positions': positions,
                    }

        if best_alt > 5 and best_data:
            results[name] = best_data

    # --- Stars (Hipparcos) ---
    with load.open(hipparcos.URL) as f:
        df = hipparcos.load_dataframe(f)

    bright = df[df['magnitude'] < 2.0]

    for hip_id, row in bright.iterrows():
        star = Star(ra_hours=row['ra_hours'], dec_degrees=row['dec_degrees'])
        name = STAR_NAMES.get(hip_id, f'HIP {hip_id}')

        best_alt = -90
        best_data = None
        positions = []

        for t, dt in zip(t_list, night_hours):
            astrometric = observer.at(t).observe(star)
            apparent = astrometric.apparent()
            alt, az, _ = apparent.altaz()

            dark = is_dark_hour(dt)
            pos = {'alt': round(alt.degrees, 1), 'az': round(az.degrees, 1), 'visible': bool(alt.degrees > 10), 'dark': dark}
            positions.append(pos)

            if alt.degrees > best_alt and dark:
                best_alt = alt.degrees
                info = STAR_INFO.get(name, {})
                best_data = {
                    'name': name,
                    'type': 'Star',
                    'magnitude': round(float(row['magnitude']), 1),
                    'altitude': round(alt.degrees, 1),
                    'azimuth': round(az.degrees, 1),
                    'direction': az_to_direction(az.degrees),
                    'best_time': dt.strftime('%I %p').lstrip('0'),
                    'color': info.get('color', '#e5e5e5'),
                    'desc': info.get('desc', ''),
                    'positions': positions,
                }

        if best_alt > 10 and best_data:
            if name not in results or float(best_data['magnitude']) < float(results[name].get('magnitude', 99)):
                results[name] = best_data

    # Sort by brightness
    result_list = list(results.values())
    result_list.sort(key=lambda x: float(x['magnitude']) if isinstance(x['magnitude'], (int, float)) else 99)

    top20 = result_list[:20]

    # Moon phase at midnight
    mid_idx = len(t_list) // 2
    moon = compute_moon_phase(eph, ts, t_list[mid_idx])

    return top20, moon, hour_labels


def az_to_direction(az):
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    idx = round(az / 22.5) % 16
    return dirs[idx]
