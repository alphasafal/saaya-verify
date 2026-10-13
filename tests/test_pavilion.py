from pathlib import Path
import json
R=Path(__file__).parents[1]
def test_pavilion_capacity_and_explicit_release_boundary():
 d=json.loads((R/'site/pavilion/assembly.json').read_text())
 ids=[p['id'] for p in d['parts']]
 assert len(ids)==len(set(ids))
 assert len([i for i in ids if i.startswith('cot_')])==5
 assert len([i for i in ids if i.startswith('fan_')])==5
 assert d['front_entry_clear_mm']==1600 and d['central_clear_strip_mm']==1300
 assert 'NOT FOR FABRICATION' in d['status']
 for p in d['parts']:
  assert (R/'site/pavilion'/f"{p['id']}.stl").stat().st_size>84
  assert len(p['why'])>20 and len(p['limit'])>20

def test_pavilion_health_and_cost_boundaries():
 s=(R/'site/rest-pavilion.html').read_text()
 for text in ['A table fan is the lower-cost baseline','five-zone firmware is not implemented','No BP sensor','collects no physiological readings','same basic airflow mechanism']:
  assert text in s
