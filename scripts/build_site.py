"""Assemble a static site from tested simulation outputs and original project assets."""
from pathlib import Path
import sys,json,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from api.core import scenario,evaluate,aggregate,SCENARIOS
from api import thermal
site=ROOT/'site';(site/'data').mkdir(exist_ok=True);(site/'downloads').mkdir(exist_ok=True)
for name in SCENARIOS:
    rows=scenario(name,1)
    (site/'data'/f'{name}.json').write_text(json.dumps({'name':name,'source':'SIMULATED','seed':1,'samples':rows,'evidence':{e:evaluate(rows,e) for e in ['roof_temp','air_speed']}},indent=2))
(site/'data'/'thermal-model.json').write_text(json.dumps(thermal.report(),indent=1))
# Cross-run method demonstration: five synthetic 'days' (seeds), one run each.
runs={e:[evaluate(scenario('normal',seed),e) for seed in (1,2,3,4,5)] for e in ['roof_temp','air_speed']}
(site/'data'/'aggregate-demo.json').write_text(json.dumps({'source':'SIMULATED','seeds':[1,2,3,4,5],'results':{e:aggregate(r) for e,r in runs.items()}},indent=1))
for name in ['evidence.json','costs.json']:
    if (ROOT/'research'/name).exists():shutil.copyfile(ROOT/'research'/name,site/'data'/name)
for name in ['SAAYA_Phase_2_Design_Pack.pdf','sheet-1.png']:
    shutil.copyfile(ROOT/'archive/lab-v1'/name,site/'downloads'/name)
for name in ['README.md','docs/engineering.md','docs/architecture-v2.svg','docs/physical-protocol.md','docs/verification.md','docs/DEFENSE.md','research/REVIEW.md','firmware/src/main.cpp']:
    if (ROOT/name).exists():shutil.copyfile(ROOT/name,site/'downloads'/Path(name).name)
if (ROOT/'cad/exports').exists():
    for p in (ROOT/'cad/exports').iterdir():
        if p.is_file():shutil.copyfile(p,site/'downloads'/p.name)
print('Static scenarios and downloads built from project sources')
