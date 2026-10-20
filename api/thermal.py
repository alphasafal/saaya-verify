"""Transparent steady-state screening model for the SAAYA shelter.

Purpose: turn design hypotheses into falsifiable, numeric predictions that the
CoolProof protocol can test. It is NOT a validated thermal simulation, NOT a
human-safety model and NOT a substitute for measurement. Every coefficient is a
named, textbook-level assumption exposed as a parameter so that a reviewer can
challenge it and see the sensitivity.

Physics used (cited in docs/DEFENSE.md):
  * Thin metal roof skins in steady state, per square metre (no conduction lag).
  * Convection only: h = 2.8 + 3.0 v (Watmuff et al. 1977). Radiation is modelled
    explicitly, so McAdams' combined 5.7 + 3.8 v would double-count it.
  * Clear-sky temperature T_sky = 0.0552 * Ta^1.5 (K, Swinbank 1963). A cold, clear
    sky is OPTIMISTIC for seated radiant load; a hazy pre-monsoon sky is warmer.
  * Grey-body exchange between parallel skins: sigma (T1^4-T2^4) / (1/e1+1/e2-1).
  * Ventilated gap: gap air assumed at ambient temperature (optimistic); sealed gap:
    natural convection through trapped air (two faces in series).
  * Roof underside sees shaded and sunlit ground in proportion to its view factor
    (differential plate -> parallel rectangle, superposition).
  * Sphere mean radiant temperature: T_mrt^4 = sum_i (Omega_i/4pi) T_i^4 + S/(eps sigma),
    S = alpha (I_b/4 + D/2 + rho G/2), each term weighted by visible solid angle.
    Person alpha 0.7 / eps 0.97 (VDI 3787 / Hoeppe convention); a black globe is
    computed separately with alpha = eps = 0.95.
  * Solar noon position from latitude and date (Cooper declination). At 12.9 N the
    noon sun is NORTH of the zenith from late April to mid-August.
  * ISO 7730 operative temperature (indicative only: outside its validity range here).
  * ISO 7726 / ASHRAE forced-convection globe relation, inverted to predict a 150 mm
    globe reading.
"""
from __future__ import annotations
import itertools
import math
from dataclasses import dataclass, asdict, replace

SIGMA = 5.670374419e-8
K = 273.15


def _k(c: float) -> float:
    return c + K


def sky_temperature_k(ta_c: float) -> float:
    """Swinbank (1963) clear-sky effective temperature."""
    return 0.0552 * _k(ta_c) ** 1.5


def h_conv(v: float) -> float:
    """Convective-only wind coefficient, Watmuff, Charters & Proctor (1977)."""
    return 2.8 + 3.0 * max(0.0, v)


def _bisect(f, lo: float, hi: float, tol: float = 1e-7, it: int = 200) -> float:
    flo = f(lo)
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


@dataclass(frozen=True)
class Conditions:
    """Outdoor driving conditions. Defaults: clear mid-May noon in Vellore (assumed)."""
    ta_c: float = 38.0              # air temperature
    rh: float = 45.0                # relative humidity, % (fan screen only)
    ghi: float = 900.0              # global horizontal irradiance, W/m2
    diffuse_fraction: float = 0.2   # clear sky
    latitude_deg: float = 12.92     # Vellore
    day_of_year: int = 135          # 15 May
    wind: float = 1.0               # m/s at roof height
    ground_albedo: float = 0.2
    sunlit_ground_rise: float = 15.0  # sunlit ground surface above air, K (assumption; measure)
    shaded_ground_rise: float = 2.0   # shaded ground surface above air, K (assumption; measure)


def solar_noon(cond: Conditions) -> tuple[float, bool]:
    """(elevation in degrees, sun_is_north) at solar noon."""
    decl = 23.44 * math.sin(2 * math.pi * (284 + cond.day_of_year) / 365)
    return 90.0 - abs(cond.latitude_deg - decl), decl > cond.latitude_deg


@dataclass(frozen=True)
class Skin:
    solar_absorptance: float
    top_emissivity: float
    bottom_emissivity: float
    label: str


# Representative surface properties (order-of-magnitude, to be measured):
GALVANISED = Skin(0.65, 0.25, 0.25, 'bare galvanised steel (new; weathering raises emissivity)')
WHITE_TOP_BARE_UNDER = Skin(0.25, 0.90, 0.25, 'white top coat, bare low-e underside')
WHITE_BOTH = Skin(0.25, 0.90, 0.90, 'white painted both faces')
WEATHERED = Skin(0.75, 0.90, 0.90, 'weathered GI / cement-fibre sheet (typical existing shed)')
H_SEALED_GAP = 3.0  # W/m2K natural convection, each face of an unvented cavity (assumption)


@dataclass(frozen=True)
class Roof:
    """Roof geometry in metres. Plan frame: +y is north."""
    kind: str = 'double'                 # 'none' | 'single' | 'double'
    upper: Skin = WHITE_TOP_BARE_UNDER
    lower: Skin = GALVANISED             # only for 'double'; its underside faces people
    x0: float = -0.2
    x1: float = 2.6
    y0: float = -0.2
    y1: float = 2.2
    underside_height: float = 2.37       # lower skin above ground
    gap_wind_fraction: float = 0.3       # share of wind speed reaching the ventilated gap
    under_wind_fraction: float = 0.5     # share of wind speed under the roof


@dataclass(frozen=True)
class Person:
    px: float = 1.2
    py: float = 1.75                     # FS-01 rear bench
    head_height: float = 1.1             # seated
    shortwave_absorptance: float = 0.7   # VDI 3787 / Hoeppe convention for a person
    emissivity: float = 0.97
    air_speed: float = 0.3               # local air speed at the person (fan / breeze)


GLOBE_ABSORPTANCE = 0.95
GLOBE_EMISSIVITY = 0.95


def _corner_solid_angle(a: float, b: float, d: float) -> float:
    """Solid angle of an a x b rectangle in a plane at distance d, with one corner
    directly opposite the observer. Signed by a and b so superposition works."""
    if d <= 0 or a == 0 or b == 0:
        return 0.0
    s = math.copysign(1.0, a) * math.copysign(1.0, b)
    a, b = abs(a), abs(b)
    return s * math.atan(a * b / (d * math.sqrt(a * a + b * b + d * d)))


def rectangle_solid_angle(px, py, x0, x1, y0, y1, d) -> float:
    """Exact solid angle (sr) of axis-aligned rectangle [x0,x1]x[y0,y1] in a parallel
    plane at distance d from the point (px, py). Works for points outside the footprint."""
    total = 0.0
    for x, sx in ((x1 - px, 1), (x0 - px, -1)):
        for y, sy in ((y1 - py, 1), (y0 - py, -1)):
            total += sx * sy * _corner_solid_angle(x, y, d)
    return max(0.0, total)


def _corner_view_factor(a: float, b: float, d: float) -> float:
    """View factor from a differential plate to a parallel a x b rectangle at distance d,
    plate opposite one corner (standard catalogue relation). Signed for superposition."""
    if d <= 0 or a == 0 or b == 0:
        return 0.0
    s = math.copysign(1.0, a) * math.copysign(1.0, b)
    A, B = abs(a) / d, abs(b) / d
    f = (A / math.sqrt(1 + A * A) * math.atan(B / math.sqrt(1 + A * A))
         + B / math.sqrt(1 + B * B) * math.atan(A / math.sqrt(1 + B * B))) / (2 * math.pi)
    return s * f


def rectangle_view_factor(px, py, x0, x1, y0, y1, d) -> float:
    total = 0.0
    for x, sx in ((x1 - px, 1), (x0 - px, -1)):
        for y, sy in ((y1 - py, 1), (y0 - py, -1)):
            total += sx * sy * _corner_view_factor(x, y, d)
    return min(1.0, max(0.0, total))


def _shadow(cond: Conditions, roof: Roof):
    """Ground shadow rectangle at solar noon (sun north -> shadow shifts south)."""
    elev, north = solar_noon(cond)
    shift = roof.underside_height / math.tan(math.radians(elev)) * (-1 if north else 1)
    return roof.x0, roof.x1, roof.y0 + shift, roof.y1 + shift


def _ground_seen_by_roof_k4(cond: Conditions, roof: Roof) -> float:
    """Effective T^4 of the ground as seen by the roof underside (centre point)."""
    sx0, sx1, sy0, sy1 = _shadow(cond, roof)
    cx, cy = (roof.x0 + roof.x1) / 2, (roof.y0 + roof.y1) / 2
    f_shade = rectangle_view_factor(cx, cy, sx0, sx1, sy0, sy1, roof.underside_height)
    return (f_shade * _k(cond.ta_c + cond.shaded_ground_rise) ** 4
            + (1 - f_shade) * _k(cond.ta_c + cond.sunlit_ground_rise) ** 4)


def _single_skin(cond: Conditions, skin: Skin, h_under: float, ground4: float):
    ta = _k(cond.ta_c)
    tsky = sky_temperature_k(cond.ta_c)
    ho = h_conv(cond.wind)
    q = skin.solar_absorptance * cond.ghi

    def residual(t):
        return (q - ho * (t - ta) - skin.top_emissivity * SIGMA * (t**4 - tsky**4)
                - h_under * (t - ta) - skin.bottom_emissivity * SIGMA * (t**4 - ground4))
    t = _bisect(residual, ta - 40, ta + 150)
    return t, abs(residual(t))


def _double_skin(cond: Conditions, roof: Roof, h_under: float, ground4: float):
    ta = _k(cond.ta_c)
    tsky = sky_temperature_k(cond.ta_c)
    ho = h_conv(cond.wind)
    sealed = roof.gap_wind_fraction <= 0
    hg = 0.0 if sealed else h_conv(cond.wind * roof.gap_wind_fraction)
    hc = H_SEALED_GAP / 2 if sealed else 0.0
    u, l = roof.upper, roof.lower
    e_gap = 1.0 / (1.0 / u.bottom_emissivity + 1.0 / l.top_emissivity - 1.0)
    q = u.solar_absorptance * cond.ghi

    def upper_for(tl):
        def r(tu):
            return (q - ho * (tu - ta) - u.top_emissivity * SIGMA * (tu**4 - tsky**4)
                    - hg * (tu - ta) - hc * (tu - tl) - e_gap * SIGMA * (tu**4 - tl**4))
        return _bisect(r, ta - 40, ta + 150)

    def lower_residual(tl):
        tu = upper_for(tl)
        return (e_gap * SIGMA * (tu**4 - tl**4) + hc * (tu - tl) - hg * (tl - ta) - h_under * (tl - ta)
                - l.bottom_emissivity * SIGMA * (tl**4 - ground4))
    tl = _bisect(lower_residual, ta - 40, ta + 150)
    tu = upper_for(tl)
    loss = (ho * (tu - ta) + u.top_emissivity * SIGMA * (tu**4 - tsky**4) + hg * (tu - ta)
            + hg * (tl - ta) + h_under * (tl - ta) + l.bottom_emissivity * SIGMA * (tl**4 - ground4))
    return tu, tl, abs(q - loss)


def roof_temperatures(cond: Conditions, roof: Roof) -> dict:
    """Steady-state skin temperatures (deg C). 'underside_c' is the surface people see."""
    if roof.kind == 'none':
        return {'kind': 'none', 'underside_c': None, 'upper_c': None, 'energy_residual_w_m2': 0.0}
    ground4 = _ground_seen_by_roof_k4(cond, roof)
    h_under = h_conv(cond.wind * roof.under_wind_fraction)
    if roof.kind == 'single':
        t, res = _single_skin(cond, roof.upper, h_under, ground4)
        return {'kind': 'single', 'upper_c': t - K, 'underside_c': t - K, 'underside_emissivity': roof.upper.bottom_emissivity,
                'ground_seen_k4': ground4, 'energy_residual_w_m2': res}
    if roof.kind == 'double':
        tu, tl, res = _double_skin(cond, roof, h_under, ground4)
        return {'kind': 'double', 'upper_c': tu - K, 'underside_c': tl - K, 'underside_emissivity': roof.lower.bottom_emissivity,
                'ground_seen_k4': ground4, 'energy_residual_w_m2': res}
    raise ValueError('roof kind must be none, single or double')


def _sphere_mrt(cond: Conditions, roof: Roof, person: Person, temps: dict, alpha: float, eps: float) -> dict:
    four_pi = 4 * math.pi
    tsky = sky_temperature_k(cond.ta_c)
    t_sun_ground = _k(cond.ta_c + cond.sunlit_ground_rise)
    t_shade_ground = _k(cond.ta_c + cond.shaded_ground_rise)
    elev, north = solar_noon(cond)
    beta = math.radians(elev)
    diffuse = cond.ghi * cond.diffuse_fraction
    beam_normal = cond.ghi * (1 - cond.diffuse_fraction) / max(math.sin(beta), 0.05)

    if roof.kind == 'none':
        omega_roof = omega_shade = 0.0
        sun_blocked = False
    else:
        d_up = roof.underside_height - person.head_height
        if d_up <= 0:
            raise ValueError('roof must be above the head')
        omega_roof = rectangle_solid_angle(person.px, person.py, roof.x0, roof.x1, roof.y0, roof.y1, d_up)
        sx0, sx1, sy0, sy1 = _shadow(cond, roof)
        omega_shade = rectangle_solid_angle(person.px, person.py, sx0, sx1, sy0, sy1, person.head_height)
        # Ray from the head towards the noon sun: does it pass through the roof?
        y_hit = person.py + d_up / math.tan(beta) * (1 if north else -1)
        sun_blocked = roof.x0 <= person.px <= roof.x1 and roof.y0 <= y_hit <= roof.y1

    omega_sky = 2 * math.pi - omega_roof
    omega_sun_ground = 2 * math.pi - omega_shade
    if roof.kind == 'none':
        t_roof_eff4 = 0.0
    else:
        e = temps['underside_emissivity']
        # A low-e underside reflects what it sees: mostly ground.
        t_roof_eff4 = e * _k(temps['underside_c']) ** 4 + (1 - e) * temps['ground_seen_k4']
    lw = (omega_roof * t_roof_eff4 + omega_sky * tsky**4
          + omega_shade * t_shade_ground**4 + omega_sun_ground * t_sun_ground**4) / four_pi
    direct = 0.0 if sun_blocked else beam_normal / 4
    sky_diffuse = diffuse / 2 * (omega_sky / (2 * math.pi))
    reflected = (cond.ground_albedo / 2) * (cond.ghi * omega_sun_ground + diffuse * omega_shade) / (2 * math.pi)
    s_abs = alpha * (direct + sky_diffuse + reflected)
    tmrt = (lw + s_abs / (eps * SIGMA)) ** 0.25 - K
    return {'tmrt_c': tmrt, 'sun_blocked': sun_blocked, 'shortwave_absorbed_w_m2': s_abs,
            'view_fractions': {'roof': omega_roof / four_pi, 'sky': omega_sky / four_pi,
                               'shaded_ground': omega_shade / four_pi, 'sunlit_ground': omega_sun_ground / four_pi}}


def mean_radiant_temperature(cond: Conditions, roof: Roof, person: Person) -> dict:
    """Person MRT at the seated head plus the prediction for a 150 mm black globe there."""
    temps = roof_temperatures(cond, roof)
    p = _sphere_mrt(cond, roof, person, temps, person.shortwave_absorptance, person.emissivity)
    g = _sphere_mrt(cond, roof, person, temps, GLOBE_ABSORPTANCE, GLOBE_EMISSIVITY)
    v = person.air_speed
    a = 0.5 if v < 0.2 else (0.6 if v < 0.6 else 0.7)
    return {
        'tmrt_c': p['tmrt_c'],
        'operative_c_indicative': a * cond.ta_c + (1 - a) * p['tmrt_c'],
        'globe_150mm_c': globe_temperature(g['tmrt_c'], cond.ta_c, v),
        'sun_on_head': not p['sun_blocked'],
        'view_fractions': p['view_fractions'],
        'shortwave_absorbed_w_m2': p['shortwave_absorbed_w_m2'],
        'roof': temps,
    }


def globe_temperature(tmrt_c: float, ta_c: float, v: float, diameter: float = 0.15, emissivity: float = GLOBE_EMISSIVITY) -> float:
    """Invert Tmrt^4 = Tg^4 + 1.1e8 v^0.6 /(eps D^0.4) (Tg - Ta). Note: below ~1 m/s mixed
    convection makes this relation biased (Teitelbaum et al. 2022); record air speed."""
    v = max(v, 0.1)
    c = 1.1e8 * v**0.6 / (emissivity * diameter**0.4)
    target = _k(tmrt_c) ** 4

    def r(tg_k):
        return tg_k**4 + c * (tg_k - _k(ta_c)) - target
    lo, hi = min(_k(ta_c), _k(tmrt_c)) - 1, max(_k(ta_c), _k(tmrt_c)) + 1
    return _bisect(r, lo, hi) - K


def seats(roof: Roof | None = None) -> dict:
    """The FS-01 bench seat and its mirror image (the less shaded edge when the sun swaps sides)."""
    roof = roof or Roof()
    p = Person()
    return {'rear seat': p, 'mirrored seat': replace(p, py=roof.y0 + roof.y1 - p.py)}


def _worst(cond, roof, people):
    runs = {name: mean_radiant_temperature(cond, roof, p) for name, p in people.items()}
    name = max(runs, key=lambda n: runs[n]['tmrt_c'])
    return name, runs


DESIGNS = [
    ('Open sun (no shelter)', lambda b: replace(b, kind='none')),
    ('Weathered GI / cement sheet (typical existing shed)', lambda b: replace(b, kind='single', upper=WEATHERED)),
    ('Single bare galvanised sheet', lambda b: replace(b, kind='single', upper=GALVANISED)),
    ('Single sheet, white both faces', lambda b: replace(b, kind='single', upper=WHITE_BOTH)),
    ('Single sheet, white top / bare underside', lambda b: replace(b, kind='single', upper=WHITE_TOP_BARE_UNDER)),
    ('SAAYA double roof (white top, ventilated gap, bare low-e lining)', lambda b: b),
    ('Double roof, sealed (unventilated) gap', lambda b: replace(b, gap_wind_fraction=0.0)),
]


def compare_designs(cond: Conditions | None = None) -> list[dict]:
    """Headline table. Each design is reported at its LESS favourable seat."""
    cond = cond or Conditions()
    out = []
    for name, make in DESIGNS:
        roof = make(Roof())
        seat, runs = _worst(cond, roof, seats())
        m = runs[seat]
        out.append({'design': name, 'underside_c': m['roof']['underside_c'], 'upper_c': m['roof']['upper_c'],
                    'tmrt_c': m['tmrt_c'], 'tmrt_by_seat_c': {k: v['tmrt_c'] for k, v in runs.items()},
                    'reported_seat': seat, 'operative_c_indicative': m['operative_c_indicative'],
                    'globe_150mm_c': m['globe_150mm_c'], 'sun_on_head': m['sun_on_head'],
                    'view_fractions': m['view_fractions'], 'energy_residual_w_m2': m['roof']['energy_residual_w_m2']})
    return out


def headline(designs: list[dict]) -> dict:
    by = {d['design']: d for d in designs}
    open_sun = by['Open sun (no shelter)']['tmrt_c']
    shed = by['Weathered GI / cement sheet (typical existing shed)']
    saaya = by['SAAYA double roof (white top, ventilated gap, bare low-e lining)']
    return {'shade_alone_k': open_sun - shed['tmrt_c'], 'roof_treatment_k': shed['tmrt_c'] - saaya['tmrt_c'],
            'total_k': open_sun - saaya['tmrt_c'], 'underside_cooler_k': shed['underside_c'] - saaya['underside_c'],
            'roof_view_fraction': saaya['view_fractions']['roof']}


def overhang_study(extra_m=(0.0, 0.3, 0.6, 0.9, 1.2), cond: Conditions | None = None) -> list[dict]:
    cond = cond or Conditions()
    rows = []
    for e in extra_m:
        roof = replace(Roof(), x0=Roof.x0 - e, x1=Roof.x1 + e, y0=Roof.y0 - e, y1=Roof.y1 + e)
        seat, runs = _worst(cond, roof, seats())
        rows.append({'extra_overhang_m': e, 'roof_area_m2': (roof.x1 - roof.x0) * (roof.y1 - roof.y0),
                     'tmrt_c': runs[seat]['tmrt_c'], 'roof_view_fraction': runs[seat]['view_fractions']['roof']})
    return rows


def _pair(cond, shed_roof=None, saaya_roof=None):
    shed_roof = shed_roof or replace(Roof(), kind='single', upper=WEATHERED)
    saaya_roof = saaya_roof or Roof()
    a = mean_radiant_temperature(cond, shed_roof, Person())['tmrt_c']
    b = mean_radiant_temperature(cond, saaya_roof, Person())['tmrt_c']
    return a, b


def sensitivity(cond: Conditions | None = None) -> list[dict]:
    """One-at-a-time sensitivity of SAAYA's roof benefit versus a weathered shed (rear seat)."""
    cond = cond or Conditions()
    out = []
    for label, field, values in (('wind (m/s)', 'wind', [0.3, 1.0, 3.0]), ('irradiance (W/m²)', 'ghi', [600.0, 900.0, 1050.0]),
                                 ('air temperature (°C)', 'ta_c', [32.0, 38.0, 42.0]),
                                 ('sunlit ground rise (K)', 'sunlit_ground_rise', [8.0, 15.0, 25.0]),
                                 ('day of year', 'day_of_year', [74, 135, 288])):
        for value in values:
            a, b = _pair(replace(cond, **{field: value}))
            out.append({'parameter': label, 'value': value, 'tmrt_existing_shed_c': a, 'tmrt_saaya_c': b, 'benefit_k': a - b})
    for eps in (0.25, 0.4, 0.6):
        lining = replace(GALVANISED, top_emissivity=eps, bottom_emissivity=eps)
        a, b = _pair(cond, saaya_roof=replace(Roof(), lower=lining))
        out.append({'parameter': 'lining emissivity (weathering)', 'value': eps, 'tmrt_existing_shed_c': a, 'tmrt_saaya_c': b, 'benefit_k': a - b})
    for frac in (0.0, 0.1, 0.3, 0.6):
        a, b = _pair(cond, saaya_roof=replace(Roof(), gap_wind_fraction=frac))
        out.append({'parameter': 'gap ventilation fraction', 'value': frac, 'tmrt_existing_shed_c': a, 'tmrt_saaya_c': b, 'benefit_k': a - b})
    return out


def second_skin_value(cond: Conditions | None = None) -> list[dict]:
    """Is the upper skin worth its cost? Single white-top/low-e sheet vs double roof, as the top coat soils."""
    cond = cond or Conditions()
    rows = []
    for state, alpha in (('clean white top', 0.25), ('soiled top coat', 0.45), ('badly soiled / chalked', 0.60)):
        top = Skin(alpha, 0.90, 0.25, f'top coat {state}')
        a = mean_radiant_temperature(cond, replace(Roof(), kind='single', upper=top), Person())
        b = mean_radiant_temperature(cond, replace(Roof(), upper=top), Person())
        rows.append({'top_coat': state, 'solar_absorptance': alpha,
                     'single_underside_c': a['roof']['underside_c'], 'double_underside_c': b['roof']['underside_c'],
                     'single_tmrt_c': a['tmrt_c'], 'double_tmrt_c': b['tmrt_c'],
                     'tmrt_saved_by_second_skin_k': a['tmrt_c'] - b['tmrt_c']})
    return rows


def ground_study(cond: Conditions | None = None) -> list[dict]:
    """The seated person sees more sunlit ground than roof; quantify that lever (rear seat)."""
    cond = cond or Conditions()
    rows = []
    for label, rise, albedo in (('bare dark soil / asphalt', 22.0, 0.10), ('typical dry ground', 15.0, 0.20),
                                ('light paving', 12.0, 0.40), ('irrigated grass / ground cover', 4.0, 0.22)):
        c = replace(cond, sunlit_ground_rise=rise, ground_albedo=albedo)
        rows.append({'surround': label, 'sunlit_ground_rise_k': rise, 'albedo': albedo,
                     'tmrt_c': mean_radiant_temperature(c, Roof(), Person())['tmrt_c']})
    return rows


def prediction_bands(cond: Conditions | None = None) -> list[dict]:
    """Declared model tolerance: the range each measurable prediction spans when uncertain
    inputs take their plausible extremes (2^5 corner cases). A measurement taken under the
    stated conditions that falls outside this band refutes the model."""
    cond = cond or Conditions()
    ranges = {'ghi': (800.0, 1000.0), 'wind': (0.5, 2.0), 'diffuse_fraction': (0.15, 0.3),
              'sunlit_ground_rise': (10.0, 20.0), 'lining_eps': (0.25, 0.5)}
    targets = {'SAAYA double roof': Roof(), 'Weathered shed sheet': replace(Roof(), kind='single', upper=WEATHERED)}
    out = []
    for name, base in targets.items():
        under, globe = [], []
        for combo in itertools.product(*ranges.values()):
            k = dict(zip(ranges, combo))
            eps = k.pop('lining_eps')
            roof = base if base.kind == 'single' else replace(base, lower=replace(GALVANISED, top_emissivity=eps, bottom_emissivity=eps))
            m = mean_radiant_temperature(replace(cond, **k), roof, Person())
            under.append(m['roof']['underside_c']); globe.append(m['globe_150mm_c'])
        out.append({'target': name, 'underside_c': [min(under), max(under)], 'globe_150mm_c': [min(globe), max(globe)]})
    return out


def report() -> dict:
    """Everything the public defense page shows, from one tested source."""
    cond = Conditions()
    elev, north = solar_noon(cond)
    designs = compare_designs(cond)
    return {
        'status': 'SCREENING MODEL - assumptions explicit, not validated, not a safety assessment',
        'conditions': dict(asdict(cond), sun_elevation_deg=elev, sun_is_north=north),
        'person': asdict(Person()),
        'designs': designs,
        'headline': headline(designs),
        'overhang': overhang_study(cond=cond),
        'sensitivity': sensitivity(cond),
        'second_skin': second_skin_value(cond),
        'ground': ground_study(cond),
        'prediction_bands': prediction_bands(cond),
        'falsification': [
            'Roof underside: DS18B20 bonded to the lining, shielded from sun; compare with prediction_bands[].underside_c.',
            '150 mm black globe at seated head height with air speed logged; compare with prediction_bands[].globe_150mm_c.',
            'Log irradiance, wind and ground temperature at the same time. Reject the model if the measurement falls outside the band on 2 or more of 3 clear days.',
        ],
    }
