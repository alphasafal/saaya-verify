import pytest
from fastapi.testclient import TestClient
from api.main import create_app
from api.core import scenario, energy
from test_physical import trial
from api.physical import evaluate_physical

def test_energy_session_reset():
    a=scenario('normal'); b=[dict(r,session_id='second') for r in a]
    assert energy(a+b)['wh']==pytest.approx(2*energy(a)['wh'])

def test_burst_cannot_bias_physical_mean():
    rows,meta=trial()
    burst=[dict(rows[0],acquired_ms=i,emitted_ms=i,roof_temp=81) for i in range(1,1000)]
    rows=sorted(rows+burst,key=lambda r:r['acquired_ms'])
    for i,r in enumerate(rows):r['seq']=i
    assert evaluate_physical(rows,meta)['status']=='INVALID'

def test_backlog_is_stale(tmp_path,monkeypatch):
    now=[100.0];monkeypatch.setattr('api.main.time.time',lambda:now[0])
    c=TestClient(create_app(str(tmp_path/'test.db'),'test'))
    rows=scenario('normal');headers={'X-Device-Token':'test'}
    c.post('/telemetry',json=dict(rows[0],source='MEASURED'),headers=headers)
    now[0]=120
    c.post('/telemetry',json=dict(rows[1],source='MEASURED'),headers=headers)
    assert c.get('/latest').json()['stale'] is True

def test_fan_bracket_airway():
    import trimesh as tm
    from pathlib import Path
    m=tm.load_mesh(Path(__file__).parents[1]/'cad/exports/fan_angle_bracket.stl')
    probe=tm.creation.box([20,6,20]);probe.apply_translation([24,1.5,24])
    overlap=tm.boolean.intersection([m,probe],engine='manifold')
    assert len(overlap.faces)==0
