"""Offline measured-pair evaluation. Operator metadata is recorded, not independently certified."""
from datetime import datetime
from .core import Sample,energy

def evaluate_physical(records,metadata):
    rows=[Sample(**r).model_dump() for r in records];reasons=[]
    endpoint=metadata.get('endpoint')
    if endpoint not in ('roof_temp','air_speed'):raise ValueError('Endpoint must be roof_temp or air_speed')
    ref='ref_roof' if endpoint=='roof_temp' else 'ref_air_speed'
    for key in ['reference_id','calibration_id','config_id','instrument_uncertainty']:
        if not metadata.get(key) or metadata[key] in ('UNVERIFIED','SIMULATED-NOT-CALIBRATED'):reasons.append(f'Missing verified operator metadata: {key}')
    try:
        declared=datetime.fromisoformat(metadata['declared_at']);started=datetime.fromisoformat(metadata['started_at'])
        if not declared.tzinfo or not started.tzinfo or declared>started:raise ValueError()
    except (KeyError,ValueError,TypeError):reasons.append('Invalid predeclaration/start timestamps')
    if metadata.get('settling_seconds',0)<600:reasons.append('Minimum 600-second settling period not declared')
    if any(r['source']!='MEASURED' for r in rows):reasons.append('Non-measured source in physical trial')
    if any(r['calibration_id']!=metadata.get('calibration_id') or r['config_id']!=metadata.get('config_id') for r in rows):reasons.append('Configuration or calibration mismatch')
    if len({(r['device_id'],r['session_id']) for r in rows})!=1:reasons.append('Missing or mixed acquisition sessions')
    ordered=sorted(rows,key=lambda r:r['seq'])
    if len({r['seq'] for r in rows})!=len(rows):reasons.append('Duplicate sequences')
    if any(b['acquired_ms']<=a['acquired_ms'] for a,b in zip(ordered,ordered[1:])):reasons.append('Nonmonotonic acquisition clock')
    if ordered and ordered[-1]['acquired_ms']-ordered[0]['acquired_ms']>601000:reasons.append('Observation exceeds declared 600-second window')
    valid=[r for r in rows if r['quality']=='valid' and 0<=r['emitted_ms']-r['acquired_ms']<=5000 and r['clock_aligned'] and r['reference_valid'] and r[endpoint] is not None and r[ref] is not None]
    # Count unique 1-second acquisition bins; high-frequency bursts cannot masquerade as coverage.
    origin=min((r['acquired_ms'] for r in rows),default=0)
    valid=[r for r in valid if 0<=r['acquired_ms']-origin<600000]
    bins={int((r['acquired_ms']-origin)//1000) for r in valid};coverage=len(bins)/600
    if len(bins)!=len(valid):reasons.append('Multiple samples in a one-second bin violate declared cadence')
    if coverage<.9:reasons.append('Less than 90% paired coverage of the 600-second window')
    if endpoint=='air_speed' and any(r['fan_fault'] for r in rows):reasons.append('Fan feedback failure during air-speed intervention')
    delta=None if reasons else sum(r[endpoint]-r[ref] for r in valid)/len(valid)
    return {'status':'INVALID' if reasons else 'OBSERVED','endpoint':endpoint,'unit':'°C' if endpoint=='roof_temp' else 'm/s','delta':delta,'coverage':coverage,'excluded_samples':len(rows)-len(valid),'reasons':reasons,'energy':energy(rows),'metadata':metadata,'source':'MEASURED','uncertainty':'Independent-run uncertainty not established; instrument uncertainty is operator-supplied','limitation':'Metadata and calibration declarations are not independently certified. No human safety conclusion.'}
