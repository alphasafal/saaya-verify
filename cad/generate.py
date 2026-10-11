"""Parametric fabrication candidates; millimetres. CSG exported with Manifold.
Run from project root: python cad/generate.py. Physical fit is NOT established by mesh tests.
"""
from pathlib import Path
import json,math
import numpy as np
import trimesh as tm
R=Path(__file__).resolve().parent;P=json.loads((R/'parameters.json').read_text());O=R/'exports';O.mkdir(exist_ok=True)
def box(size,at=(0,0,0)):
    m=tm.creation.box(extents=size);m.apply_translation(np.array(at)+np.array(size)/2);return m

def cyl(r,h,at=(0,0,0),axis='z'):
    m=tm.creation.cylinder(radius=r,height=h,sections=48)
    if axis=='y':m.apply_transform(tm.transformations.rotation_matrix(math.pi/2,[1,0,0]));m.apply_translation([at[0],at[1]+h/2,at[2]])
    elif axis=='x':m.apply_transform(tm.transformations.rotation_matrix(math.pi/2,[0,1,0]));m.apply_translation([at[0]+h/2,at[1],at[2]])
    else:m.apply_translation([at[0],at[1],at[2]+h/2])
    return m

def union(*items):return tm.boolean.union(list(items),engine='manifold')
def sub(a,*items):return tm.boolean.difference([a,*items],engine='manifold')
report=[]
def save(name,m):
    assert m.is_watertight and m.volume>0,name
    m.export(O/(name+'.stl'));report.append({'part':name,'dimensions_mm':m.extents.round(3).tolist(),'volume_cm3':round(m.volume/1000,3),'watertight':bool(m.is_watertight),'physical_fit':'UNVERIFIED'})
# 120 x 90 x 45 enclosure, lid included; screw bosses run inside corners.
L,W,H=P['enclosure'];w=P['wall'];t=P['lid_thickness'];bosses=[(7,7),(L-7,7),(7,W-7),(L-7,W-7)]
shell=sub(box([L,W,H-t]),box([L-2*w,W-2*w,H],[w,w,w]))
for x,y in bosses:shell=union(shell,cyl(5.5,H-t-w,[x,y,w]))
for x,y in bosses:shell=sub(shell,cyl(1.35,H,[x,y,0]))
# Front removable display insert, three 7mm nominal pushbuttons, indicator and cable glands.
shell=sub(shell,box([36,6,22],[12,-1,14]),*[cyl(3.5,6,[x,-1,24],'y') for x in [64,82,100]],cyl(1.6,6,[112,-1,34],'y'),cyl(4,6,[22,W-4,18],'y'),cyl(4,6,[95,W-4,18],'y'))
# Floor holes for replaceable slotted carrier; nuts remain accessible before installation.
for x,y in [(18,30),(102,30),(18,67),(102,67)]:shell=sub(shell,cyl(1.65,6,[x,y,-1]))
save('enclosure_base',shell)
lid=sub(box([L,W,t]),*[cyl(1.65,t+2,[x,y,-1]) for x,y in bosses]);save('enclosure_lid',lid)
# Universal carrier takes insulated zip ties; board-specific holes are intentionally not guessed.
tray=box([100,57,2])
for x in [12,88]:
    for y in [6,43]:tray=sub(tray,box([8,3,4],[x-4,y,-1]))
for x,y in [(8,10),(92,10),(8,47),(92,47)]:tray=sub(tray,cyl(1.65,4,[x,y,-1]))
save('universal_board_carrier',tray)
bezel=sub(box([44,30,3]),box([P['oled_window'][0],P['oled_window'][1],5],[10,8,-1]))
for x,y in [(4,4),(40,4),(4,26),(40,26)]:bezel=sub(bezel,cyl(1.3,5,[x,y,-1]))
save('oled_bezel_measure_module_first',bezel)
# Fan plate: 32mm square centres, grille strip gaps ~3mm, spacers separate.
guard=box([48,48,3])
for x in range(8,40,6):guard=sub(guard,box([3,32,5],[x,8,-1]))
for x in [8,40]:
    for y in [8,40]:guard=sub(guard,cyl(1.65,5,[x,y,-1]))
save('fan_guard_40mm',guard)
spacer=sub(cyl(3.8,4),cyl(1.65,6,[0,0,-1]));save('fan_guard_spacer',spacer)
# 48mm angle mount with same fan bolt grid on vertical face and base slots.
bracket=union(box([48,22,3]),box([48,3,48]))
for x in [8,40]:
    for z in [8,40]:bracket=sub(bracket,cyl(1.65,5,[x,-1,z],'y'))
for x in [8,40]:bracket=sub(bracket,box([3.4,10,5],[x-1.7,8,-1]))
save('fan_angle_bracket',bracket)
# Sensor hood / shield cage: open underside with slots; not a calibrated aspirated shield.
hood=sub(box([30,34,24]),box([25,29,23],[2.5,2.5,-1]))
for z in [5,11,17]:
    hood=sub(hood,box([32,22,3],[-1,6,z]),box([18,36,3],[6,-1,z]))
# slots intersect sidewalls; roof and corner ribs remain joined.
save('sensor_shield_cage',hood)
# Four identical base tiles are joined with plates; 220mm-bed-compatible pieces.
base=box([150,120,4])
for x in [10,140]:
    for y in [10,110]:base=sub(base,cyl(1.65,6,[x,y,-1]))
save('base_quarter_print_4',base)
roof=box([160,130,3])
for x in [20,140]:
    for y in [20,110]:roof=sub(roof,cyl(1.65,5,[x,y,-1]))
save('roof_quarter_print_8',roof)
pillar=box([12,12,P['pillar_height']]);pillar=sub(pillar,cyl(1.35,16,[6,6,-1]),cyl(1.35,17,[6,6,P['pillar_height']-16]));save('pillar_print_4',pillar)
roof_spacer=sub(cyl(5,P['roof_gap']),cyl(1.65,P['roof_gap']+2,[0,0,-1]));save('roof_spacer_print_4',roof_spacer)
join=box([44,24,3]);join=sub(join,*[cyl(1.65,5,[x,y,-1]) for x in [12,32] for y in [6,18]]);save('join_plate_drill_to_fit',join)
# Jaali test coupon: 96 x 64, open square geometry rather than a claimed optimal pattern.
for pitch in [8,12]:
    screen=box([96,64,2.4])
    for x in range(6,90-pitch,pitch):
        for y in range(6,58-pitch,pitch):screen=sub(screen,box([pitch-3,pitch-3,5],[x,y,-1]))
    save(f'jaali_coupon_pitch_{pitch}',screen)
(O/'mesh-report.json').write_text(json.dumps(report,indent=2));print('Exported',len(report),'closed positive-volume meshes')
# Dimensioned SVG: orthographic drawing with envelope / hole centres, not a tolerance-certified production drawing.
def svg_header(title):return f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="780" viewBox="0 0 1100 780"><rect width="1100" height="780" fill="#f7f5ec"/><g font-family="Arial" fill="#193b32"><text x="40" y="50" font-size="26">{title}</text><text x="40" y="77" font-size="13">V2 / MILLIMETRES / FABRICATION CANDIDATE / PHYSICAL FIT UNVERIFIED</text>'
s=svg_header('SAAYA — DRY ENCLOSURE / DATUM FRONT-LEFT-BOTTOM')
s+='<g transform="translate(70 125) scale(3)"><rect width="120" height="90" fill="none" stroke="#275c49" stroke-width=".5"/><rect x="2.5" y="2.5" width="115" height="85" fill="none" stroke="#9fb4a3" stroke-width=".4"/>'
for x,y in bosses:s+=f'<circle cx="{x}" cy="{y}" r="5.5" fill="none" stroke="#275c49" stroke-width=".4"/><circle cx="{x}" cy="{y}" r="1.35" fill="none" stroke="#275c49" stroke-width=".4"/>'
s+='<rect x="18" y="30" width="54.4" height="27.9" fill="#c5d9c2"/><text x="20" y="43" font-size="3.8">ESP32 REFERENCE ENVELOPE</text><rect x="85" y="30" width="25" height="25" fill="#e2d3af"/><text x="86" y="43" font-size="3.8">I/O / DRIVER</text><rect x="18" y="62" width="22" height="18" fill="#b7c9c2"/><text x="20" y="71" font-size="3.8">INA219</text></g>'
s+='<text x="200" y="425" font-size="17">120 OUTSIDE / 115 INSIDE</text><text x="50" y="460" font-size="14">DEPTH 90 / WALL 2.5 / SHELL HEIGHT 42.5 + LID 2.5</text>'
s+='<g transform="translate(560 150) scale(3)"><rect width="120" height="45" fill="none" stroke="#275c49" stroke-width=".5"/><rect x="12" y="9" width="36" height="22" fill="none" stroke="#275c49" stroke-width=".5"/>'
for x in [64,82,100]:s+=f'<circle cx="{x}" cy="21" r="3.5" fill="none" stroke="#275c49" stroke-width=".5"/>'
s+='</g><text x="560" y="320" font-size="15">FRONT: 36 x 22 BEZEL OPENING; 3 x Ø7 BUTTONS</text><text x="560" y="350" font-size="14">BUTTON X: 64 / 82 / 100; Z: 24 FROM BASE</text><text x="560" y="380" font-size="14">LID: Ø3.3 AT (7,7), (113,7), (7,83), (113,83)</text><text x="560" y="410" font-size="14">REAR: Ø8 CABLE ENTRIES AT X22 / X95, Z18</text>'
notes=['ASSEMBLY: M3 FASTENERS; CHECK THREAD/PILOT FIT WITH A SMALL COUPON FIRST.','NOMINAL 0.3 CLEARANCE IS A STARTING VALUE, NOT A VERIFIED PRINT TOLERANCE.','USE INSULATED CARRIER / STANDOFFS. KEEP ANTENNA CLEAR OF METAL AND POWER WIRES.','OLED BEZEL IS REPLACEABLE; MEASURE YOUR MODULE BEFORE PRINTING.','FOUR BASE TILES: 150 x 120 x 4; ROOF TILES: 160 x 130 x 3; PILLARS: 12 x 12 x 190.','ROOF GAP: 16. SOLAR AND EVAPORATIVE MODULES EXCLUDED FROM THE CORE ASSEMBLY.','RAIN / UV / STRUCTURAL / ELECTRICAL CERTIFICATION NOT ESTABLISHED.']
for i,n in enumerate(notes):s+=f'<text x="45" y="{530+i*28}" font-size="14">{n}</text>'
s+='</g></svg>'; (O/'enclosure-drawing.svg').write_text(s)
