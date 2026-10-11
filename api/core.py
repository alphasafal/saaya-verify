"""Synthetic demonstrator coefficients are illustrative, not a thermal model."""
import math
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field
SCENARIOS=('normal','humid','fan_failure','sensor_failure','low_water','no_power','reference_mismatch')
class Sample(BaseModel):
    model_config=ConfigDict(allow_inf_nan=False,extra='forbid')
    schema_version:int=1
    device_id:str='saaya-sim'
    session_id:str
    config_id:str='tabletop-v2'
    calibration_id:str='SIMULATED-NOT-CALIBRATED'
    seq:int=Field(ge=0)
    source:Literal['SIMULATED','MEASURED']
    acquired_ms:int=Field(ge=0)
    emitted_ms:int=Field(ge=0)
    temp:float|None=Field(default=None,ge=-40,le=125)
    rh:float|None=Field(default=None,ge=0,le=100)
    outdoor_temp:float|None=None
    outdoor_rh:float|None=Field(default=None,ge=0,le=100)
    roof_temp:float|None=None
    ref_roof:float|None=None
    air_speed:float|None=Field(default=None,ge=0)
    ref_air_speed:float|None=Field(default=None,ge=0)
    watts:float|None=Field(default=None,ge=0)
    rpm:float|None=Field(default=None,ge=0)
    duty:float=Field(default=0,ge=0,le=100)
    water:Literal['available','low','unknown']='unknown'
    help:bool=False
    quality:Literal['valid','invalid','stale','unavailable']='valid'
    fan_fault:bool=False
    clock_aligned:bool=False
    reference_valid:bool=False

def scenario(name,seed=1):
    if name not in SCENARIOS:raise ValueError('Unknown scenario')
    result=[]
    for i in range(60):
        n=math.sin(i*.37+seed)*.15
        r=dict(session_id=f'sim-{name}-{seed}',seq=i,source='SIMULATED',acquired_ms=i*1000,emitted_ms=i*1000,temp=33+n,rh=48+n,outdoor_temp=36+n,outdoor_rh=48+n,roof_temp=35+n,ref_roof=41+n,air_speed=1.2+n/10,ref_air_speed=.2,watts=1.4,rpm=3000,duty=70,water='available',quality='valid',clock_aligned=True,reference_valid=True)
        if name=='humid':r.update(rh=82+n,outdoor_rh=82+n,temp=34+n)
        if name=='fan_failure' and i>=20:r.update(rpm=0,air_speed=.2,fan_fault=True)
        if name=='sensor_failure' and i>=20:r.update(temp=None,rh=None,quality='invalid',duty=0,rpm=0)
        if name=='low_water' and i>=20:r['water']='low'
        if name=='no_power':r['watts']=None
        if name=='reference_mismatch' and i>=20:r['reference_valid']=False
        result.append(Sample(**r).model_dump())
    return result

def control(prev,inputs):
    now=inputs.get('now_ms',0);help_latched=bool((prev.get('help',False) and not inputs.get('ack',False)) or inputs.get('help',False))
    duty=70 if inputs.get('manual') else (50 if inputs.get('auto') and not inputs.get('fault') else 0)
    started=prev.get('started',now) if prev.get('duty',0)>0 and duty>0 else now
    fault=bool(duty>0 and now-started>=3000 and (inputs.get('rpm') is None or inputs['rpm']<100))
    return dict(help=help_latched,duty=duty,started=started,fan_fault=fault)

def energy(rows):
    groups={};total=0;valid=0;span=0
    for r in rows:groups.setdefault((r['device_id'],r['session_id']),[]).append(r)
    for group in groups.values():
        ordered=sorted(group,key=lambda r:r['seq'])
        for a,b in zip(ordered,ordered[1:]):
            dt=(b['acquired_ms']-a['acquired_ms'])/1000
            if dt<=0:continue
            span+=dt
            if dt>2 or b['seq']!=a['seq']+1 or a['watts'] is None or b['watts'] is None:continue
            total+=(a['watts']+b['watts'])/2*dt/3600;valid+=dt
    return dict(wh=total if valid else None,coverage=valid/span if span else 0,valid_seconds=valid,total_seconds=span,method='Per-device/session trapezoidal integration; gaps >2 s excluded')

def evaluate(rows,endpoint='roof_temp'):
    reasons=[];delta=None
    if endpoint not in ('roof_temp','air_speed'):raise ValueError('Unknown endpoint')
    if len(rows)<48:reasons.append('Insufficient coverage: at least 48 of 60 samples required')
    sources=sorted(set(r['source'] for r in rows))
    if len(sources)!=1:reasons.append('Missing or mixed data sources')
    if len(set(r['session_id'] for r in rows))>1:reasons.append('Mixed sessions')
    if len(set(r['config_id'] for r in rows))>1:reasons.append('Mixed configurations')
    ref='ref_roof' if endpoint=='roof_temp' else 'ref_air_speed'
    if any(r['quality']!='valid' or r['emitted_ms']-r['acquired_ms']>5000 for r in rows):reasons.append('Invalid or stale sensor data')
    if any(not r['clock_aligned'] or not r['reference_valid'] for r in rows):reasons.append('Unaligned or mismatched reference conditions')
    if any(r[endpoint] is None or r[ref] is None for r in rows):reasons.append('Required endpoint or reference measurement unavailable')
    if endpoint=='air_speed' and any(r['fan_fault'] for r in rows):reasons.append('Fan feedback fault: requested intervention not confirmed')
    ordered=sorted(rows,key=lambda r:r['seq'])
    if any(b['seq']<=a['seq'] or b['acquired_ms']<=a['acquired_ms'] or b['acquired_ms']-a['acquired_ms']>2000 for a,b in zip(ordered,ordered[1:])):reasons.append('Duplicate, disordered or gapped observation times')
    if not reasons:delta=sum(r[endpoint]-r[ref] for r in rows)/len(rows)
    return dict(status='INVALID' if reasons else 'OBSERVED',endpoint=endpoint,unit='°C' if endpoint=='roof_temp' else 'm/s',delta=delta,sources=sources,reasons=reasons,sample_count=len(rows),energy=energy(rows),uncertainty='Not established: independent repeated runs required',interpretation='Descriptive paired difference only; not a safety or human-recovery assessment',method='Mean intervention minus simultaneous reference; synthetic coefficients are illustrative')
