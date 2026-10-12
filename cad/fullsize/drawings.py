from pathlib import Path
O=Path(__file__).resolve().parent/'exports'
def start(title):return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1000" viewBox="0 0 1400 1000"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M8,0 L0,4 L8,8" fill="none" stroke="#234c40"/></marker></defs><rect width="1400" height="1000" fill="#faf8ef"/><g font-family="Arial" fill="#234c40"><text x="40" y="50" font-size="28">{title}</text><text x="40" y="80" font-size="16">FS-01 / REV A / ALL DIMENSIONS mm / REVIEW ONLY — NOT FOR CONSTRUCTION</text>']
def rect(s,x,y,w,h,fill='none'):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#234c40" stroke-width="1.5"/>')
def line(s,x,y,xx,yy):s.append(f'<path d="M{x},{y} L{xx},{yy}" stroke="#234c40" fill="none"/>')
def text(s,x,y,t,size=16):s.append(f'<text x="{x}" y="{y}" font-size="{size}">{t}</text>')
def circle(s,x,y,r):s.append(f'<circle cx="{x}" cy="{y}" r="{r}" stroke="#234c40" fill="none"/>')
def dim(s,x,y,xx,yy,label):s.append(f'<path d="M{x},{y} L{xx},{yy}" stroke="#234c40" marker-start="url(#a)" marker-end="url(#a)"/>');text(s,(x+xx)/2+5,(y+yy)/2-10,label,14)
def end(s,file):s.append('</g></svg>');(O/file).write_text(''.join(s))
s=start('GENERAL ARRANGEMENT / POST GRID + OCCUPIED SPACE')
text(s,60,125,'PLAN / nominal projected dimensions');rect(s,60,160,560,480);rect(s,100,200,480,400)
for x in [100,580]:
 for y in [200,600]:rect(s,x-6,y-6,12,12,'#8fa597')
rect(s,140,500,280,90,'#dcc5a2');text(s,160,545,'1400 × 450 bench');rect(s,470,380,80,150);text(s,455,365,'Access bay');dim(s,100,680,580,680,'2400 POST CENTRES');dim(s,650,200,650,600,'2000');dim(s,60,150,620,150,'2800 ROOF');text(s,75,720,'Front approach remains open; no compliance certification assumed.')
text(s,760,125,'FRONT / frame and double roof');
for x in [780,1260]:rect(s,x-6,254,12,460,'#8fa597');rect(s,x-20,714,40,2)
rect(s,762,238,516,16);rect(s,740,210,560,2);rect(s,740,186,560,2);rect(s,820,626,280,5,'#dcc5a2');dim(s,1340,254,1340,716,'2310 CLEAR');dim(s,780,753,1260,753,'2400');text(s,775,790,'Roof fall: 120 over 2000 (3.434°), toward front.');text(s,775,815,'Roof gap approximately 120; connection details HOLD.')
text(s,60,855,'Datum: floor level Z0; front-left post centre X0,Y0. Rear post centre Y2000. Roof overhang nominally 200 each side.');text(s,60,885,'SHS posts 60 × 60 × 3; crossbeams RHS 80 × 60 × 3; purlins RHS 60 × 40 × 3. Candidate sections require structural approval.');text(s,60,915,'No foundation sizes, anchor capacities, roof forming/seal detail or certified safe occupancy are established by this drawing.');end(s,'general-arrangement.svg')
s=start('INTERFACE PLATES / HOLE COORDINATES')
for x,y,w,h,t,holes,title in [(80,180,200,200,10,[(a,b,18) for a in [30,170] for b in [30,170]],'BP01 / BASE PLATE'),(700,180,120,100,6,[(a,b,11) for a in [25,95] for b in [35,65]],'CP01 / ROOF CONNECTION')]:
 k=2;text(s,x,y-35,title);rect(s,x,y,w*k,h*k)
 for a,b,d in holes:circle(s,x+a*k,y+b*k,d*k/2)
 dim(s,x,y+h*k+35,x+w*k,y+h*k+35,str(w));dim(s,x+w*k+35,y,x+w*k+35,y+h*k,str(h));text(s,x,y+h*k+80,f'Thickness {t}; holes Ø{holes[0][2]}. Datum: lower-left in part CAD.');text(s,x,y+h*k+108,'Hole coordinates: '+str([(a,b) for a,b,d in holes]),13)
text(s,80,800,'Base anchor pattern 140 × 140. Anchors and concrete/soil design are unresolved. Do not select anchors from hole diameter alone.');text(s,80,835,'Proposed plate hole-position target ±0.25 mm; size +0.2/0 mm. Fabricator and structural engineer to confirm joint fits/edge distances.');text(s,80,870,'DXFs contain flat profiles only. CP02 cap and carrier/lid profiles are included as separate DXFs. No formed roof flat-pattern approval.');end(s,'plate-interfaces.svg')
s=start('DRY SERVICE ENCLOSURE / PORT DATUMS')
rect(s,80,160,600,480);rect(s,130,450,76,50)
for x in [210,245,280]:circle(s,80+x*2,640-60*2,7)
text(s,80,130,'FRONT / 300 W × 240 H; depth 120; nominal wall 3');dim(s,80,675,680,675,'300');text(s,80,720,'OLED opening: X25–63, Z70–95. Three Ø7 buttons: X210 / 245 / 280 at Z60.');text(s,80,755,'Bottom cable ports: Ø20 at (X,Y) = (55,60), (130,60), (205,60).');text(s,80,790,'Carrier 260 × 80 × 3; lid 300 × 120 × 3. Lid holes Ø4.5 at (12,12), (288,12), (12,108), (288,108).');
rect(s,810,180,360,144);text(s,810,150,'TOP / 300 × 120');text(s,790,405,'RELEASE HOLDS',20);text(s,790,440,'Gasket, hinge, latch and mounting supports');text(s,790,470,'Actual board/display dimensions and standoffs');text(s,790,500,'Cable glands, bend radius and strain relief');text(s,790,530,'IP/weather and electrical inspection');text(s,80,870,'A purchased, certified outdoor enclosure is preferred. This custom shell is a packaging proposal, not a rated enclosure.');end(s,'enclosure-interfaces.svg')
print('3 dimensioned SVG review sheets generated')
