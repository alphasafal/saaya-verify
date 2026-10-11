import pytest
from api.physical import evaluate_physical
from api.core import scenario

def trial():
    rows=[]
    for i in range(600):
        r=scenario('normal',1)[i%60].copy();r.update(source='MEASURED',session_id='physical-test-fixture',seq=i,acquired_ms=i*1000,emitted_ms=i*1000,calibration_id='test-cal',config_id='test-config');rows.append(r)
    meta=dict(endpoint='roof_temp',reference_id='test-reference',calibration_id='test-cal',config_id='test-config',settling_seconds=600,declared_at='2026-01-01T09:00:00+00:00',started_at='2026-01-01T09:10:00+00:00',instrument_uncertainty='Fixture only; not a real calibration')
    return rows,meta

def test_physical_protocol_accepts_complete_fixture():
    rows,meta=trial();result=evaluate_physical(rows,meta)
    assert result['status']=='OBSERVED' and result['coverage']==1
    assert result['delta']==pytest.approx(-6)

def test_physical_rejects_unverified_calibration():
    rows,meta=trial();rows[0]['calibration_id']='UNVERIFIED'
    assert evaluate_physical(rows,meta)['status']=='INVALID'

def test_physical_insufficient_data():
    rows,meta=trial();assert evaluate_physical(rows[:500],meta)['status']=='INVALID'

def test_physical_rejects_simulation():
    rows,meta=trial();rows[0]['source']='SIMULATED';assert evaluate_physical(rows,meta)['status']=='INVALID'

def test_physical_predeclaration_and_settling():
    rows,meta=trial();meta['settling_seconds']=0
    assert evaluate_physical(rows,meta)['status']=='INVALID'
