# Tonight's Sky — How It Works

An astronomy page that computes the top 20 brightest stars and planets visible from Tamil Nadu, India. Rebuilt daily by a cron job. No external APIs — all calculations done locally using astronomical libraries.

## Table of Contents

- [Overview](#overview)
- [How Star Positions Are Computed](#how-star-positions-are-computed)
  - [The Observer](#the-observer)
  - [Altitude and Azimuth](#altitude-and-azimuth)
  - [Converting RA/Dec to Alt/Az](#converting-radec-to-altaz)
- [How Stars Are Selected](#how-stars-are-selected)
  - [The Hipparcos Catalog](#the-hipparcos-catalog)
  - [Planets](#planets)
  - [Brightness and Magnitude](#brightness-and-magnitude)
- [How the 24-Hour Window Works](#how-the-24-hour-window-works)
- [How Moon Phase Is Computed](#how-moon-phase-is-computed)
- [How the Sky Map Works](#how-the-sky-map-works)
  - [Mapping Alt/Az to Pixels](#mapping-altaz-to-pixels)
  - [Time Slider](#time-slider)
- [Star Colors and Types](#star-colors-and-types)
- [Architecture](#architecture)
- [Key Concepts for Beginners](#key-concepts-for-beginners)

---

## Overview

Every time the build runs, the sky module:

1. Loads a planetary ephemeris (`de421.bsp`) — a table of planet positions over centuries
2. Loads the Hipparcos star catalog (`hip_main.dat`) — 118,218 stars measured by the ESA satellite
3. For each hour from 6 PM to 5 PM (24 hours), computes where every bright star and planet appears in the sky from Tamil Nadu
4. Picks the top 20 brightest objects that are above the horizon during dark hours
5. Computes the moon phase and its impact on visibility
6. Renders everything into a static HTML page with an interactive sky map

---

## How Star Positions Are Computed

### The Observer

Everything starts with **where you are** on Earth. We define the observer's position using latitude and longitude:

```python
LAT = 11.0   # Tamil Nadu, degrees north of the equator
LON = 79.0   # degrees east of the Prime Meridian
observer = earth + wgs84.latlon(LAT, LON)
```

The same star appears in different positions depending on where you stand. Sirius might be overhead in Tamil Nadu but barely visible from London at the same time.

### Altitude and Azimuth

Stars are located using two angles:

- **Altitude (Alt)**: How high above the horizon (0° = horizon, 90° = directly overhead, called the "zenith")
- **Azimuth (Az)**: Compass direction (0° = North, 90° = East, 180° = South, 270° = West)

```
        N (0°)
        |
W (270°) --- Zenith --- E (90°)
        |
        S (180°)
```

A star at altitude 45° and azimuth 90° is halfway up the sky, looking due east.

### Converting RA/Dec to Alt/Az

Stars in catalogs are stored in **Right Ascension (RA)** and **Declination (Dec)** — a coordinate system fixed to the stars, not the Earth. Think of it like longitude and latitude but for the sky.

The conversion from RA/Dec to Alt/Az depends on:
- Your location on Earth (latitude/longitude)
- The current time (Earth's rotation changes which stars are overhead)
- The date (Earth's orbit changes which stars are visible at night)

This is what Skyfield does for us:

```python
astrometric = observer.at(time).observe(star)
apparent = astrometric.apparent()
alt, az, distance = apparent.altaz()
```

The `.observe()` call accounts for the star's actual position. The `.apparent()` call adds atmospheric refraction (the atmosphere bends light, making stars appear slightly higher than they are). The `.altaz()` converts to the local coordinate system.

---

## How Stars Are Selected

### The Hipparcos Catalog

The [Hipparcos catalog](https://en.wikipedia.org/wiki/Hipparcos) was created by the European Space Agency's Hipparcos satellite (1989-1993). It measured precise positions of 118,218 stars. Each star has an ID (HIP number), position (RA/Dec), and apparent magnitude.

We filter to stars brighter than magnitude 2.0:

```python
bright = df[df['magnitude'] < 2.0]
```

This gives us about 45-50 stars — the brightest naked-eye stars. Many have familiar names (Sirius, Rigel, Vega, etc.) which we map from HIP IDs:

```python
STAR_NAMES = {
    32349: 'Sirius',      # HIP 32349
    24436: 'Rigel',       # HIP 24436
    91262: 'Vega',        # HIP 91262
    ...
}
```

### Planets

Planets aren't in the Hipparcos catalog — they move relative to the stars. Their positions come from a **planetary ephemeris** (`de421.bsp`), a file created by NASA's Jet Propulsion Laboratory that encodes the orbits of all solar system bodies.

```python
jupiter = eph['jupiter barycenter']
astrometric = observer.at(time).observe(jupiter)
```

We track Mercury, Venus, Mars, Jupiter, and Saturn — the five planets visible to the naked eye.

### Brightness and Magnitude

Astronomers measure brightness using **apparent magnitude** — a logarithmic scale where **lower = brighter**:

| Object | Magnitude |
|---|---|
| Sun | -26.7 |
| Full Moon | -12.7 |
| Venus (at brightest) | -4.6 |
| Sirius (brightest star) | -1.46 |
| Faintest naked-eye star | ~6.0 |

Each step of 1 magnitude = 2.5× difference in brightness. So Sirius (mag -1.46) is about 10× brighter than Vega (mag 0.03).

Planet magnitudes change as their distance from Earth varies:

```python
mag = planetary_magnitude(astrometric)
```

This Skyfield function calculates the apparent magnitude based on the planet's current distance and phase angle (how much of its lit side faces us).

---

## How the 24-Hour Window Works

We compute positions for every hour from 6 PM to 5 PM the next day:

```python
for hour in range(18, 42):  # 18 = 6 PM, 41 = 5 PM next day
    h = hour % 24
    ...
```

For each object, we track its position at every hour. The **best viewing time** is the hour during dark hours (7 PM - 5 AM) when the object reaches its highest altitude.

```python
def is_dark_hour(dt):
    return dt.hour >= 19 or dt.hour < 6
```

Daytime hours are still computed so the time slider can show where objects are during the day — they're just marked as "not visible to naked eye" since the Sun drowns them out.

---

## How Moon Phase Is Computed

The moon phase depends on the angle between the Sun and Moon as seen from Earth:

```python
elongation = sun_position.separation_from(moon_position)
phase_angle = 180 - elongation.degrees
illumination = (1 + cos(phase_angle)) / 2 * 100
```

- **New Moon**: Sun and Moon in the same direction (elongation ≈ 0°) → 0% illuminated
- **Full Moon**: Sun and Moon in opposite directions (elongation ≈ 180°) → 100% illuminated
- **Quarter**: 90° apart → 50% illuminated

To determine if the moon is **waxing** (growing) or **waning** (shrinking), we compare tonight's elongation with tomorrow's. If tomorrow's elongation is smaller, the moon is past full and waning.

Moon illumination affects stargazing:
- **>75%**: Bright moonlight washes out faint stars
- **40-75%**: Some impact on faint stars
- **<40%**: Dark sky, great conditions

---

## How the Sky Map Works

### Mapping Alt/Az to Pixels

The sky map is a circle representing the dome of the sky above you. The center is the zenith (directly overhead), the edge is the horizon.

Converting altitude/azimuth to x/y coordinates:

```javascript
// Distance from center: altitude 90° = center, 0° = edge
const dist = (1 - alt / 90) * radius * 0.9;

// Angle from north, clockwise
const angle = (azimuth - 90) * Math.PI / 180;

// Cartesian coordinates
const x = centerX + dist * Math.cos(angle);
const y = centerY + dist * Math.sin(angle);
```

The `- 90` converts from compass bearing (0° = top/North) to standard math angle (0° = right). The `* 0.9` adds a small margin so stars at the horizon aren't right at the edge.

Star dot size scales with brightness:

```
width = max(12 - magnitude * 2, 4) pixels
```

So Sirius (mag -1.4) gets a 14.8px dot, while Deneb (mag 1.2) gets a 9.6px dot.

### Time Slider

The slider lets you scrub through 24 hours. Each object has a pre-computed array of 24 positions (one per hour). Moving the slider updates every star's position with a CSS transition:

```javascript
slider.addEventListener('input', () => {
    updatePositions(parseInt(slider.value));
});
```

During daytime hours, stars are shown at 20% opacity to indicate they're above the horizon but not visible. The sky map border changes color and a sun indicator appears.

---

## Star Colors and Types

Star colors in the sky map reflect their actual spectral type (surface temperature):

| Color | Temperature | Examples |
|---|---|---|
| Blue-white (`#aaccff`) | >10,000 K | Sirius, Rigel, Spica, Vega |
| White (`#ffffff`) | ~7,500 K | Altair, Deneb |
| Yellow (`#ffffcc`) | ~5,500 K | Capella, Polaris, Sun |
| Orange (`#ffcc88`) | ~4,500 K | Arcturus, Pollux |
| Red (`#ff8844`) | ~3,500 K | Betelgeuse, Aldebaran |
| Deep red (`#ff6644`) | ~3,000 K | Antares |

Planets have their own characteristic colors (Jupiter: warm white, Mars: reddish, Venus: bright white).

---

## Architecture

```
src/sky/
├── compute.py    # All astronomy calculations
│   ├── get_night_hours()      → list of 24 datetime objects
│   ├── compute_sky()          → top 20 objects + moon phase + hour labels
│   ├── compute_moon_phase()   → illumination %, name, emoji, impact
│   ├── is_dark_hour()         → bool
│   └── az_to_direction()      → compass string (N, NNE, NE, etc.)
│
├── builder.py    # Renders Jinja2 template to static HTML
│   └── build()                → writes build/sky/index.html
│
└── __init__.py

templates/
└── sky.html      # Interactive page with sky map, slider, table
    ├── CSS: Dark theme, sky map circle, responsive layout
    ├── HTML: Moon card, legend, sky map, time slider, data table
    └── JS: Star positioning, time slider, click interactions
```

**Data files** (auto-downloaded by Skyfield on first run):
- `de421.bsp` (~17 MB) — JPL planetary ephemeris (1899-2053)
- `hip_main.dat` (~53 MB) — Hipparcos star catalog

**Dependencies**:
- `skyfield` — Astronomy calculations (positions, magnitudes)
- `pandas` — Required by Skyfield to load the Hipparcos catalog
- `jinja2` — HTML template rendering

---

## Key Concepts for Beginners

| Concept | Where It's Used |
|---|---|
| **Coordinate systems** | RA/Dec (sky-fixed) vs Alt/Az (observer-fixed) |
| **Trigonometry** | Converting spherical to Cartesian coordinates for the sky map |
| **Logarithmic scales** | Magnitude system (each step = 2.5× brightness) |
| **Ephemeris** | Pre-computed tables of celestial body positions |
| **Atmospheric refraction** | Light bending makes stars appear higher than they are |
| **Phase angles** | Moon illumination depends on Sun-Moon-Earth geometry |
| **Data pipelines** | Fetch catalog → filter → compute positions → render HTML |
| **Static site generation** | Compute once, serve static HTML (no server needed) |
| **CSS transforms** | Positioning dots on a circular sky map |
| **Client-side interactivity** | Time slider updates positions without reloading |

### Want to Extend This?

- **Constellations**: Draw lines between stars that form constellation patterns
- **ISS tracking**: The ISS orbit is publicly available — show when it passes overhead
- **Multiple locations**: Let the user enter any latitude/longitude
- **Star names on map**: Show labels for the brightest few stars by default
- **Meteor showers**: Highlight dates of major meteor showers with radiant points
