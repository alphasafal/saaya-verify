from pathlib import Path
import json,math
import cadquery as cq
O=Path(__file__).resolve().parent/'exports';manifest=json.loads((O/'assembly.json').read_text());bom=json.loads((O/'bom.json').read_text());shapes={};errors=[]
for p in bom:
 s=cq.importers.importStep(str(O/(p['part']+'.step'))).val();shapes[p['part']]=s
 if not s.isValid() or s.Volume()<=0:errors.append(p['part'])
items=[]
for i in manifest['instances']:
 s=shapes[i['part']]
 if i.get('rotation_z'):s=s.rotate((0,0,0),(0,0,1),i['rotation_z'])
 if i.get('rotation_x'):s=s.rotate((0,0,0),(1,0,0),i['rotation_x'])
 s=s.translate(tuple(i['position']));items.append((i,s,s.BoundingBox()))
hits=[]
for n,(a,sa,ba) in enumerate(items):
 for b,sb,bb in items[n+1:]:
  if any(min(getattr(ba,k+'max'),getattr(bb,k+'max'))-max(getattr(ba,k+'min'),getattr(bb,k+'min'))<=0 for k in 'xyz'):continue
  v=sa.intersect(sb).Volume()
  if v>1:
   hardware=a['group'] in ['hardware','foundation'] or b['group'] in ['hardware','foundation']
   hits.append(dict(a=a['name'],b=b['name'],overlap_mm3=round(v,2),disposition='Fastener/connection interface: verify holes, seating and joint stack' if hardware else 'Resolve interference before fabrication'))
result=dict(status='REVIEW REQUIRED' if hits else 'NO SOLID INTERSECTIONS >1 mm3',checked_instances=len(items),invalid_reimported_parts=errors,intersection_threshold_mm3=1,intersections=hits,limitations='Includes deliberate unthreaded fastener/connection envelopes. Does not check hidden missing supports, tool access, tolerances, loads or assembly sequence. No automatic manufacturing approval.')
(O/'interference.json').write_text(json.dumps(result,indent=2));assert not errors,errors
print('Valid STEP parts:',len(shapes),'Intersections requiring disposition:',len(hits));print(json.dumps(hits[:25],indent=2))
