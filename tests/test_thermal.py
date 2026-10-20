import math
from dataclasses import replace
import pytest
from api.thermal import (Conditions, Roof, Person, GALVANISED, WHITE_BOTH, WEATHERED, rectangle_solid_angle,
                         rectangle_view_factor, roof_temperatures, mean_radiant_temperature, globe_temperature,
                         compare_designs, headline, overhang_study, second_skin_value, prediction_bands, solar_noon,
                         report, sky_temperature_k, h_conv)


def test_solid_angle_limits_and_superposition():
    # A huge plane fills the hemisphere: 2 pi.
    assert rectangle_solid_angle(0, 0, -1e6, 1e6, -1e6, 1e6, 1.0) == pytest.approx(2 * math.pi, rel=1e-5)
    # Closed-form check: square of side 2 centred at distance 1 -> 4*asin(1/(sqrt2*sqrt2)) = 4*asin(1/2).
    assert rectangle_solid_angle(0, 0, -1, 1, -1, 1, 1.0) == pytest.approx(4 * math.asin(1 / 2), rel=1e-9)
    # Splitting the rectangle in two must conserve solid angle (superposition).
    whole = rectangle_solid_angle(0.3, 0.2, -1, 2, -1, 1, 1.4)
    parts = rectangle_solid_angle(0.3, 0.2, -1, 0.5, -1, 1, 1.4) + rectangle_solid_angle(0.3, 0.2, 0.5, 2, -1, 1, 1.4)
    assert whole == pytest.approx(parts, rel=1e-9)
    # A point outside the footprint still sees a positive, smaller angle.
    assert 0 < rectangle_solid_angle(5, 0, -1, 1, -1, 1, 1.0) < rectangle_solid_angle(0, 0, -1, 1, -1, 1, 1.0)


def test_view_fractions_close_to_one_sphere():
    m = mean_radiant_temperature(Conditions(), Roof(), Person())
    assert sum(m['view_fractions'].values()) == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize('kind', ['single', 'double'])
def test_roof_energy_balance_closes(kind):
    r = roof_temperatures(Conditions(), replace(Roof(), kind=kind))
    assert r['energy_residual_w_m2'] < 1e-3


def test_no_sun_roof_near_or_below_air():
    # At night the roof radiates to a cold sky; it cannot be hotter than the air.
    r = roof_temperatures(replace(Conditions(), ghi=0.0, sunlit_ground_rise=0.0, shaded_ground_rise=0.0), replace(Roof(), kind='single', upper=WHITE_BOTH))
    assert r['underside_c'] <= Conditions().ta_c + 0.5


def test_physical_orderings():
    c = Conditions()
    dark = roof_temperatures(c, replace(Roof(), kind='single', upper=WEATHERED))['underside_c']
    white = roof_temperatures(c, replace(Roof(), kind='single', upper=WHITE_BOTH))['underside_c']
    double = roof_temperatures(c, Roof())['underside_c']
    assert dark > white > double > c.ta_c
    # More wind always cools a sunlit roof.
    calm = roof_temperatures(replace(c, wind=0.3), Roof())['upper_c']
    windy = roof_temperatures(replace(c, wind=3.0), Roof())['upper_c']
    assert calm > windy
    # Sealing the gap must not make the lining cooler than a ventilated gap.
    sealed = roof_temperatures(c, replace(Roof(), gap_wind_fraction=0.0))['underside_c']
    assert sealed >= double


def test_shade_dominates_and_roof_choice_is_secondary():
    rows = {r['design']: r for r in compare_designs()}
    open_sun = rows['Open sun (no shelter)']['tmrt_c']
    shed = rows['Weathered GI / cement sheet (typical existing shed)']['tmrt_c']
    saaya = rows['SAAYA double roof (white top, ventilated gap, bare low-e lining)']['tmrt_c']
    assert rows['Open sun (no shelter)']['sun_on_head'] and not rows['Weathered GI / cement sheet (typical existing shed)']['sun_on_head']
    assert open_sun - saaya > 10            # shade is the main mechanism
    assert 0 < shed - saaya < open_sun - saaya  # roof treatment helps, but less than shade itself


def test_overhang_monotonic_and_second_skin_reported():
    t = [r['tmrt_c'] for r in overhang_study()]
    assert all(a > b for a, b in zip(t, t[1:]))
    rows = second_skin_value()
    assert all(r['double_underside_c'] < r['single_underside_c'] for r in rows)
    # The upper skin matters more as the top coat soils.
    gains = [r['tmrt_saved_by_second_skin_k'] for r in rows]
    assert gains == sorted(gains)


def test_globe_inversion_round_trip():
    tg = globe_temperature(55.0, 38.0, 0.5)
    assert 38.0 < tg < 55.0
    c = 1.1e8 * 0.5**0.6 / (0.95 * 0.15**0.4)
    tmrt = ((tg + 273.15) ** 4 + c * (tg - 38.0)) ** 0.25 - 273.15
    assert tmrt == pytest.approx(55.0, abs=1e-4)


def test_swinbank_sky_is_colder_than_air():
    assert sky_temperature_k(38.0) < 38.0 + 273.15


def test_report_is_labelled_as_screening():
    r = report()
    assert 'SCREENING' in r['status'] and 'not validated' in r['status']
    assert r['falsification']


def test_plate_view_factor_limits():
    assert rectangle_view_factor(0, 0, -1e6, 1e6, -1e6, 1e6, 2.0) == pytest.approx(1.0, abs=1e-5)
    # Catalogue value: unit square, plate at a corner, distance 1 -> 0.1385
    assert rectangle_view_factor(0, 0, 0, 1, 0, 1, 1.0) == pytest.approx(0.1385, abs=5e-4)


def test_convection_is_convective_only():
    # Watmuff 2.8 + 3.0 v, not McAdams' combined 5.7 + 3.8 v (radiation is explicit).
    assert h_conv(0) == 2.8 and h_conv(1) == pytest.approx(5.8)


def test_may_noon_sun_is_north_of_zenith_in_vellore():
    elev, north = solar_noon(Conditions(day_of_year=135))
    assert north and 83 < elev < 86
    elev, north = solar_noon(Conditions(day_of_year=355))
    assert not north and elev < 60


def test_globe_uses_black_globe_absorptance():
    # A black globe absorbs more sunlight than a person; its prediction must sit above
    # the globe reading implied by the person's MRT.
    m = mean_radiant_temperature(Conditions(), Roof(kind='none'), Person())
    assert m['globe_150mm_c'] > globe_temperature(m['tmrt_c'], Conditions().ta_c, Person().air_speed)


def test_headline_is_additive_not_double_counted():
    h = headline(compare_designs())
    assert h['shade_alone_k'] + h['roof_treatment_k'] == pytest.approx(h['total_k'])
    assert h['shade_alone_k'] > h['roof_treatment_k'] > 0


def test_prediction_bands_bracket_nominal_and_underside_discriminates():
    bands = {b['target']: b for b in prediction_bands()}
    rows = {r['design']: r for r in compare_designs()}
    lo, hi = bands['SAAYA double roof']['underside_c']
    assert lo <= rows['SAAYA double roof (white top, ventilated gap, bare low-e lining)']['underside_c'] <= hi
    # Underside bands do not overlap: the cheapest measurement can tell the designs apart.
    assert hi < bands['Weathered shed sheet']['underside_c'][0]
