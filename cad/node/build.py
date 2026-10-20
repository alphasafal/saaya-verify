"""SAAYA Node v1 -- retrofit IoT controller for an existing rest shade (or FS-01).

All dimensions mm. Datum: enclosure front-left-bottom corner; X right, Y into the wall
(front face y=0, back y=D), Z up. The enclosure is a purchased IP65 ABS box machined to
the hole plan below; the CAD is a fit/placement model, NOT a manufacturing release.
Run: .cadvenv/bin/python cad/node/build.py
"""
from pathlib import Path
import cadquery as cq
import json, shutil

R = Path(__file__).resolve().parent
O = R / 'exports'
O.mkdir(exist_ok=True)

# ---------------- parameters (single source for CAD, drawings and the PDF) ----------------
P = {
    'enclosure': {'W': 175, 'H': 100, 'D': 60, 'wall': 3.0, 'lid_depth': 15,
                  'note': 'Purchased IP65 ABS box ProtechT WPE16 175 x 100 x 60 (Probots, INR 949); lid is the front panel'},
    'oled_window': {'x': 15, 'z': 62, 'w': 25, 'h': 14, 'note': 'Visible area of 0.96 in SSD1306 (21.7 x 10.9 active)'},
    'help_button': {'x': 140, 'z': 62, 'dia': 12, 'note': '12 mm IP65 metal momentary (ProMax), red: HELP (latching request)'},
    'status_led': {'x': 140, 'z': 86, 'dia': 8, 'note': '5 mm red LED in 8 mm panel bezel: help / fan fault / sensor fault'},
    'mode_button': {'x': 140, 'z': 30, 'dia': 12, 'note': '12 mm IP65 metal momentary: fan off / manual'},
    'ack_button': {'y': 38, 'z': 50, 'dia': 12, 'note': 'Right side wall: staff acknowledge, deliberately not on the front'},
    'buzzer_grille': {'x': 27.5, 'z': 32, 'holes': 5, 'dia': 2.0, 'pitch': 5},
    'glands_bottom': {'y': 38, 'xs': [25, 55, 85, 115, 145], 'dia': 12.5,
                      'labels': ['12 V IN', 'FAN', 'SEAT T/RH', 'REF T/RH', 'ROOF + FLOAT'],
                      'note': 'PG7 glands, cable 3-6.5 mm; drip loops below the box'},
    'vent_side': {'y': 38, 'z': 18, 'dia': 12.5, 'note': 'M12 breathable membrane vent, left wall low, against condensation'},
    'bracket': {'W': 215, 'H': 110, 't': 3, 'wall_holes': [(-97, -45), (97, -45), (-97, 45), (97, 45)], 'wall_hole_dia': 6.5,
                'clamp_slots': {'w': 8, 'h': 32, 'xs': [-35, 35], 'zs': [-28, 28]},
                'note': '3 mm aluminium back plate: 4 x M6 wall/anchor holes or 2 stainless hose clamps around a post (up to 90 mm)'},
    'internal_plate': {'w': 160, 'h': 86, 't': 1.5},
    'main_board': {'x': 10, 'z': 8, 'w': 90, 'h': 70, 'standoff': 8, 'note': '90 x 70 perfboard: ESP32 socket, two 2N3904 stages, pull-ups, terminal blocks'},
    'esp32': {'x': 24, 'z': 40, 'w': 54.4, 'h': 27.9, 't': 13, 'note': 'ESP32-DevKitC footprint 54.4 x 27.9'},
    'ina219': {'x': 118, 'z': 54, 'w': 25.5, 'h': 22.3, 't': 4},
    'buck': {'x': 118, 'z': 28, 'w': 22, 'h': 17, 't': 5, 'note': 'MP1584EN 12 V -> 5 V'},
    'fuse': {'x': 118, 'z': 10, 'w': 30, 'h': 10, 't': 10, 'note': '5x20 fuse holder, 1 A slow-blow on 12 V input'},
    'shield': {'plate_dia': 110, 'plates': 5, 'pitch': 14, 't': 2, 'inner_hole': 50, 'rod_r': 45,
               'note': 'Multi-plate radiation shield (white PP/ABS plates on 3 x M5 rods); sensor at centre, open sides'},
    'fan': {'size': 120, 'depth': 25, 'hole_pitch': 105, 'note': 'Arctic P12 Pro 120 mm 12 V 4-wire PWM fan with tach (0 rpm below 5 % PWM), wire guards'},
}
E = P['enclosure']
W, H, D, t = E['W'], E['H'], E['D'], E['wall']

parts = []
asm = cq.Assembly(name='SAAYA_NODE_V1')


def box(x, y, z, at=(0, 0, 0)):
    return cq.Workplane('XY').box(x, y, z, centered=False).val().translate(cq.Vector(*at))


def cyl(r, h, at=(0, 0, 0), axis=(0, 0, 1)):
    return cq.Solid.makeCylinder(r, h, cq.Vector(*at), cq.Vector(*axis))


def add(name, shape, color, group, note=''):
    assert shape.isValid() and shape.Volume() > 0, name
    asm.add(shape, name=name, color=cq.Color(*[int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]))
    cq.exporters.export(shape, str(O / f'{name}.stl'), tolerance=0.2, angularTolerance=0.4)
    bb = shape.BoundingBox()
    parts.append({'name': name, 'group': group, 'color': color, 'note': note,
                  'bounds_mm': [round(v, 2) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)]})


# ---------------- enclosure body (rear part) and lid (front panel) ----------------
ld = E['lid_depth']
body = box(W, D - ld, H, (0, ld, 0)).cut(box(W - 2 * t, D - ld, H - 2 * t, (t, ld, t)))   # open towards the front
g = P['glands_bottom']
for x in g['xs']:
    body = body.cut(cyl(g['dia'] / 2, t + 2, (x, g['y'], -1)))
v = P['vent_side']
body = body.cut(cyl(v['dia'] / 2, t + 2, (-1, v['y'], v['z']), (1, 0, 0)))
a = P['ack_button']
body = body.cut(cyl(a['dia'] / 2, t + 2, (W - t - 1, a['y'], a['z']), (1, 0, 0)))
add('enclosure_body', body, '#d9dcd6', 'enclosure', E['note'])

lid = box(W, ld, H).cut(box(W - 2 * t, ld, H - 2 * t, (t, t, t)))                        # closed front face at y=0..t
o = P['oled_window']
lid = lid.cut(box(o['w'], t + 2, o['h'], (o['x'], -1, o['z'])))
for key in ('help_button', 'mode_button'):
    b = P[key]
    lid = lid.cut(cyl(b['dia'] / 2, t + 2, (b['x'], -1, b['z']), (0, 1, 0)))
bz = P['buzzer_grille']
for i in range(bz['holes']):
    lid = lid.cut(cyl(bz['dia'] / 2, t + 2, (bz['x'] + (i - 2) * bz['pitch'], -1, bz['z']), (0, 1, 0)))
sl = P['status_led']
lid = lid.cut(cyl(sl['dia'] / 2, t + 2, (sl['x'], -1, sl['z']), (0, 1, 0)))
add('enclosure_lid', lid, '#eef0ea', 'enclosure', 'Front panel: OLED window, HELP and MODE buttons, status LED, buzzer grille')
add('status_led', cyl(2.5, 6, (sl['x'], -4, sl['z']), (0, 1, 0)).fuse(cyl(4.2, 2, (sl['x'], -2, sl['z']), (0, 1, 0))), '#e04a3a', 'hmi', sl['note'])

# Clear window and button caps (for the render)
add('oled_glass', box(o['w'] - 1, 1, o['h'] - 1, (o['x'] + .5, 1, o['z'] + .5)), '#1e2a35', 'hmi', 'Polycarbonate window over OLED')
hb = P['help_button']
add('help_button', cyl(hb['dia'] / 2 - .5, 6, (hb['x'], -5, hb['z']), (0, 1, 0)).fuse(cyl(hb['dia'] / 2 + 2.5, 2, (hb['x'], -2, hb['z']), (0, 1, 0))), '#c8372d', 'hmi', hb['note'])
mb = P['mode_button']
add('mode_button', cyl(mb['dia'] / 2 - .5, 5, (mb['x'], -4, mb['z']), (0, 1, 0)).fuse(cyl(mb['dia'] / 2 + 2, 2, (mb['x'], -2, mb['z']), (0, 1, 0))), '#2f6f8f', 'hmi', mb['note'])
add('ack_button', cyl(a['dia'] / 2 - .5, 5, (W - 3, a['y'], a['z']), (1, 0, 0)).fuse(cyl(a['dia'] / 2 + 2, 2, (W, a['y'], a['z']), (1, 0, 0))), '#2b2b2b', 'hmi', a['note'])

# Glands (visual envelope: hex nut + dome below the floor)
glands = []
for x in g['xs']:
    glands.append(cyl(9.5, 4, (x, g['y'], -4)).fuse(cyl(7, 12, (x, g['y'], -16))))
glands.append(cyl(8, 6, (-6, v['y'], v['z']), (1, 0, 0)))
add('glands_and_vent', cq.Compound.makeCompound(glands), '#3a3a3a', 'enclosure', g['note'])

# ---------------- internals, mounted on a plate against the back wall ----------------
ip = P['internal_plate']
py = D - t - ip['t']
add('mounting_plate', box(ip['w'], ip['t'], ip['h'], ((W - ip['w']) / 2, py, (H - ip['h']) / 2)), '#b6bcc2', 'internals', 'Galvanised/Al mounting plate')
mbd = P['main_board']
by = py - mbd['standoff'] - 1.6
add('main_board', box(mbd['w'], 1.6, mbd['h'], (mbd['x'], by, mbd['z'])), '#3f7d4e', 'internals', mbd['note'])
es = P['esp32']
add('esp32_devkitc', box(es['w'], es['t'], es['h'], (es['x'], by - es['t'], es['z'])), '#26303a', 'internals', es['note'])
add('esp32_shield_can', box(18, 3.2, 25.5, (es['x'] + 30, by - es['t'] - 3.2, es['z'] + 1.2)), '#a9adb1', 'internals', 'WROOM module can; antenna end clear of metal')
for key, col in (('ina219', '#6b4fa0'), ('buck', '#2d5fa3'), ('fuse', '#b07a2a')):
    c = P[key]
    add(key, box(c['w'], c['t'], c['h'], (c['x'], py - 6 - c['t'], c['z'])), col, 'internals', c.get('note', ''))
add('oled_module', box(27.3, 4, 27.8, (o['x'] - 1.2, t + 1, o['z'] - 8)), '#1b4f72', 'hmi', 'SSD1306 0.96 in I2C module behind window')
add('buzzer', cyl(6, 9.5, (bz['x'], t + 1, bz['z']), (0, 1, 0)), '#222222', 'hmi', '12 mm active buzzer behind grille')
add('terminal_blocks', box(70, 9, 10, (20, by - 9, 10)), '#1f6fb2', 'internals', '5.08 mm pluggable terminals for field wiring')

# ---------------- back bracket ----------------
bk = P['bracket']
bx0, bz0 = W / 2 - bk['W'] / 2, H / 2 - bk['H'] / 2
bracket = box(bk['W'], bk['t'], bk['H'], (bx0, D, bz0))
for dx, dz in bk['wall_holes']:
    bracket = bracket.cut(cyl(bk['wall_hole_dia'] / 2, bk['t'] + 2, (W / 2 + dx, D - 1, H / 2 + dz), (0, 1, 0)))
cs = bk['clamp_slots']
for dx in cs['xs']:
    for dz in cs['zs']:
        bracket = bracket.cut(box(cs['w'], bk['t'] + 2, cs['h'] / 2, (W / 2 + dx - cs['w'] / 2, D - 1, H / 2 + dz - cs['h'] / 4)))
add('back_bracket', bracket, '#8f9aa3', 'mounting', bk['note'])

# ---------------- radiation shield + SHT31 (shown beside the box, own bracket) ----------------
sh = P['shield']
sx, sy, sz = -140, 35, 0
plates = []
for i in range(sh['plates']):
    pl = cyl(sh['plate_dia'] / 2, sh['t'], (sx, sy, sz + i * sh['pitch']))
    if i < sh['plates'] - 1:
        pl = pl.cut(cyl(sh['inner_hole'] / 2, sh['t'] + 2, (sx, sy, sz + i * sh['pitch'] - 1)))
    plates.append(pl)
rods = [cyl(2.5, sh['pitch'] * (sh['plates'] - 1) + sh['t'], (sx + dx, sy + dy, sz)) for dx, dy in ((sh['rod_r'], 0), (-sh['rod_r'] / 2, sh['rod_r'] * .866), (-sh['rod_r'] / 2, -sh['rod_r'] * .866))]
add('radiation_shield', cq.Compound.makeCompound(plates + rods), '#f4f4ef', 'sensor', sh['note'])
add('sht31_in_shield', box(12.7, 2.6, 18, (sx - 6.35, sy - 1.3, sz + 18)), '#2a7a5a', 'sensor', 'SHT31 module at plate-stack centre')

# ---------------- fan module (shown above the box for scale) ----------------
f = P['fan']
fx, fy, fz = W + 60, 10, 0
frame = box(f['size'], f['depth'], f['size'], (fx, fy, fz)).cut(cyl(58, f['depth'] + 2, (fx + 60, fy - 1, fz + 60), (0, 1, 0)))
hub = cyl(20, f['depth'] - 4, (fx + 60, fy + 2, fz + 60), (0, 1, 0))
blades = [box(36, 3, 12, (fx + 60 + 18, fy + 10, fz + 54)).rotate(cq.Vector(fx + 60, 0, fz + 60), cq.Vector(fx + 60, 1, fz + 60), k * 360 / 7) for k in range(7)]
add('fan_120', cq.Compound.makeCompound([frame, hub] + blades), '#3b4048', 'actuator', f['note'])
guard = [cq.Solid.makeTorus(r, 1.2, cq.Vector(fx + 60, fy - 2, fz + 60), cq.Vector(0, 1, 0)) for r in (20, 36, 52)]
add('fan_guard', cq.Compound.makeCompound(guard), '#9aa0a6', 'actuator', 'Wire guard, both faces')

asm.save(str(O / 'SAAYA_NODE_v1.step'))
(O / 'node.json').write_text(json.dumps({'revision': 'NODE-v1', 'units': 'mm', 'status': 'FIT/PLACEMENT MODEL - NOT A MANUFACTURING RELEASE',
                                         'parameters': P, 'parts': parts}, indent=1))
S = R.parents[1] / 'site' / 'node'
S.mkdir(exist_ok=True)
for p in O.iterdir():
    shutil.copy2(p, S / p.name)
print('SAAYA Node v1:', len(parts), 'parts; STEP + STL + node.json')

# ---------------- interference check (solid intersections > 1 mm^3) ----------------
shapes = {p['name']: None for p in parts}
for child in asm.children:
    shapes[child.name] = child.obj
names = [n for n in shapes if shapes[n] is not None]
clashes = []
for i, a_ in enumerate(names):
    for b_ in names[i + 1:]:
        sa, sb = shapes[a_], shapes[b_]
        ba, bb_ = sa.BoundingBox(), sb.BoundingBox()
        if ba.xmax < bb_.xmin or bb_.xmax < ba.xmin or ba.ymax < bb_.ymin or bb_.ymax < ba.ymin or ba.zmax < bb_.zmin or bb_.zmax < ba.zmin:
            continue
        vol = sa.intersect(sb).Volume()
        if vol > 1:
            clashes.append({'a': a_, 'b': b_, 'mm3': round(vol, 1)})
(O / 'interference.json').write_text(json.dumps({'checked_pairs': len(names) * (len(names) - 1) // 2, 'clashes': clashes}, indent=1))
shutil.copy2(O / 'interference.json', S / 'interference.json')
print('Interference:', clashes or 'none above 1 mm^3')
