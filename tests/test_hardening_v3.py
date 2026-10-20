"""Regression tests for the v0.3 review: each test names the flaw it pins down."""
import gc
import math
import sqlite3
import warnings
import pytest
from fastapi.testclient import TestClient
from api.core import Sample, scenario, evaluate, aggregate, declaration_for, classify, paired_statistics, auto_request
from api.main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(str(tmp_path / 'v3.db'), token='t')) as c:
        yield c


def finished(client, name, seed, endpoint, margin=None):
    run = client.post('/sim/scenario', json={'name': name, 'seed': seed}).json()
    body = {'run_id': run['run_id'], 'endpoint': endpoint}
    if margin is not None:
        body['margin'] = margin
    exp = client.post('/experiments', json=body).json()
    client.post('/sim/step', json={'run_id': run['run_id'], 'count': 60})
    client.post('/experiments/' + exp['id'] + '/finish')
    return exp['id']


# Flaw: every request leaked a SQLite connection (sqlite3's context manager never closes).
def test_no_leaked_database_connections(tmp_path):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always', ResourceWarning)
        with TestClient(create_app(str(tmp_path / 'leak.db'), token='t')) as c:
            finished(c, 'normal', 1, 'roof_temp')
            c.get('/latest'); c.get('/history')
        gc.collect()
    assert not [w for w in caught if issubclass(w.category, ResourceWarning) and 'sqlite' in str(w.message).lower()]


def test_wal_mode_enabled(tmp_path):
    with TestClient(create_app(str(tmp_path / 'wal.db'), token='t')):
        pass
    con = sqlite3.connect(tmp_path / 'wal.db')
    try:
        assert con.execute('PRAGMA journal_mode').fetchone()[0] == 'wal'
    finally:
        con.close()


# Flaw: roof/outdoor/air-speed fields had no physical bounds; a corrupted frame could store 9e9 °C.
@pytest.mark.parametrize('field,value', [('roof_temp', 500), ('ref_roof', -100), ('outdoor_temp', 200),
                                         ('air_speed', 99), ('watts', 1e6), ('rpm', 1e6)])
def test_implausible_values_rejected(field, value):
    data = scenario('normal', 1)[0]
    data[field] = value
    with pytest.raises(ValueError):
        Sample(**data)


# Flaw: a device holding the token could inject SIMULATED rows into the simulation namespace.
def test_device_endpoint_accepts_measured_only(client):
    row = scenario('normal', 1)[0]
    assert client.post('/telemetry', json=row, headers={'X-Device-Token': 't'}).status_code == 422


# Flaw: the spec requires three outcomes (difference / no clear difference / invalid) and a
# predeclared beneficial direction; the evaluator only ever said OBSERVED or INVALID.
def test_outcome_uses_predeclared_direction_and_margin():
    rows = scenario('normal', 1)
    assert evaluate(rows, 'roof_temp')['outcome'] == 'DIFFERENCE_IN_DECLARED_DIRECTION'
    assert evaluate(rows, 'roof_temp', declaration_for('roof_temp', margin=50))['outcome'] == 'NO_CLEAR_DIFFERENCE'
    # Swap intervention and reference: the same data now shows harm, and says so.
    flipped = [dict(r, roof_temp=r['ref_roof'], ref_roof=r['roof_temp']) for r in rows]
    assert evaluate(flipped, 'roof_temp')['outcome'] == 'DIFFERENCE_AGAINST_DECLARED_DIRECTION'
    assert evaluate(scenario('fan_failure', 1), 'air_speed')['outcome'] == 'INVALID'
    assert classify(0.0, declaration_for('air_speed')) == 'NO_CLEAR_DIFFERENCE'


def test_bad_margin_rejected():
    for bad in (0, -1, float('nan'), float('inf')):
        with pytest.raises(ValueError):
            declaration_for('roof_temp', bad)


def test_within_run_autocorrelation_reported():
    s = paired_statistics([math.sin(i * .37) for i in range(60)])
    assert s['lag1_autocorrelation'] > 0.5 and s['n_effective'] < s['n'] / 3
    assert paired_statistics([1.0])['sd'] is None


# Flaw: "uncertainty not established" was permanent; there was no method to establish it.
def test_cross_run_aggregation_needs_independent_runs(client):
    ids = [finished(client, 'normal', seed, 'roof_temp') for seed in (1, 2, 3, 4, 5)]
    res = client.post('/evidence/aggregate', json={'experiment_ids': ids}).json()
    assert res['runs_valid'] == 5 and res['ci95'][0] < res['mean'] < res['ci95'][1]
    assert res['outcome'] == 'DIFFERENCE_IN_DECLARED_DIRECTION' and 'warning' in res
    two = client.post('/evidence/aggregate', json={'experiment_ids': ids[:2]}).json()
    assert two['outcome'] == 'UNCERTAINTY_NOT_ESTABLISHED' and two['ci95'] is None
    assert client.post('/evidence/aggregate', json={'experiment_ids': [ids[0], ids[0]]}).status_code == 422
    mixed = finished(client, 'normal', 6, 'air_speed')
    assert client.post('/evidence/aggregate', json={'experiment_ids': ids[:3] + [mixed]}).status_code == 422
    margin = finished(client, 'normal', 7, 'roof_temp', margin=3)
    assert client.post('/evidence/aggregate', json={'experiment_ids': ids[:3] + [margin]}).status_code == 422


def test_invalid_runs_are_counted_not_dropped(client):
    ids = [finished(client, 'normal', s, 'roof_temp') for s in (1, 2, 3)]
    ids.append(finished(client, 'reference_mismatch', 4, 'roof_temp'))
    res = client.post('/evidence/aggregate', json={'experiment_ids': ids}).json()
    assert res['runs_invalid'] == 1 and res['runs_valid'] == 3 and 'note' in res


def test_equivalence_and_inconclusive_logic():
    d = declaration_for('roof_temp', margin=1.0)
    base = {'endpoint': 'roof_temp', 'sources': ['SIMULATED'], 'declaration': d, 'status': 'OBSERVED'}
    tight = [dict(base, delta=x, session_ids=[str(i)]) for i, x in enumerate([0.1, -0.1, 0.05, -0.05])]
    assert aggregate(tight)['outcome'] == 'EQUIVALENT_WITHIN_MARGIN'
    noisy = [dict(base, delta=x, session_ids=[str(i)]) for i, x in enumerate([-3, 2, -1.5])]
    assert aggregate(noisy)['outcome'] == 'INCONCLUSIVE'


def test_declaration_is_locked_into_the_record(client):
    run = client.post('/sim/scenario', json={'name': 'normal'}).json()
    exp = client.post('/experiments', json={'run_id': run['run_id'], 'endpoint': 'roof_temp', 'margin': 2.5}).json()
    assert exp['declaration']['margin'] == 2.5
    client.post('/sim/step', json={'run_id': run['run_id'], 'count': 60})
    rec = client.post('/experiments/' + exp['id'] + '/finish').json()
    assert rec['evidence']['declaration']['margin'] == 2.5


def test_old_database_is_migrated(tmp_path):
    path = tmp_path / 'old.db'
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE experiments(id TEXT PRIMARY KEY,run TEXT,endpoint TEXT,result TEXT)')
    con.commit(); con.close()
    with TestClient(create_app(str(path), token='t')) as c:
        assert finished(c, 'normal', 1, 'roof_temp')


# Flaw: a single 32 °C threshold makes an automatic fan chatter around the set point.
def test_auto_fan_hysteresis():
    assert not auto_request(False, 31.9) and auto_request(False, 32.0)
    assert auto_request(True, 31.2) and not auto_request(True, 30.9)
    assert not auto_request(True, None) and not auto_request(False, float('nan'))


def test_thermal_model_endpoint(client):
    r = client.get('/model/thermal').json()
    assert 'SCREENING' in r['status'] and len(r['designs']) >= 6


def test_physical_cli_single_and_aggregate(tmp_path):
    import json, subprocess, sys
    from tests.test_physical import trial
    outs = []
    for day in range(3):
        rows, meta = trial()
        for r in rows:
            r['session_id'] = f'day{day}'
        (tmp_path / f's{day}.json').write_text(json.dumps(rows)); (tmp_path / f'm{day}.json').write_text(json.dumps(meta))
        out = tmp_path / f'r{day}.json'
        subprocess.run([sys.executable, 'scripts/evaluate_physical.py', str(tmp_path / f's{day}.json'), str(tmp_path / f'm{day}.json'), '--output', str(out)], check=True)
        outs.append(str(out))
    study = tmp_path / 'study.json'
    subprocess.run([sys.executable, 'scripts/evaluate_physical.py', '--aggregate', *outs, '--output', str(study)], check=True)
    res = json.loads(study.read_text())
    assert res['source'] == 'MEASURED' and res['runs_valid'] == 3 and res['ci95'] is not None
