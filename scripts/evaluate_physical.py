import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from api.physical import evaluate_physical
p=argparse.ArgumentParser();p.add_argument('samples',help='JSON array of paired canonical telemetry samples');p.add_argument('metadata',help='Predeclared physical protocol metadata JSON');p.add_argument('--output',required=True);a=p.parse_args()
r=evaluate_physical(json.loads(Path(a.samples).read_text()),json.loads(Path(a.metadata).read_text()))
Path(a.output).write_text(json.dumps(r,indent=2));print(r['status']);print('\n'.join(r['reasons']))
