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
    # Physical plausibility bounds = sensor operating ranges (SHT31/DS18B20: -40..125 C).
    outdoor_temp:float|None=Field(default=None,ge=-40,le=125)
    outdoor_rh:float|None=Field(default=None,ge=0,le=100)
    roof_temp:float|None=Field(default=None,ge=-40,le=125)
    ref_roof:float|None=Field(default=None,ge=-40,le=125)
    air_speed:float|None=Field(default=None,ge=0,le=30)
    ref_air_speed:float|None=Field(default=None,ge=0,le=30)
    watts:float|None=Field(default=None,ge=0,le=500)
    rpm:float|None=Field(default=None,ge=0,le=30000)
    duty:float=Field(default=0,ge=0,le=100)
    water:Literal['available','low','unknown']='unknown'
    help:bool=False
    quality:Literal['valid','invalid','stale','unavailable']='valid'
    fan_fault:bool=False
    fan_advice:Literal['ok','caution','avoid','unknown']|None=None
    clock_aligned:bool=False
    reference_valid:bool=False

def scenario(name,seed=1):
    if name not in SCENARIOS:raise ValueError('Unknown scenario')
    result=[]
    # Deterministic run-to-run variation (synthetic "different day"), so that the
    # cross-run statistics in aggregate() have something honest to estimate.
    day_roof=.8*math.sin(seed*2.3);day_air=.12*math.sin(seed*1.3+.5)
    for i in range(60):
        n=math.sin(i*.37+seed)*.15
        r=dict(session_id=f'sim-{name}-{seed}',seq=i,source='SIMULATED',acquired_ms=i*1000,emitted_ms=i*1000,temp=33+n,rh=48+n,outdoor_temp=36+n,outdoor_rh=48+n,roof_temp=35+n+day_roof,ref_roof=41+n,air_speed=1.2+n/10+day_air,ref_air_speed=.2,watts=1.4,rpm=3000,duty=70,water='available',quality='valid',clock_aligned=True,reference_valid=True)
        if name=='humid':r.update(rh=82+n,outdoor_rh=82+n,temp=34+n)
        if name=='fan_failure' and i>=20:r.update(rpm=0,air_speed=.2,fan_fault=True)
        if name=='sensor_failure' and i>=20:r.update(temp=None,rh=None,quality='invalid',duty=0,rpm=0)
        if name=='low_water' and i>=20:r['water']='low'
        if name=='no_power':r['watts']=None
        if name=='reference_mismatch' and i>=20:r['reference_valid']=False
        result.append(Sample(**r).model_dump())
    return result

AUTO_ON_C=32.0;AUTO_OFF_C=31.0  # bench demonstration band, not an occupational threshold
# Fan-benefit screen, mirrors firmware/include/controller.h. Sources: Morris et al. 2021 Lancet
# Planetary Health (ceilings 39/38/37 C by age/medication), WHO fact sheet (fans heat the body >40 C),
# Gagnon et al. 2016 JAMA (no benefit for older adults at 42 C). A screen, not a clinical rule.
FAN_CAUTION_C=37.0;FAN_AVOID_C=39.0;FAN_RESUME_C=38.5

def fan_advice(air_c):
    if air_c is None or not math.isfinite(air_c):return 'unknown'
    return 'avoid' if air_c>=FAN_AVOID_C else ('caution' if air_c>=FAN_CAUTION_C else 'ok')

def auto_request(prev_on,temp):
    """Hysteresis: start at >=32 C, keep running until <31 C. Automatic mode also stops at >=39 C,
    where a fan may add heat, and restarts only below 38.5 C. Manual mode is never blocked."""
    if temp is None or not math.isfinite(temp):return False
    return (AUTO_OFF_C<=temp<FAN_AVOID_C) if prev_on else (AUTO_ON_C<=temp<FAN_RESUME_C)

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

# Predeclared, endpoint-specific decision rules. The margin is the smallest difference we
# agree in advance to treat as meaningful. It is set above what the instruments could
# produce on their own: two probes each rated +/-0.5 C could disagree by up to ~1 C before
# the co-location swap removes their fixed offset, so 1.0 C; low-speed anemometers are
# typically ~+/-(0.05 m/s + 5 %), so 0.2 m/s.
DECLARATIONS={
    'roof_temp':{'beneficial_direction':'lower','margin':1.0,'unit':'°C','margin_basis':'Set above possible disagreement of two ±0.5 °C probes before offset correction; chosen before data collection'},
    'air_speed':{'beneficial_direction':'higher','margin':0.2,'unit':'m/s','margin_basis':'Typical low-speed anemometer accuracy ≈±(0.05 m/s + 5 %); 0.2 m/s chosen before data collection'},
}

def declaration_for(endpoint,margin=None):
    if endpoint not in DECLARATIONS:raise ValueError('Unknown endpoint')
    d=dict(DECLARATIONS[endpoint],endpoint=endpoint)
    if margin is not None:
        if not (isinstance(margin,(int,float)) and math.isfinite(margin) and margin>0):raise ValueError('Margin must be a positive finite number')
        d['margin']=float(margin);d['margin_basis']='Operator-declared before data collection'
    return d

def classify(delta,declaration):
    """ONE run's point estimate versus the predeclared direction and margin. A single run is
    never called a 'difference': that label is reserved for aggregate() over independent days."""
    sign=-1 if declaration['beneficial_direction']=='lower' else 1
    if delta*sign>=declaration['margin']:return 'POINT_ESTIMATE_IN_DECLARED_DIRECTION'
    if delta*sign<=-declaration['margin']:return 'POINT_ESTIMATE_AGAINST_DECLARED_DIRECTION'
    return 'POINT_ESTIMATE_WITHIN_MARGIN'

def paired_statistics(diffs):
    """Descriptive statistics of within-run paired differences. Consecutive 1 s samples are
    autocorrelated, so the effective sample size n_eff=n(1-r1)/(1+r1), clamped to [1, n], is
    reported to show why a within-run confidence interval would be false precision."""
    n=len(diffs)
    if n<2:return {'n':n,'mean':diffs[0] if diffs else None,'sd':None,'lag1_autocorrelation':None,'n_effective':None}
    m=sum(diffs)/n;den=sum((x-m)**2 for x in diffs);sd=math.sqrt(den/(n-1))
    out={'n':n,'mean':m,'sd':sd,'min':min(diffs),'max':max(diffs)}
    if sd<=1e-9*max(1.0,abs(m)):  # constant series: autocorrelation is undefined, not 0.98 from rounding noise
        out.update(lag1_autocorrelation=None,n_effective=None);return out
    r1=sum((a-m)*(b-m) for a,b in zip(diffs,diffs[1:]))/den
    out.update(lag1_autocorrelation=r1,n_effective=min(n,max(1.0,n*(1-r1)/(1+r1))));return out

def evaluate(rows,endpoint='roof_temp',declaration=None,day=None):
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
    declaration=declaration or declaration_for(endpoint)
    if declaration.get('endpoint',endpoint)!=endpoint:reasons.append('Declaration does not match endpoint')
    stats=None
    if not reasons:
        diffs=[r[endpoint]-r[ref] for r in ordered];delta=sum(diffs)/len(diffs);stats=paired_statistics(diffs)
    outcome='INVALID' if reasons else classify(delta,declaration)
    return dict(status='INVALID' if reasons else 'OBSERVED',outcome=outcome,declaration=declaration,endpoint=endpoint,unit='°C' if endpoint=='roof_temp' else 'm/s',delta=delta,paired_statistics=stats,sources=sources,session_ids=sorted(set(r['session_id'] for r in rows)),day=day,reasons=reasons,sample_count=len(rows),energy=energy(rows),uncertainty='Not established: independent repeated runs on separate days required',interpretation='Single-run descriptive paired difference; not a safety or human-recovery assessment',method='Mean intervention minus simultaneous reference; synthetic coefficients are illustrative')

# Two-sided 95 % Student-t critical values, df 1..30 (standard table).
_T95=[12.706,4.303,3.182,2.776,2.571,2.447,2.365,2.306,2.262,2.228,2.201,2.179,2.160,2.145,2.131,2.120,2.110,2.101,2.093,2.086,2.080,2.074,2.069,2.064,2.060,2.056,2.052,2.048,2.045,2.042]

def t95(df):return _T95[df-1] if df<=30 else 1.96+2.4/df

def aggregate(results,min_runs=3):
    """Combine independent runs (one run = one unit of replication). Uses run means only, never
    pooled samples. Runs must come from at least `min_runs` distinct days, because runs on the same
    afternoon share weather and are not independent. Decision is equivalence-style against the
    predeclared margin using a two-sided 95 % CI (stricter than the 90 % CI of a standard TOST):
    a direction is claimed only if the whole interval clears the margin."""
    if not results:raise ValueError('No runs supplied')
    endpoints={r['endpoint'] for r in results};sources={tuple(r['sources']) for r in results}
    decls={(r['declaration']['beneficial_direction'],r['declaration']['margin']) for r in results}
    if len(endpoints)!=1:raise ValueError('Runs mix endpoints')
    if len(sources)!=1:raise ValueError('Runs mix SIMULATED and MEASURED sources')
    if len(decls)!=1:raise ValueError('Runs used different predeclared directions or margins')
    sessions=[s for r in results for s in r.get('session_ids',[])]
    if len(sessions)!=len(set(sessions)):raise ValueError('The same acquisition session appears twice; runs are not independent')
    valid=[r for r in results if r['status']=='OBSERVED'];invalid=len(results)-len(valid)
    decl=dict(results[0]['declaration']);deltas=[r['delta'] for r in valid];n=len(deltas)
    days=sorted({r.get('day') for r in valid if r.get('day')})
    out={'endpoint':results[0]['endpoint'],'source':results[0]['sources'][0] if results[0]['sources'] else None,'declaration':decl,'runs_supplied':len(results),'runs_valid':n,'runs_invalid':invalid,'valid_fraction':n/len(results),'distinct_days':len(days),'run_deltas':deltas,'method':'Mean of independent run-level paired differences (≥3 distinct days); Student-t two-sided 95 % CI; equivalence-style decision against predeclared margin'}
    if invalid:out['note']='Invalid runs are reported in runs_invalid and valid_fraction, not silently dropped'
    reason=None
    if n<min_runs:reason=f'At least {min_runs} valid independent runs required; have {n}'
    elif any(not r.get('day') for r in valid):reason='Every run must record the day it was collected'
    elif len(days)<min_runs:reason=f'Runs must span at least {min_runs} distinct days; have {len(days)}'
    if reason:
        out.update(mean=sum(deltas)/n if n else None,sd=None,ci95=None,outcome='UNCERTAINTY_NOT_ESTABLISHED',reason=reason);return out
    m=sum(deltas)/n;sd=math.sqrt(sum((x-m)**2 for x in deltas)/(n-1));half=t95(n-1)*sd/math.sqrt(n);lo,hi=m-half,m+half
    sign=-1 if decl['beneficial_direction']=='lower' else 1;mar=decl['margin']
    blo,bhi=sorted((lo*sign,hi*sign))
    if blo>=mar:outcome='DIFFERENCE_IN_DECLARED_DIRECTION'
    elif bhi<=-mar:outcome='DIFFERENCE_AGAINST_DECLARED_DIRECTION'
    elif blo>-mar and bhi<mar:outcome='EQUIVALENT_WITHIN_MARGIN'
    else:outcome='INCONCLUSIVE'
    out.update(mean=m,sd=sd,ci95=[lo,hi],outcome=outcome)
    if out['source']=='SIMULATED':out['warning']='Synthetic runs demonstrate the method only; this is not evidence about a physical shelter'
    return out
