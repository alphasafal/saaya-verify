"""Transparent steady-state screening model for the SAAYA shelter.

Purpose: turn design hypotheses into falsifiable, numeric predictions that the
CoolProof protocol can test. It is NOT a validated thermal simulation, NOT a
human-safety model and NOT a substitute for measurement. Every coefficient is a
named, textbook-level assumption exposed as a parameter so that a reviewer can
challenge it and see the sensitivity.

Physics used (all standard, cited in docs/DEFENSE.md):
  * Thin metal roof skins in steady state, per square metre (no conduction lag).
  * External convection h = 5.7 + 3.8 v  (W/m2K, McAdams/Watmuff wind relation).
  * Clear-sky temperature T_sky = 0.0552 * Ta^1.5 (K, Swinbank 1963).
  * Grey-body exchange between parallel skins: sigma (T1^4-T2^4) / (1/e1+1/e2-1).
  * Mean radiant temperature of a sphere: T_mrt^4 = sum_i (Omega_i/4pi) T_i^4
    + S_abs/(eps_p sigma), with shortwave S_abs = alpha_p (I_b/4 + D/2 + rho G/2)
    weighted by visible solid angle (ISO 7726 sphere convention).
  * Exact solid angle of a rectangle seen from a point (corner formula and
    superposition), so roof size, height and overhang are geometric inputs.
  * ISO 7730 operative temperature weighting by air speed.
  * ISO 7726 forced-convection globe relation, inverted to predict what a black
    globe thermometer should read -- the cheapest independent check.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, asdict, replace

SIGMA = 5.670374419e-8
K = 273.15


def _k(c: float) -> float:
    return c + K


def sky_temperature_k(ta_c: float) -> float:
    """Swinbank (1963) clear-sky effective temperature. Conservative (cold sky)."""
    return 0.0552 * _k(ta_c) ** 1.5


def h_wind(v: float) -> float:
    return 5.7 + 3.8 * max(0.0, v)


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
    """Outdoor driving conditions. Defaults: a clear pre-monsoon Vellore noon (assumed)."""
    ta_c: float = 38.0              # air temperature
    rh: float = 45.0                # relative humidity, % (used by fan screen only)
    ghi: float = 900.0              # global horizontal irradiance, W/m2
    diffuse_fraction: float = 0.2   # clear sky
    sun_elevation_deg: float = 78.0 # near-noon, latitude ~12.9 N, Apr-May
    wind: float = 1.0               # m/s at roof height
    ground_albedo: float = 0.2
    sunlit_ground_rise: float = 15.0  # sunlit ground surface above air, K (assumption; measure)
    shaded_ground_rise: float = 2.0   # shaded ground surface above air, K (assumption; measure)


@dataclass(frozen=True)
class Skin:
    solar_absorptance: float
    top_emissivity: float
    bottom_emissivity: float
    label: str


# Representative surface properties (order-of-magnitude, to be measured):
GALVANISED = Skin(0.65, 0.25, 0.25, 'bare galvanised steel')
WHITE_TOP_BARE_UNDER = Skin(0.25, 0.90, 0.25, 'white top coat, bare low-e underside')
WHITE_BOTH = Skin(0.25, 0.90, 0.90, 'white painted both faces')
WEATHERED = Skin(0.75, 0.90, 0.90, 'weathered GI / cement-fibre sheet (typical existing shed)')
H_SEALED_GAP = 3.0  # W/m2K natural convection, each face of an unvented cavity (assumption)


@dataclass(frozen=True)
class Roof:
    """Roof geometry in metres, in a plan frame where the seated head is at (px, py)."""
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
    py: float = 1.75
    head_height: float = 1.1             # seated
    shortwave_absorptance: float = 0.7   # ISO 7726 convention
    emissivity: float = 0.97
    air_speed: float = 0.3               # local air speed at the person (fan / breeze)


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


def _single_skin(cond: Conditions, skin: Skin, h_under: float, t_ground_k: float):
    ta = _k(cond.ta_c)
    tsky = sky_temperature_k(cond.ta_c)
    ho = h_wind(cond.wind)
    q = skin.solar_absorptance * cond.ghi

    def residual(t):
        return (q - ho * (t - ta) - skin.top_emissivity * SIGMA * (t**4 - tsky**4)
                - h_under * (t - ta) - skin.bottom_emissivity * SIGMA * (t**4 - t_ground_k**4))
    t = _bisect(residual, ta - 40, ta + 150)
    return t, abs(residual(t))


def _double_skin(cond: Conditions, roof: Roof, h_under: float, t_ground_k: float):
    ta = _k(cond.ta_c)
    tsky = sky_temperature_k(cond.ta_c)
    ho = h_wind(cond.wind)
    sealed = roof.gap_wind_fraction <= 0
    # Ventilated: both gap faces exchange with ambient-temperature air.
    # Sealed: no ambient exchange; the trapped air couples the skins (two faces in series).
    hg = 0.0 if sealed else h_wind(cond.wind * roof.gap_wind_fraction)
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
                - l.bottom_emissivity * SIGMA * (tl**4 - t_ground_k**4))
    tl = _bisect(lower_residual, ta - 40, ta + 150)
    tu = upper_for(tl)
    # Closure check of the whole two-node network.
    gain = q
    loss = (ho * (tu - ta) + u.top_emissivity * SIGMA * (tu**4 - tsky**4) + hg * (tu - ta)
            + hg * (tl - ta) + h_under * (tl - ta) + l.bottom_emissivity * SIGMA * (tl**4 - t_ground_k**4))
    return tu, tl, abs(gain - loss)


def roof_temperatures(cond: Conditions, roof: Roof) -> dict:
    """Steady-state skin temperatures (deg C). 'underside_c' is the surface people see."""
    t_shaded = _k(cond.ta_c + cond.shaded_ground_rise)
    h_under = h_wind(cond.wind * roof.under_wind_fraction)
    if roof.kind == 'none':
        return {'kind': 'none', 'underside_c': None, 'upper_c': None, 'energy_residual_w_m2': 0.0}
    if roof.kind == 'single':
        t, res = _single_skin(cond, roof.upper, h_under, t_shaded)
        return {'kind': 'single', 'upper_c': t - K, 'underside_c': t - K,
                'underside_emissivity': roof.upper.bottom_emissivity, 'energy_residual_w_m2': res}
    if roof.kind == 'double':
        tu, tl, res = _double_skin(cond, roof, h_under, t_shaded)
        return {'kind': 'double', 'upper_c': tu - K, 'underside_c': tl - K,
                'underside_emissivity': roof.lower.bottom_emissivity, 'energy_residual_w_m2': res}
    raise ValueError('roof kind must be none, single or double')


def mean_radiant_temperature(cond: Conditions, roof: Roof, person: Person) -> dict:
    """Sphere MRT at the seated head, with solid-angle bookkeeping that sums to 4 pi."""
    four_pi = 4 * math.pi
    ta = _k(cond.ta_c)
    tsky = sky_temperature_k(cond.ta_c)
    t_sun_ground = _k(cond.ta_c + cond.sunlit_ground_rise)
    t_shade_ground = _k(cond.ta_c + cond.shaded_ground_rise)
    beta = math.radians(cond.sun_elevation_deg)
    diffuse = cond.ghi * cond.diffuse_fraction
    beam_normal = cond.ghi * (1 - cond.diffuse_fraction) / max(math.sin(beta), 0.05)
    temps = roof_temperatures(cond, roof)

    if roof.kind == 'none':
        omega_roof = 0.0
        omega_shade = 0.0
        sun_blocked = False
    else:
        d_up = roof.underside_height - person.head_height
        if d_up <= 0:
            raise ValueError('roof must be above the head')
        omega_roof = rectangle_solid_angle(person.px, person.py, roof.x0, roof.x1, roof.y0, roof.y1, d_up)
        # Ground shadow displaced toward the sun's opposite side by H / tan(beta) (sun due south, +y north).
        shift = roof.underside_height / math.tan(beta)
        omega_shade = rectangle_solid_angle(person.px, person.py, roof.x0, roof.x1,
                                            roof.y0 + shift, roof.y1 + shift, person.head_height)
        # Is the head inside the roof's shadow line for the direct beam?
        y_hit = person.py - d_up / math.tan(beta)
        sun_blocked = roof.x0 <= person.px <= roof.x1 and roof.y0 <= y_hit <= roof.y1

    omega_sky = 2 * math.pi - omega_roof
    omega_sun_ground = 2 * math.pi - omega_shade

    # Long-wave: roof underside seen through its emissivity, reflecting ~shaded ground.
    if roof.kind == 'none':
        t_roof_eff4 = 0.0
    else:
        e = temps['underside_emissivity']
        t_roof_eff4 = e * _k(temps['underside_c']) ** 4 + (1 - e) * t_shade_ground ** 4
    lw = (omega_roof * t_roof_eff4 + omega_sky * tsky**4
          + omega_shade * t_shade_ground**4 + omega_sun_ground * t_sun_ground**4) / four_pi

    # Short-wave absorbed per unit sphere area.
    direct = 0.0 if sun_blocked else beam_normal / 4
    sky_diffuse = diffuse / 2 * (omega_sky / (2 * math.pi))
    reflected = (cond.ground_albedo / 2) * (cond.ghi * omega_sun_ground + diffuse * omega_shade) / (2 * math.pi)
    s_abs = person.shortwave_absorptance * (direct + sky_diffuse + reflected)

    tmrt = (lw + s_abs / (person.emissivity * SIGMA)) ** 0.25
    tmrt_c = tmrt - K
    v = person.air_speed
    a = 0.5 if v < 0.2 else (0.6 if v < 0.6 else 0.7)
    operative = a * cond.ta_c + (1 - a) * tmrt_c
    return {
        'tmrt_c': tmrt_c,
        'operative_c': operative,
        'globe_150mm_c': globe_temperature(tmrt_c, cond.ta_c, v),
        'sun_on_head': not sun_blocked,
        'view_fractions': {
            'roof': omega_roof / four_pi, 'sky': omega_sky / four_pi,
            'shaded_ground': omega_shade / four_pi, 'sunlit_ground': omega_sun_ground / four_pi,
        },
        'shortwave_absorbed_w_m2': s_abs,
        'roof': temps,
    }


def globe_temperature(tmrt_c: float, ta_c: float, v: float, diameter: float = 0.15, emissivity: float = 0.95) -> float:
    """Invert ISO 7726 forced convection: Tmrt^4 = Tg^4 + 1.1e8 v^0.6 /(eps D^0.4) (Tg - Ta)."""
    v = max(v, 0.1)
    c = 1.1e8 * v**0.6 / (emissivity * diameter**0.4)
    target = _k(tmrt_c) ** 4

    def r(tg_k):
        return tg_k**4 + c * (tg_k - _k(ta_c)) - target
    lo, hi = min(_k(ta_c), _k(tmrt_c)) - 1, max(_k(ta_c), _k(tmrt_c)) + 1
    return _bisect(r, lo, hi) - K


def compare_designs(cond: Conditions | None = None, person: Person | None = None) -> list[dict]:
    """The headline table: what each roof option should do to the seated radiant load."""
    cond = cond or Conditions()
    person = person or Person()
    base = Roof()
    options = [
        ('Open sun (no shelter)', replace(base, kind='none')),
        ('Weathered GI / cement sheet (typical existing shed)', replace(base, kind='single', upper=WEATHERED)),
        ('Single bare galvanised sheet', replace(base, kind='single', upper=GALVANISED)),
        ('Single sheet, white both faces', replace(base, kind='single', upper=WHITE_BOTH)),
        ('Single sheet, white top / bare underside', replace(base, kind='single', upper=WHITE_TOP_BARE_UNDER)),
        ('SAAYA double roof (white top, ventilated gap, bare low-e lining)', base),
        ('Double roof, sealed (unventilated) gap', replace(base, gap_wind_fraction=0.0)),
    ]
    out = []
    for name, roof in options:
        m = mean_radiant_temperature(cond, roof, person)
        out.append({'design': name, 'underside_c': m['roof']['underside_c'], 'upper_c': m['roof']['upper_c'],
                    'tmrt_c': m['tmrt_c'], 'operative_c': m['operative_c'], 'globe_150mm_c': m['globe_150mm_c'],
                    'sun_on_head': m['sun_on_head'], 'view_fractions': m['view_fractions'],
                    'energy_residual_w_m2': m['roof']['energy_residual_w_m2']})
    return out


def overhang_study(extra_m=(0.0, 0.3, 0.6, 0.9, 1.2), cond: Conditions | None = None, person: Person | None = None) -> list[dict]:
    """Deep-verandah argument: how much each extra metre of overhang buys at the seat."""
    cond = cond or Conditions()
    person = person or Person()
    rows = []
    base = Roof()
    for e in extra_m:
        roof = replace(base, x0=base.x0 - e, x1=base.x1 + e, y0=base.y0 - e, y1=base.y1 + e)
        m = mean_radiant_temperature(cond, roof, person)
        area = (roof.x1 - roof.x0) * (roof.y1 - roof.y0)
        rows.append({'extra_overhang_m': e, 'roof_area_m2': area, 'tmrt_c': m['tmrt_c'],
                     'roof_view_fraction': m['view_fractions']['roof']})
    return rows


def sensitivity(cond: Conditions | None = None, person: Person | None = None) -> list[dict]:
    """One-at-a-time sensitivity of the SAAYA roof benefit versus a typical weathered shed sheet."""
    cond = cond or Conditions()
    person = person or Person()
    base = Roof()
    single = replace(base, kind='single', upper=WEATHERED)
    variations = [
        ('wind', 'wind', [0.3, 1.0, 3.0]),
        ('irradiance', 'ghi', [600.0, 900.0, 1050.0]),
        ('air temperature', 'ta_c', [32.0, 38.0, 42.0]),
        ('sunlit ground rise', 'sunlit_ground_rise', [8.0, 15.0, 25.0]),
    ]
    out = []
    for label, field, values in variations:
        for value in values:
            c = replace(cond, **{field: value})
            a = mean_radiant_temperature(c, single, person)['tmrt_c']
            b = mean_radiant_temperature(c, base, person)['tmrt_c']
            out.append({'parameter': label, 'value': value, 'tmrt_existing_shed_c': a,
                        'tmrt_saaya_c': b, 'benefit_k': a - b})
    for frac in (0.0, 0.1, 0.3, 0.6):
        r = replace(base, gap_wind_fraction=frac)
        a = mean_radiant_temperature(cond, single, person)['tmrt_c']
        b = mean_radiant_temperature(cond, r, person)['tmrt_c']
        out.append({'parameter': 'gap ventilation fraction', 'value': frac,
                    'tmrt_existing_shed_c': a, 'tmrt_saaya_c': b, 'benefit_k': a - b})
    return out


def second_skin_value(cond: Conditions | None = None, person: Person | None = None) -> list[dict]:
    """Is the upper skin worth its cost? Compare one white-top/low-e-underside sheet with the
    double roof, clean and after the white top coat has soiled (absorptance rises)."""
    cond = cond or Conditions()
    person = person or Person()
    rows = []
    for state, alpha in (('clean white top', 0.25), ('soiled top coat', 0.45), ('badly soiled / chalked', 0.60)):
        top = Skin(alpha, 0.90, 0.25, f'top coat {state}')
        single = replace(Roof(), kind='single', upper=top)
        double = replace(Roof(), upper=top)
        a = mean_radiant_temperature(cond, single, person)
        b = mean_radiant_temperature(cond, double, person)
        rows.append({'top_coat': state, 'solar_absorptance': alpha,
                     'single_underside_c': a['roof']['underside_c'], 'double_underside_c': b['roof']['underside_c'],
                     'single_tmrt_c': a['tmrt_c'], 'double_tmrt_c': b['tmrt_c'],
                     'tmrt_saved_by_second_skin_k': a['tmrt_c'] - b['tmrt_c']})
    return rows


def ground_study(cond: Conditions | None = None, person: Person | None = None) -> list[dict]:
    """The seated person sees more sunlit ground than roof; quantify that lever."""
    cond = cond or Conditions()
    person = person or Person()
    rows = []
    for label, rise, albedo in (('bare dark soil / asphalt', 22.0, 0.10), ('typical dry ground', 15.0, 0.20),
                                ('light paving', 12.0, 0.40), ('irrigated grass / ground cover', 4.0, 0.22)):
        c = replace(cond, sunlit_ground_rise=rise, ground_albedo=albedo)
        rows.append({'surround': label, 'sunlit_ground_rise_k': rise, 'albedo': albedo,
                     'tmrt_c': mean_radiant_temperature(c, Roof(), person)['tmrt_c']})
    return rows


def report() -> dict:
    """Everything the public defense page shows, from one tested source."""
    cond = Conditions()
    person = Person()
    return {
        'status': 'SCREENING MODEL - assumptions explicit, not validated, not a safety assessment',
        'conditions': asdict(cond),
        'person': asdict(person),
        'designs': compare_designs(cond, person),
        'overhang': overhang_study(cond=cond, person=person),
        'sensitivity': sensitivity(cond, person),
        'second_skin': second_skin_value(cond, person),
        'ground': ground_study(cond, person),
        'falsification': [
            'Roof underside (DS18B20 taped to lower skin, shaded from sun): predicted values in designs[].underside_c.',
            'Black globe 150 mm at seated head height: predicted designs[].globe_150mm_c at the stated air speed.',
            'Reject the model if paired measurements across >=3 independent clear days differ by more than the declared margin.',
        ],
    }
