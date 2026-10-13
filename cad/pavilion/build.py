"""FS-02 five-person rest pavilion. Concept solids in mm; NOT a fabrication release."""
from pathlib import Path
import cadquery as cq
import json, math, shutil
R=Path(__file__).resolve().parent; O=R/'exports';O.mkdir(exist_ok=True)
A=cq.Assembly(name='SAAYA_FS02_CONCEPT_ONLY'); rows=[]
def box(x,y,z):return cq.Workplane('XY').box(x,y,z,centered=False).val()
def cyl(r,h,pos=(0,0,0),axis=(0,0,1)):return cq.Solid.makeCylinder(r,h,cq.Vector(*pos),cq.Vector(*axis))
def add(id,s,group,color,title,why,limit):
 assert s.isValid() and s.Volume()>0,id
 A.add(s,name=id,color=cq.Color(color));cq.exporters.export(s,str(O/(id+'.stl')),tolerance=1,angularTolerance=.2)
 b=s.BoundingBox();rows.append(dict(id=id,group=group,color=color,title=title,why=why,limit=limit,bounds=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]))
def compound(shapes):return cq.Compound.makeCompound(shapes)
# A slab is a site-space reservation, not a foundation design.
add('footprint',box(6000,5400,60).translate((0,0,-60)),'site','#c5b79c','6.0 × 5.4 m rest footprint','Five cots arranged around a 1.3 m transverse circulation strip and 1.6 m front entry. Existing shaded premises should be considered before building this structure.','Ground bearing, drainage, accessible approach and foundations are unengineered. No accessibility compliance claim.')
posts=[]
for x,y in [(0,0),(1800,0),(4100,0),(5900,0),(0,5300),(3000,5300),(5900,5300),(0,2650),(5900,2650)]:
 posts.append(box(100,100,2800).cut(box(90,90,2802).translate((5,5,-1))).translate((x,y,0)))
add('frame',compound(posts+[box(6000,100,160).translate((0,y,2800)) for y in [0,5300]]+[box(100,5400,160).translate((x,0,2800)) for x in [0,2950,5900]]),'structure','#49786d','Perimeter frame / span proposal','An open pavilion keeps cross-ventilation paths and access visible. Perimeter posts keep the central front access route open.','Member dimensions only establish conceptual geometry; loading, bracing, joints, anchors and roof uplift require structural engineering.')
# Overhang 600 mm; central roof slots under raised weather cap.
lower=box(7200,6600,60).translate((-600,-600,3000)).cut(box(600,5400,100).translate((2700,0,2980)))
upper=box(7200,6600,20).translate((-600,-600,3320)).cut(box(600,5400,100).translate((2700,0,3300)))
add('lower_roof',lower,'roof','#d5ddc1','Shaded lower roof / insulation allowance','A separate lower surface shields occupants from direct sun; 260 mm clear roof cavity is reserved between skins. Insulation selection is open.','No measured underside or radiant-temperature reduction. Condensation, fire, dust and service access need detailing.')
add('reflective_roof',upper,'roof','#efe6cf','Reflective overhanging upper roof','Deep chajja/verandah-like shade is adapted as a 600 mm overhang. A reflective exterior reduces solar absorption; performance depends on material, soiling and sun angle.','Flat concept envelope only: slope, drainage, fastening and reflectance specifications are not detailed.')
add('ridge_cap',box(1200,6000,40).translate((2400,-300,3660)),'roof','#a8875c','Raised shaded ridge / exhaust proposal','A raised cap over the central roof slot provides a high-level path for warm air. It borrows the principle of high openings, not a promise of windcatcher performance.','Rain baffles, insect mesh, reverse flow and wind-pressure analysis remain open. This cannot generate ventilation without a driving pressure difference.')
# Perforated screens remain open at top and along front; slats = replaceable low-mass jaali concept.
for side,x in [('west',0),('east',5940)]:
 slats=[box(60,45,1600).translate((x,100+i*120,850)) for i in range(43)]
 add(side+'_screen',compound(slats),'screen','#b88757',side.title()+' removable jaali screen','Shades low-angle sun while retaining gaps for ventilation; modules can be removed or adjusted for actual sun and wind exposure.','Nominal slat geometry is not a validated porosity or pressure-loss design. More screening may reduce useful airflow.')
add('rear_screen',compound([box(45,60,1600).translate((100+i*120,5340,850)) for i in range(48)]),'screen','#b88757','Rear permeable screen','Reduces direct exposure at cot head ends while keeping an open pavilion. Orientation must follow the surveyed site.','Sun paths and prevailing winds for the actual plot have not been surveyed.')
# Cots run north-south; head ends +Y. Clear central strip y=2100..3400.
places=[(400,200),(4400,200),(400,3400),(2400,3400),(4400,3400)]
for i,(x,y) in enumerate(places,1):
 # 750 x 1900 platform, 450 mm high; inclined 650 mm head section.
 base=box(750,1250,35).translate((x,y,450))
 back=box(750,650,35).rotate((0,0,0),(1,0,0),20).translate((x,y+1250,450))
 legs=[box(40,40,450).translate((x+xx,y+yy,0)) for xx in [10,700] for yy in [50,1150,1780]]
 add(f'cot_{i}',compound([base,back]+legs),'cot','#458f89',f'Reclining cot {i} / rest position','750 × 1900 mm nominal cot, 450 mm deck height, illustrative 20° backrest. Replaceable breathable surface rather than thick heat-retaining upholstery; worker chooses a comfortable posture.','Not a medical bed or a treatment posture. Capacity, stability, cleanability, transfers and backrest lock require supplier selection and testing. Do not leave an ill worker to sleep unattended.')
 # One independently controlled 400 mm axial fan reference at each head, tilted downward 35 degrees.
 fx=x+375;fy=y+1700;fz=1350
 fan=box(460,65,460).translate((-230,-32.5,-230)).cut(cyl(205,80,(0,-40,0),(0,1,0)))
 blades=[cyl(42,40,(0,-20,0),(0,1,0))]
 for k in range(7):blades.append(box(65,10,155).translate((12,-5,40)).rotate((0,0,0),(0,1,0),k*360/7))
 guards=[cq.Solid.makeTorus(r,3,cq.Vector(0,-40,0),cq.Vector(0,1,0)) for r in [65,110,155,202]]
 fan=compound([fan]+blades+guards).rotate((0,0,0),(1,0,0),35).translate((fx,fy,fz))
 support=box(45,45,1350).translate((fx-22,fy+80,0))
 add(f'fan_{i}',compound([fan,support]),'fan','#d59b34',f'Individual fan {i} / adjustable concept','One nominal 400 mm fan per cot targets an occupied resting zone. Local manual speed/off control avoids forcing everyone to accept the same airflow.','Illustrative fan, guard and stand; no supplier, fan curve, motor voltage, power or outdoor rating selected. A larger diameter or five fans does not establish adequate cooling.')
 add(f'air_sensor_{i}',compound([box(55,55,80).translate((x+820,y+1500,950)),box(18,22,4).translate((x+838,y+1518,1030))]),'sensor','#1faabb',f'Air temperature / RH sensor {i}','Placed beside the cot at torso/head-zone height, away from controller heat. Per-zone readings reveal uneven conditions.','Radiation shield and location bias need validation. This measures air, not body temperature or BP. Distributed wiring/interface is a new design, not existing bench I²C over long cables.')
 add(f'control_{i}',box(70,80,30).translate((x+760,y+1250,600)),'control','#cf5f48',f'Local fan / assistance control {i}','Reachable local speed/off and assistance button; autonomous local controls should remain usable without cloud connectivity.','Reach and posture need user trials. The five-zone controller and wiring are proposed; current firmware supports the earlier bench only.')
add('service_cabinet',box(500,250,800).translate((3300,5000,0)),'control','#38656b','Dry service cabinet / five-zone proposal','Central protected distribution, controller and display; separate per-fan branch protection and feedback are required.','Not a wiring design. Electrical ratings, protection, earthing, enclosure IP, isolation and qualified installation are open.')
add('reference_station',box(100,100,150).translate((-900,2500,1100)),'sensor','#1faabb','External reference air station','An independent shaded, ventilated reference outside the pavilion enables paired environmental comparison.','Final radiation shielding and matching exposure require a test protocol; not an unshielded sun-heated sensor.')
add('wbgt_station',compound([cyl(12,900,(5700,4900,0)),cq.Solid.makeSphere(75,cq.Vector(5700,4900,975))]),'validation','#535068','External calibrated WBGT / validation reservation','Reserve space for a calibrated occupational heat instrument and separate air-speed mapping. Environmental evaluation also needs workload, clothing and acclimatization context.','Illustrative instrument location only. A black sphere alone is not a complete WBGT instrument; no physiological verdict is produced.')
A.save(str(O/'SAAYA_FS02_concept.step'))
data=dict(revision='FS-02 CONCEPT',units='mm',status='NOT FOR FABRICATION / NO COOLING PERFORMANCE CLAIM',footprint_mm=[6000,5400],roof_mm=[7200,6600],cot_count=5,fan_count=5,central_clear_strip_mm=1300,front_entry_clear_mm=1600,parts=rows)
(O/'assembly.json').write_text(json.dumps(data,indent=2))
# Validation is geometry-only; no assembly collision or structural approval is implied.
(O/'validation.json').write_text(json.dumps(dict(part_count=len(rows),all_generated_shapes_valid=True,step_bytes=(O/'SAAYA_FS02_concept.step').stat().st_size,not_tested=['assembly interference','strength','human reach','airflow','thermal performance','electrical protection']),indent=2))
S=R.parents[1]/'site'/'pavilion';S.mkdir(exist_ok=True)
for f in O.iterdir():shutil.copy2(f,S/f.name)
print('Generated',len(rows),'concept components; STEP, STL, manifest and geometry status.')
