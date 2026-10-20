"""Evaluate one measured paired trial, or combine several finished trials.

  python scripts/evaluate_physical.py paired-records.json metadata.json --output result.json
  python scripts/evaluate_physical.py --aggregate day1-run1.json day2-run1.json day3-run1.json --output study.json
"""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from api.physical import evaluate_physical
from api.core import aggregate
p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('inputs',nargs='+',help='samples.json metadata.json, or with --aggregate: finished result files')
p.add_argument('--aggregate',action='store_true',help='combine independent finished results (one per run)')
p.add_argument('--output',required=True);a=p.parse_args()
if a.aggregate:
    r=aggregate([json.loads(Path(x).read_text()) for x in a.inputs])
    Path(a.output).write_text(json.dumps(r,indent=2));print(r['outcome']);print(r.get('reason',''))
else:
    if len(a.inputs)!=2:p.error('expected samples.json and metadata.json')
    r=evaluate_physical(json.loads(Path(a.inputs[0]).read_text()),json.loads(Path(a.inputs[1]).read_text()))
    Path(a.output).write_text(json.dumps(r,indent=2));print(r['status'],r['outcome']);print('\n'.join(r['reasons']))
