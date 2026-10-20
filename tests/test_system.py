import math
import pytest
from fastapi.testclient import TestClient
from api.core import Sample, scenario, evaluate, energy, control
from api.main import create_app

@pytest.mark.parametrize('field,value',[('rh',101),('rh',-1),('temp',float('nan')),('watts',-2),('rpm',float('inf')),('seq',-1)])
def test_reject_bad_measurement(field,value):
    data=scenario('normal',1)[0];data[field]=value
    with pytest.raises(ValueError):Sample(**data)

def test_seed_reproducibility():
    assert scenario('normal',9)==scenario('normal',9)
    assert scenario('normal',9)!=scenario('normal',8)

@pytest.mark.parametrize('name',['normal','humid','fan_failure','sensor_failure','low_water','no_power','reference_mismatch'])
def test_scenario_sources(name):
    rows=scenario(name,1)
    assert len(rows)==60 and all(Sample(**r).source=='SIMULATED' for r in rows)

def test_fan_fault_blocks_evidence():
    r=evaluate(scenario('fan_failure',1),'air_speed')
    assert r['status']=='INVALID' and any('feedback' in x for x in r['reasons'])

def test_mixed_sources_blocked():
    rows=scenario('normal',1);rows[1]['source']='MEASURED'
    assert evaluate(rows,'roof_temp')['status']=='INVALID'

def test_no_fake_real_reference():
    rows=scenario('normal',1)
    for r in rows:r.update(source='MEASURED',ref_roof=None,clock_aligned=False)
    assert evaluate(rows,'roof_temp')['status']=='INVALID'

def test_reference_mismatch():
    assert evaluate(scenario('reference_mismatch',1),'roof_temp')['status']=='INVALID'

def test_no_power_is_not_zero():
    e=energy(scenario('no_power',1))
    assert e['wh'] is None and e['coverage']==0

def test_gap_not_integrated():
    rows=scenario('normal',1)
    rows=[r for r in rows if r['seq'] not in range(5,50)]
    assert energy(rows)['coverage']<.3

def test_reboot_does_not_bridge_energy():
    rows=scenario('normal',1);a=energy(rows)['wh'];rows[30]['session_id']='newboot'
    assert energy(rows)['wh']<a

def test_positive_result_is_not_safety():
    r=evaluate(scenario('normal',1),'roof_temp')
    assert r['status']=='OBSERVED' and r['delta']<0
    assert r['uncertainty'].startswith('Not established: independent repeated runs')

def test_control_help_and_override():
    state=control({}, {'help':True,'fault':True,'manual':True,'now_ms':0})
    assert state['help'] and state['duty']==70
    state=control(state, {'fault':False,'manual':False,'now_ms':1000})
    assert state['help']
    assert not control(state,{'ack':True,'now_ms':2000})['help']

def test_idle_and_startup_not_fault():
    assert not control({}, {'now_ms':0,'rpm':0})['fan_fault']
    s=control({}, {'manual':True,'now_ms':0,'rpm':0})
    assert not s['fan_fault']
    assert control(s, {'manual':True,'now_ms':5000,'rpm':0})['fan_fault']

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(str(tmp_path/'test.db'),token='test-token')) as c:yield c

def test_real_ingestion_auth_and_dedup(client):
    r=scenario('normal',1)[0];r['source']='MEASURED'
    assert client.post('/telemetry',json=r).status_code==401
    h={'X-Device-Token':'test-token'}
    assert client.post('/telemetry',json=r,headers=h).json()['inserted']
    assert not client.post('/telemetry',json=r,headers=h).json()['inserted']
    r['session_id']='newboot'
    assert client.post('/telemetry',json=r,headers=h).json()['inserted']

def test_complete_workflow(client):
    run=client.post('/sim/scenario',json={'name':'fan_failure','seed':4}).json()
    exp=client.post('/experiments',json={'run_id':run['run_id'],'endpoint':'air_speed'}).json()
    assert client.post('/sim/step',json={'run_id':run['run_id'],'count':60}).status_code==200
    result=client.post('/experiments/'+exp['id']+'/finish').json()
    assert result['evidence']['status']=='INVALID'
    url='/experiments/'+exp['id']+'/export'
    export=client.get(url).json();assert len(export['samples'])==60
    assert client.get(url+'?format=csv').headers['content-type'].startswith('text/csv')
    assert client.post('/experiments/'+exp['id']+'/finish').json()==result

def test_reset_preserves_experiment(client):
    run=client.post('/sim/scenario',json={'name':'normal'}).json()
    exp=client.post('/experiments',json={'run_id':run['run_id'],'endpoint':'roof_temp'}).json()
    other=client.post('/sim/scenario',json={'name':'normal'}).json()
    client.post('/sim/step',json={'run_id':other['run_id'],'count':60})
    result=client.post('/experiments/'+exp['id']+'/finish').json()
    assert result['evidence']['status']=='INVALID'

def test_declared_before_collection(client):
    r=client.post('/sim/scenario',json={'name':'normal'}).json()
    client.post('/sim/step',json={'run_id':r['run_id'],'count':10})
    assert client.post('/experiments',json={'run_id':r['run_id'],'endpoint':'roof_temp'}).status_code==409

def test_bad_scenario_and_missing_experiment(client):
    assert client.post('/sim/scenario',json={'name':'bogus'}).status_code==422
    assert client.get('/experiments/missing').status_code==404
    assert client.get('/history?limit=1000000').status_code==422

def test_no_external_ai_by_default(client):
    assert client.get('/analysis/status').json()['ai_enabled'] is False
