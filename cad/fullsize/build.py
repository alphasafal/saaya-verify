"""SAAYA FS-01 revision A: review/quotation solids, mm. NOT issued for construction."""
from pathlib import Path
import cadquery as cq
import json,csv,math,collections
R=Path(__file__).resolve().parent;O=R/'exports';O.mkdir(exist_ok=True)
parts={};instances=[];assembly=cq.Assembly(name='SAAYA_FS01_REVIEW_ONLY');slope=.06
colors={'frame':'#486d60','roof':'#e6e8d9','shade':'#bba478','seat':'#ac805a','electronics':'#38656b','hardware':'#8b9291','wet':'#78aeb0','foundation':'#aaa999'}
def box(x,y,z):return cq.Workplane('XY').box(x,y,z,centered=False).val()
def cyl(r,h,at=(0,0,0),axis=(0,0,1)):return cq.Solid.makeCylinder(r,h,cq.Vector(*at),cq.Vector(*axis))
def cut(s,*tools):
 for t in tools:s=s.cut(t)
 return s

def tube_z(w,d,t,h):return cut(box(w,d,h),box(w-2*t,d-2*t,h+2).translate((t,t,-1)))
def tube_x(l,w,h,t):return cut(box(l,w,h),box(l+2,w-2*t,h-2*t).translate((-1,t,t)))
def slope_tube(length,w,h,t):
 # Vertical end cuts and true sloping longitudinal faces; ends meet horizontal support elevations.
 outer=cq.Workplane('YZ').polyline([(0,0),(length,slope*length),(length,slope*length+h),(0,h)]).close().extrude(w).val()
 inner=cq.Workplane('YZ').polyline([(-1,slope*-1+t),(length+1,slope*(length+1)+t),(length+1,slope*(length+1)+h-t),(-1,h-t-slope)]).close().extrude(w-2*t).val().translate((t,0,0))
 return outer.cut(inner)
def slope_slab(w,d,t):
 return cq.Workplane('YZ').polyline([(0,0),(d,slope*d),(d,slope*d+t),(0,t)]).close().extrude(w).val()

def roof_skin(t,holes):
 s=slope_slab(2800,2400,t)
 for x,y,diam in holes:s=s.cut(cyl(diam/2,160,(x,y,-1)))
 return s

def plate(w,d,t,holes):
 s=box(w,d,t)
 for x,y,diam in holes:s=s.cut(cyl(diam/2,t+2,(x,y,-1)))
 return s

def define(name,shape,material,process,note='',flat=False,density=7850):
 assert shape.isValid() and shape.Volume()>0,name
 parts[name]=dict(shape=shape,material=material,process=process,note=note,density=density,flat=flat)
 cq.exporters.export(shape,str(O/(name+'.step')));cq.exporters.export(shape,str(O/(name+'.stl')),tolerance=.3,angularTolerance=.2)
 if flat:cq.exporters.export(cq.Workplane(obj=shape).faces('>Z').wires().toPending(),str(O/(name+'.dxf')))
 return name

def put(part,name,pos,group='frame',rot=0):
 shape=parts[part]['shape'];loc=cq.Location(cq.Vector(*pos),cq.Vector(0,0,1),rot)
 assembly.add(shape,name=name,loc=loc,color=cq.Color(*[int(colors[group][i:i+2],16)/255 for i in (1,3,5)]))
 instances.append(dict(part=part,name=name,position=pos,rotation_z=rot,group=group,color=colors[group]))

steel='S235/S275 equivalent candidate; obtain mill certificate'
define('BP01_base_plate',plate(200,200,10,[(x,y,18) for x in [30,170] for y in [30,170]]),steel,'Laser cut + drill','Four anchor holes; foundation and anchor design HOLD',True)
define('P01_front_post',tube_z(60,60,3,2300),steel,'Saw SHS 60x60x3; weld base','Bottom at z10; cap/vent/drain detail by galvanizer')
define('P02_rear_post',tube_z(60,60,3,2420),steel,'Saw SHS 60x60x3; weld base')
define('B01_crossbeam',cut(tube_x(2580,60,80,3),*[cyl(5.5,82,(90+x+dx,30+dy,-1)) for x in [0,1200,2400] for dx in [-35,35] for dy in [-15,15]]),steel,'Saw RHS 80x60x3','Connection plate/weld schedule requires structural review')
define('R01_roof_purlin',cut(slope_tube(2000,40,60,3),box(42,52,130).translate((-1,1950,-10))),steel,'RHS 60x40x3; vertical end cuts','Slope 3.434 degrees; span 2000; rear bottom seating relief up to 3 mm over 50 mm requires structural review')
define('CP01_roof_connection',plate(120,100,6,[(x,y,11) for x in [25,95] for y in [35,65]]),steel,'Laser cut + drill','M10 proposed; hole pattern matched to bolt envelopes',True)
define('SP01_roof_spacer',slope_tube(30,30,116,2),steel,'Saw SHS 30x30x2','Ventilation gap; bolted cap plates not load approved')
define('CP02_spacer_cap',cut(slope_slab(80,80,3),*[cyl(3.3,10,(x,y,-1)) for x,y in [(12,12),(12,68),(68,12),(68,68),(40,40)]]),steel,'Laser cut + drill','M6 proposed, isolate dissimilar metals',True)
# Roof panels exported as true solids with coordinated holes. Flat sheet sizing is projected before slope.
roofholes=[(x,y,6.6) for x in [200,1400,2600] for y in [200,1200,2200]]
define('RF01_lower_skin',roof_skin(1,roofholes),'Aluminium sheet candidate','Cut/drill; split into transportable panels at fabrication','One solid envelope; seam/hem tooling detail HOLD',True,density=2700)
define('RF02_upper_skin',roof_skin(.8,roofholes),'Coated steel sheet candidate','Cut/drill/form; reflective finish','Flat envelope; formed profile, laps, rain seal and uplift fixing HOLD',True)
# Knee braces are spatially separate gusset plates, cut from flat stock.
tri=cq.Workplane('XZ').polyline([(0,0),(450,450),(0,450)]).close().extrude(6).val()
tri=tri.cut(cyl(30,8,(90,1,340),(0,-1,0)))
define('G01_knee_gusset',tri,steel,'Laser cut 6 mm; weld to frame','Weld access and buckling check HOLD')
define('ST01_bench_leg',tube_z(40,40,2,345),steel,'Saw SHS 40x40x2')
define('ST02_bench_rail',tube_x(1400,40,40,2),steel,'Saw SHS 40x40x2')
define('ST04_bench_crossrail',tube_x(450,40,40,2),steel,'Saw SHS 40x40x2','Transverse support beneath every slat; connection strength review required')
define('ST03_seat_slat',box(1400,70,25),'Durable timber / recycled plastic candidate','Cut, radius edges, predrill','Material/creep/fire specification and surface temperature test HOLD',density=650)
# Rear shade is a replaceable louvre cassette, no assumed aerodynamic optimization.
define('JA01_louvre',box(20,40,1070),'Timber candidate','Cut and finish','Interchangeable spacing; check wind load and splinters',density=650)
define('JA02_screen_rail',tube_x(1400,30,30,2),steel,'Saw RHS 30x30x2')
# Service enclosure and removable lid; all ports are actual cutouts, electronics remain reference envelopes.
enc=cut(box(300,120,240),box(294,114,238).translate((3,3,3)))
for x in [55,130,205]:enc=enc.cut(cyl(10,8,(x,60,-1)))
for x in [210,245,280]:enc=enc.cut(cyl(3.5,8,(x,-1,60),(0,1,0)))
enc=enc.cut(box(38,8,25).translate((25,-1,70))).cut(cyl(1.7,8,(280,-1,95),(0,1,0)))
define('E01_dry_enclosure',enc,'Aluminium candidate','Fold/weld or purchased enclosure adapted','Envelope only for enclosure process; seals, hinges, wall mounts and IP test HOLD',density=2700)
define('E02_service_lid',plate(300,120,3,[(x,y,4.5) for x in [12,288] for y in [12,108]]),'Aluminium candidate','Cut/drill','Gasket and threaded supports require supplier selection',True,density=2700)
define('E03_component_carrier',plate(260,80,3,[(x,y,4.5) for x in [10,250] for y in [10,70]]),'Aluminium candidate','Cut/drill','Insulated standoffs; board mounting holes transferred after component approval',True,density=2700)
define('F01_fan_cartridge',cut(box(240,4,240),cyl(95,6,(120,-1,120),(0,1,0)),*[cyl(2.7,6,(x,-1,z),(0,1,0)) for x in [43,197] for z in [43,197]]),'Aluminium candidate','Cut + drill','154 mm fan bolt grid; confirm actual fan drawing/revision',density=2700)
guard=box(240,3,240)
for x in range(20,218,9):guard=guard.cut(box(4,5,190).translate((x,-1,25)))
guard=cut(guard,*[cyl(2.7,5,(x,-1,z),(0,1,0)) for x in [43,197] for z in [43,197]])
define('F02_fan_guard',guard,'Aluminium candidate','Laser cut; deburr','4 mm slots; finger/probe clearance, rigidity and airflow tests required',density=2700)
define('F03_reference_fan',cut(box(200,30,200),cyl(90,32,(100,-1,100),(0,1,0))), 'Purchased Noctua NF-A20 PWM reference','Purchase','Not weather qualified; use an outdoor-rated substitute before release',density=500)
define('S01_sensor_shield',cut(box(50,50,70),box(44,44,69).translate((3,3,-1))), 'UV-resistant polymer candidate','Print fit prototype; source qualified shield','Illustrative shield enclosure; ventilation/radiation performance unverified',density=1200)
define('E04_ESP32_reference',box(48.26,27.94,14),'Purchased electronics','Purchase','Espressif DevKitC V4 PCB outline; connector/component heights require measurement',density=900)
define('E05_monitor_reference',box(25,20,12),'Purchased electronics','Purchase','INA219 nominal; exact supplier board HOLD',density=900)
define('E06_display_reference',box(36,6,24),'Purchased electronics','Purchase','OLED nominal; final module/drawing HOLD',density=900)
define('S02_roof_probe',cyl(3,50),'Stainless probe reference','Purchase','Probe dimensional allowance, supplier confirmation required',density=8000)
define('W01_optional_water_vessel',cut(box(180,180,230),box(172,172,228).translate((4,4,4))),'Polymer vessel candidate','Purchase','Empty removable experiment vessel; no potable-water or cooling claim',density=950)
define('HW01_M10_bolt_reference',cyl(5,100).fuse(cyl(8,6,(0,0,100))),'Steel hardware','Purchase','Unthreaded solid envelope; grade/length/washer/torque approval HOLD')
define('HW02_M16_anchor_reference',cyl(8,200,(0,0,-180)).fuse(cyl(13,10,(0,0,20))),'Anchor hardware','Purchase','Geometry ONLY; embedment and capacity not designed')
define('C01_cable_trunk',cut(box(25,18,1700),box(21,16,1702).translate((2,2,-1))),'UV-resistant conduit candidate','Cut and mechanically fasten','No mains wiring in model; secure clamps and drip loops required',density=1200)
define('MT01_rear_service_rail',tube_x(2340,20,20,2),steel,'Saw RHS 20x20x2','Rear support rail; weld/attachment verification required')
define('MT02_fan_support_arm',tube_x(90,20,20,2),steel,'Saw RHS 20x20x2','Rotate along Y; weld to rail')
define('MT03_enclosure_backrail',tube_x(400,20,20,2),steel,'Saw RHS 20x20x2','Bracket attachment and back-wall sealing HOLD')
define('MT04_enclosure_return',tube_x(110,20,20,2),steel,'Saw RHS 20x20x2')
define('MT05_seated_sensor_stem',tube_z(20,20,2,650),steel,'Saw SHS 20x20x2','Bench mount fastener detail HOLD')
define('MT06_reference_sensor_stem',tube_z(20,20,2,1096),steel,'Saw SHS 20x20x2','Independent reference support; anti-tip/anchor verification HOLD')
define('MT07_sensor_foot',plate(80,80,4,[(x,y,6.6) for x in [12,68] for y in [12,68]]),steel,'Laser cut/drill',flat=True)
define('E07_button_reference',cyl(3,10,(0,0,0),(0,1,0)),'Purchased switch','Purchase','Envelope only; choose exact panel switch',density=1200)
define('E08_LED_reference',cyl(1.5,5,(0,0,0),(0,1,0)),'Purchased indicator','Purchase','Envelope only',density=1200)
define('E09_buzzer_reference',box(12,12,8),'Purchased buzzer','Purchase','Envelope only; audible level unverified',density=1200)
define('S03_SHT31_reference',box(12.7,18,2.6),'Purchased sensor','Purchase','Adafruit 2857 current outline reference; confirm purchased revision',density=1000)
define('W02_float_reference',box(8,20,12),'Purchased level switch','Purchase','Nominal envelope; material compatibility and wiring unverified',density=1000)
for i,(x,y) in enumerate([(0,0),(2400,0),(0,2000),(2400,2000)]):
 put('BP01_base_plate',f'base_{i}',(x-100,y-100,0),'hardware');put('P01_front_post' if y==0 else 'P02_rear_post',f'post_{i}',(x-30,y-30,10))
 for j,(dx,dy) in enumerate([(-70,-70),(-70,70),(70,-70),(70,70)]):put('HW02_M16_anchor_reference',f'anchor_{i}_{j}',(x+dx,y+dy,0),'foundation')
for i,y in enumerate([0,2000]):put('B01_crossbeam',f'crossbeam_{i}',(-90,y-30,2310+slope*y))
for i,x in enumerate([0,1200,2400]):
 put('R01_roof_purlin',f'purlin_{i}',(x-20,0,2396))
 for j,y in enumerate([0,2000]):
  put('CP01_roof_connection',f'connection_{i}_{j}',(x-60,y-50,2390+slope*y),'hardware')
  for k,(dx,dy) in enumerate([(-35,-15),(-35,15),(35,-15),(35,15)]):put('HW01_M10_bolt_reference',f'roof_bolt_{i}_{j}_{k}',(x+dx,y+dy,2296+slope*y),'hardware')
# Roofing tilted to exact projected fall; local Y length shortens by cos(theta) (recorded as unresolved edge projection tolerance).
angle=math.degrees(math.atan(slope))
for part,name,z in [('RF01_lower_skin','lower_roof',2456),('RF02_upper_skin','upper_roof',2576)]:
 shape=parts[part]['shape']
 assembly.add(shape,name=name,loc=cq.Location(cq.Vector(-200,-200,z-12)),color=cq.Color(*[int(colors['roof'][i:i+2],16)/255 for i in (1,3,5)]))
 instances.append(dict(part=part,name=name,position=[-200,-200,z-12],rotation_x=0,group='roof',color=colors['roof']))
for i,x in enumerate([0,1200,2400]):
 for j,y in enumerate([0,1000,2000]):
  put('SP01_roof_spacer',f'roof_spacer_{i}_{j}',(x-15,y-15,2457+slope*(y-15)))
  put('CP02_spacer_cap',f'roof_cap_{i}_{j}',(x-40,y-40,2573+slope*(y-40)),'hardware')
for i,x in enumerate([0,2400]):
 put('G01_knee_gusset',f'front_knee_{i}',(x+(30 if i==0 else -30),0,1860),rot=0 if i==0 else 180)
for i,(x,y) in enumerate([(230,1520),(1530,1520),(230,1840),(1530,1840)]):put('ST01_bench_leg',f'bench_leg_{i}',(x,y,0))
for i,y in enumerate([1520,1840]):put('ST02_bench_rail',f'bench_rail_{i}',(200,y,345))
for i,x in enumerate([270,920,1570]):put('ST04_bench_crossrail',f'bench_crossrail_{i}',(x,1500,385),rot=90)
for i in range(6):put('ST03_seat_slat',f'seat_slat_{i}',(200,1500+i*76,425),'seat')
for i,z in enumerate([900,2000]):put('JA02_screen_rail',f'screen_rail_{i}',(200,1940,z),'shade')
for i in range(18):
 if 800<=220+i*76<=1110:continue # removable fan opening; no louvre/guard clash
 put('JA01_louvre',f'louvre_{i}',(220+i*76,1900,930),'shade')
put('E01_dry_enclosure','dry_enclosure',(1970,1740,950),'electronics');put('E02_service_lid','service_lid',(1970,1740,1190),'electronics');put('E03_component_carrier','component_carrier',(1990,1760,970),'electronics')
put('E04_ESP32_reference','ESP32',(2010,1770,985),'electronics');put('E05_monitor_reference','INA219',(2100,1770,985),'electronics');put('E06_display_reference','OLED',(1996,1735,1020),'electronics')
put('F01_fan_cartridge','fan_mount',(850,1880,1400),'electronics');put('F03_reference_fan','reference_fan',(870,1884,1420),'electronics');put('F02_fan_guard','front_fan_guard',(850,1865,1400),'hardware');put('F02_fan_guard','rear_fan_guard',(850,1920,1400),'hardware')
put('S01_sensor_shield','reference_sensor',(-140,200,1100),'electronics');put('S01_sensor_shield','seated_sensor',(1450,1750,1100),'electronics');put('S02_roof_probe','roof_probe',(1300,1000,2464),'electronics')
put('W01_optional_water_vessel','optional_water',(0,1640,0),'wet');put('C01_cable_trunk','cable_route',(2432,1980,650),'electronics')
put('MT01_rear_service_rail','rear_service_rail',(30,1970,1380))
for i,x in enumerate([870,1090]):put('MT02_fan_support_arm',f'fan_support_arm_{i}',(x,1880,1380),rot=90)
put('MT03_enclosure_backrail','enclosure_backrail',(1970,1860,950));put('MT04_enclosure_return','enclosure_return',(2370,1880,950),rot=90)
put('MT05_seated_sensor_stem','seated_sensor_stem',(1465,1765,450));put('MT06_reference_sensor_stem','reference_sensor_stem',(-125,215,4));put('MT07_sensor_foot','reference_sensor_foot',(-155,185,0),'hardware')
for name,x in [('mode',2180),('assistance',2215),('acknowledge',2250)]:put('E07_button_reference',name+'_button',(x,1735,1010),'electronics')
put('E08_LED_reference','assistance_LED',(2250,1738,1045),'electronics');put('E09_buzzer_reference','assistance_buzzer',(2200,1770,985),'electronics')
put('S03_SHT31_reference','outdoor_SHT31',(-122,217,1130),'electronics');put('S03_SHT31_reference','seated_SHT31',(1468,1767,1130),'electronics');put('W02_float_reference','water_availability_switch',(30,1680,40),'wet')
# Save true boundary-representation assembly and a browser manifest from the same coordinates.
assembly.save(str(O/'SAAYA_FS01_assembly.step'))
counts=collections.Counter(i['part'] for i in instances);bom=[]
for name,p in parts.items():
 b=p['shape'].BoundingBox();mass=p['shape'].Volume()*1e-9*p['density']
 bom.append(dict(part=name,quantity=counts[name],material=p['material'],process=p['process'],envelope_mm=[round(b.xlen,3),round(b.ylen,3),round(b.zlen,3)],unit_mass_kg=round(mass,3),mass_basis='Idealized solid volume × assumed density; purchased electronics masses are placeholders',note=p['note']))
(O/'assembly.json').write_text(json.dumps(dict(revision='FS01-A',status='DESIGN REVIEW / NOT FOR CONSTRUCTION',units='mm',instances=instances),indent=2));(O/'bom.json').write_text(json.dumps(bom,indent=2))
with (O/'bom.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=bom[0].keys());w.writeheader();w.writerows(bom)
report=dict(parts=len(parts),instances=len(instances),all_solids_valid=all(p['shape'].isValid() for p in parts.values()),idealized_mass_kg=round(sum(r['unit_mass_kg']*r['quantity'] for r in bom),2),construction_release=False)
(O/'validation.json').write_text(json.dumps(report,indent=2));print(report)
