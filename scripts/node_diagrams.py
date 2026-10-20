"""Generate the SAAYA Node interfacing diagram, dimensioned enclosure drawing and installation
elevation as SVG (docs/node/ and site/node/). Geometry is read from cad/node/exports/node.json
so drawings and CAD cannot drift apart. Run: python scripts/node_diagrams.py
"""
from pathlib import Path
import json, html, shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'node'
OUT.mkdir(parents=True, exist_ok=True)
P = json.loads((ROOT / 'cad/node/exports/node.json').read_text())['parameters']
FONT = "font-family='Helvetica,Arial,sans-serif'"
C = {'12v': '#d6332b', '5v': '#e08a17', '3v3': '#7a3db8', 'gnd': '#1d1d1d', 'sda': '#1f6fd1', 'scl': '#0aa0a0',
     'sig': '#2e8b3d', 'ink': '#1f2a26', 'muted': '#5d6b64', 'box': '#f6f7f3', 'line': '#9aa59f'}
e = html.escape


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.b = w, h, []

    def add(self, s):
        self.b.append(s)

    def text(self, x, y, s, size=13, anchor='start', weight='normal', color=None, italic=False):
        st = " font-style='italic'" if italic else ''
        self.add(f"<text x='{x}' y='{y}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' fill='{color or C['ink']}'{st}>{e(s)}</text>")

    def rect(self, x, y, w, h, fill=None, stroke=None, rx=4, sw=1.2, dash=None):
        d = f" stroke-dasharray='{dash}'" if dash else ''
        self.add(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rx}' fill='{fill or C['box']}' stroke='{stroke or C['ink']}' stroke-width='{sw}'{d}/>")

    def wire(self, pts, color, width=2.2, label=None, lpos=None, dash=None):
        d = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
        da = f" stroke-dasharray='{dash}'" if dash else ''
        self.add(f"<path d='{d}' fill='none' stroke='{color}' stroke-width='{width}' stroke-linejoin='round'{da}/>")
        for x, y in (pts[0], pts[-1]):
            self.add(f"<circle cx='{x}' cy='{y}' r='3' fill='{color}'/>")
        if label:
            x, y = lpos or pts[len(pts) // 2]
            self.text(x, y, label, 11, 'middle', color=color)

    def resistor(self, x, y, label, vertical=False):
        if vertical:
            self.rect(x - 6, y - 16, 12, 32, '#fff', C['ink'], 2, 1.2)
            self.text(x + 10, y + 4, label, 11)
        else:
            self.rect(x - 16, y - 6, 32, 12, '#fff', C['ink'], 2, 1.2)
            self.text(x, y - 10, label, 11, 'middle')

    def save(self, name, title):
        body = '\n'.join(self.b)
        svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{self.w}' height='{self.h}' viewBox='0 0 {self.w} {self.h}' {FONT}>"
               f"<title>{e(title)}</title><rect width='{self.w}' height='{self.h}' fill='#ffffff'/>{body}</svg>")
        (OUT / name).write_text(svg)
        return OUT / name


def module(s, x, y, w, title, sub, pins, side='left', pitch=24, color='#eef3ee'):
    """Box with pins on one side; returns {pin: (x, y)} at the box edge."""
    h = 34 + pitch * len(pins)
    s.rect(x, y, w, h, color, C['ink'], 6, 1.4)
    s.text(x + w / 2, y + 17, title, 13, 'middle', 'bold')
    if sub:
        s.text(x + w / 2, y + 30, sub, 10.5, 'middle', color=C['muted'])
    out = {}
    for i, p in enumerate(pins):
        py = y + 46 + i * pitch
        px = x if side == 'left' else x + w
        s.add(f"<line x1='{px - 7 if side == 'left' else px}' y1='{py}' x2='{px if side == 'left' else px + 7}' y2='{py}' stroke='{C['ink']}' stroke-width='2'/>")
        s.text(px + (8 if side == 'left' else -8), py + 4, p, 11.5, 'start' if side == 'left' else 'end')
        out[p] = (px - 7 if side == 'left' else px + 7, py)
    return out


# ============================ 1. Interfacing diagram ============================
s = Svg(1800, 1240)
s.text(40, 46, 'SAAYA Node v1 - interfacing diagram (ESP32-DevKitC V4, 3.3 V logic)', 24, weight='bold')
s.text(40, 72, 'All signal levels 3.3 V. Fan 12 V. Grounds common (star point at buck converter GND). Pin names = DevKitC V4 header silk-screen. Firmware: firmware/src/main.cpp', 13, color=C['muted'])

# ESP32 with the real DevKitC V4 header order
EX, EY, EW = 770, 160, 240
left = ['3V3', 'EN', 'VP/36', 'VN/39', 'IO34', 'IO35', 'IO32', 'IO33', 'IO25', 'IO26', 'IO27', 'IO14', 'IO12', 'GND', 'IO13', 'SD2', 'SD3', 'CMD', '5V']
right = ['GND', 'IO23', 'IO22', 'TXD0', 'RXD0', 'IO21', 'GND', 'IO19', 'IO18', 'IO5', 'IO17', 'IO16', 'IO4', 'IO0', 'IO2', 'IO15', 'SD1', 'SD0', 'CLK']
used_l = {'3V3', 'IO34', 'IO35', 'IO32', 'IO33', 'IO25', 'IO26', 'IO27', 'IO14', 'GND', '5V'}
used_r = {'GND', 'IO22', 'IO21', 'IO4'}
PIT = 34
EH = 110 + PIT * len(left) + 40
s.rect(EX, EY, EW, EH, '#26303a', '#11171c', 10, 2)
s.rect(EX + 60, EY + 14, 120, 70, '#a9adb1', '#5b6066', 4, 1)
s.text(EX + EW / 2, EY + 46, 'ESP32-WROOM-32E', 12, 'middle', 'bold', '#1b1b1b')
s.text(EX + EW / 2, EY + 62, 'Wi-Fi / BT antenna end', 9.5, 'middle', color='#1b1b1b')
s.text(EX + EW / 2, EY + EH - 30, 'ESP32-DevKitC V4', 15, 'middle', 'bold', '#ffffff')
s.text(EX + EW / 2, EY + EH - 12, 'micro-USB (programming only)', 10.5, 'middle', color='#c9d1d9')
L, Rr = {}, {}
for i, p in enumerate(left):
    y = EY + 110 + i * PIT
    col = '#ffd27a' if p in used_l else '#7d8790'
    s.add(f"<circle cx='{EX + 14}' cy='{y}' r='5' fill='{col}'/>")
    s.text(EX + 26, y + 4, p, 12, color='#ffffff' if p in used_l else '#8f99a3', weight='bold' if p in used_l else 'normal')
    L.setdefault(p, (EX, y))
for i, p in enumerate(right):
    y = EY + 110 + i * PIT
    col = '#ffd27a' if p in used_r else '#7d8790'
    s.add(f"<circle cx='{EX + EW - 14}' cy='{y}' r='5' fill='{col}'/>")
    s.text(EX + EW - 26, y + 4, p, 12, 'end', color='#ffffff' if p in used_r else '#8f99a3', weight='bold' if p in used_r else 'normal')
    Rr.setdefault(p, (EX + EW, y))
GNDL = L['GND']

# ---------- left side: fan + PWM stage ----------
fan = module(s, 60, 120, 190, 'Arctic P12 Pro 120 mm', '12 V 4-wire PWM, tach 2 p/rev', ['1 GND', '2 +12 V', '3 TACH', '4 PWM'], 'right', 26, '#eef1f6')
# Q1 2N3904 stage between fan PWM and IO25
qx, qy = 430, 230
s.add(f"<circle cx='{qx}' cy='{qy}' r='18' fill='#fff' stroke='{C['ink']}' stroke-width='1.4'/>")
s.text(qx, qy + 4, 'Q1', 11, 'middle', 'bold')
s.text(qx, qy + 34, '2N3904', 10.5, 'middle', color=C['muted'])
s.wire([fan['4 PWM'], (qx, fan['4 PWM'][1]), (qx, qy - 18)], C['sig'], label='collector', lpos=(qx - 40, qy - 26))
s.resistor(560, qy, '4.7 kΩ')
s.wire([(qx + 18, qy), (544, qy)], C['sig'])
s.wire([(576, qy), (690, qy), (690, L['IO25'][1]), L['IO25']], C['sig'], label='IO25 PWM 25 kHz (inverted)', lpos=(700, qy - 22))
s.resistor(470, 290, '10 kΩ B-E', vertical=True)
s.wire([(470, qy), (470, 274)], C['ink'], 1.4)
s.wire([(470, 306), (470, 330)], C['gnd'], 1.6)
s.wire([(qx, qy + 18), (qx, 330), (470, 330)], C['gnd'], 1.6, label='E → GND', lpos=(400, 344))
# tach with pull-up
s.wire([fan['3 TACH'], (330, fan['3 TACH'][1]), (330, 380), (710, 380), (710, L['IO34'][1]), L['IO34']], C['sig'], label='TACH → IO34 (input-only)', lpos=(520, 374))
s.resistor(330, 410, '10 kΩ to 3V3', vertical=True)
s.wire([(330, 380), (330, 394)], C['ink'], 1.4)
s.wire([(330, 426), (330, 444)], C['3v3'], 1.6, label='3V3', lpos=(355, 452))

# ---------- float switch ----------
fl = module(s, 60, 470, 190, 'Float switch (water)', 'dry reed contact, NO', ['A', 'B → GND'], 'right', 26, '#eef6f6')
s.wire([fl['A'], (730, fl['A'][1]), (730, L['IO35'][1]), L['IO35']], C['sig'], label='IO35 (input-only): closed = water OK', lpos=(470, fl['A'][1] - 8))
s.resistor(300, fl['A'][1] + 40, '10 kΩ to 3V3', vertical=True)
s.wire([(300, fl['A'][1]), (300, fl['A'][1] + 24)], C['ink'], 1.4)
s.text(318, fl['A'][1] + 70, 'external pull-up (no internal on IO34-39)', 10, color=C['muted'])

# ---------- buttons ----------
bt = module(s, 60, 640, 190, 'Panel buttons', '12 mm IP65 momentary, to GND', ['MODE', 'HELP', 'ACK'], 'right', 30, '#f6f1ea')
for name, pin, lab in (('MODE', 'IO32', 'IO32 mode (internal pull-up)'), ('HELP', 'IO33', 'IO33 help latch → flash'), ('ACK', 'IO27', 'IO27 staff acknowledge')):
    x0 = {'MODE': 600, 'HELP': 640, 'ACK': 670}[name]
    s.wire([bt[name], (x0, bt[name][1]), (x0, L[pin][1]), L[pin]], C['sig'], label=lab, lpos=(420, bt[name][1] - 7))

# ---------- LED + buzzer ----------
ld = module(s, 60, 820, 190, 'Status LED', '5 mm red, panel bezel', ['Anode', 'Cathode → GND'], 'right', 26, '#f6ecec')
s.resistor(420, ld['Anode'][1], '330 Ω')
s.wire([ld['Anode'], (404, ld['Anode'][1])], C['sig'])
s.wire([(436, ld['Anode'][1]), (620, ld['Anode'][1]), (620, L['IO26'][1]), L['IO26']], C['sig'], label='IO26 (~8 mA)', lpos=(530, ld['Anode'][1] - 8))
bz = module(s, 60, 960, 190, 'Active buzzer SFM-27', '3-24 V, <12 mA, >95 dB', ['+ (12 V)', '−'], 'right', 26, '#f6ecec')
q2x, q2y = 430, bz['−'][1] + 40
s.add(f"<circle cx='{q2x}' cy='{q2y}' r='18' fill='#fff' stroke='{C['ink']}' stroke-width='1.4'/>")
s.text(q2x, q2y + 4, 'Q2', 11, 'middle', 'bold')
s.text(q2x + 26, q2y + 30, '2N3904 low-side', 10.5, color=C['muted'])
s.wire([bz['−'], (q2x, bz['−'][1]), (q2x, q2y - 18)], C['ink'], 1.6)
s.resistor(560, q2y, '4.7 kΩ')
s.wire([(q2x + 18, q2y), (544, q2y)], C['sig'])
s.wire([(576, q2y), (650, q2y), (650, L['IO14'][1]), L['IO14']], C['sig'], label='IO14 buzzer', lpos=(680, q2y - 22))
s.wire([(q2x, q2y + 18), (q2x, q2y + 40)], C['gnd'], 1.6, label='GND', lpos=(q2x + 22, q2y + 44))
s.wire([bz['+ (12 V)'], (310, bz['+ (12 V)'][1]), (310, 1196), (775, 1196), (775, 1142)], C['12v'], 2, label='12 V (after fuse)', lpos=(370, 1110))

# ---------- right side: I2C bus ----------
BX = 1250
sda_x, scl_x = 1120, 1150
s.wire([Rr['IO21'], (sda_x, Rr['IO21'][1]), (sda_x, 1060)], C['sda'], 3, label='SDA', lpos=(sda_x - 20, Rr['IO21'][1] - 8))
s.wire([Rr['IO22'], (scl_x, Rr['IO22'][1]), (scl_x, 1060)], C['scl'], 3, label='SCL', lpos=(scl_x + 20, Rr['IO22'][1] - 8))
s.text(1250, 152, 'I²C bus 0 @ 50 kHz · one 4.7 kΩ pull-up pair to 3V3', 12, 'start', 'bold', C['sda'])
s.text(1250, 168, '(breakout boards add their own pull-ups in parallel: keep total ≥ 2 kΩ)', 10, color=C['muted'])
devs = [
    ('SHT30 - seat air', 'addr 0x44 (ADDR→GND) · in radiation shield', 180),
    ('SHT30 - reference air', 'addr 0x45 (ADDR→3V3) · ≤5 m STP cable', 360),
    ('SSD1306 0.96" OLED', 'addr 0x3C · 128×64', 540),
    ('INA219 power monitor', 'addr 0x40 (A0,A1→GND) · 0.1 Ω shunt', 720),
]
for title, sub, y in devs:
    m = module(s, BX, y, 300, title, sub, ['VCC (3V3)', 'GND', 'SDA', 'SCL'], 'left', 26, '#eef1fb')
    s.wire([(sda_x, m['SDA'][1]), m['SDA']], C['sda'], 2.2)
    s.wire([(scl_x, m['SCL'][1]), m['SCL']], C['scl'], 2.2)
    s.wire([(1190, m['VCC (3V3)'][1]), m['VCC (3V3)']], C['3v3'], 1.8)
    s.wire([(1210, m['GND'][1]), m['GND']], C['gnd'], 1.8)
s.wire([(1190, 200), (1190, 830)], C['3v3'], 1.8)
s.wire([(1210, 200), (1210, 856)], C['gnd'], 1.8)
s.wire([L['3V3'], (EX - 40, L['3V3'][1]), (EX - 40, 128), (1190, 128), (1190, 200)], C['3v3'], 2.2, label='3V3 rail (onboard LDO, ~500 mA budget)', lpos=(980, 122))
s.wire([Rr['GND'], (1210, Rr['GND'][1]), (1210, 200)], C['gnd'], 2.2)
# INA219 high side
s.text(BX + 292, 784, 'VIN+  12 V in', 11.5, 'end', color=C['12v'])
s.text(BX + 292, 804, 'VIN−  to fan', 11.5, 'end', color=C['12v'])
s.text(BX + 292, 824, 'fan branch only', 10, 'end', color=C['muted'])
# DS18B20
ds = module(s, BX, 900, 300, 'DS18B20 roof probe', '1-Wire · waterproof · on roof underside', ['VDD (3V3)', 'GND', 'DQ'], 'left', 26, '#f1eefb')
s.wire([Rr['IO4'], (1080, Rr['IO4'][1]), (1080, ds['DQ'][1]), ds['DQ']], C['sig'], label='IO4 1-Wire', lpos=(1095, Rr['IO4'][1] + 18))
s.resistor(1235, ds['DQ'][1] + 40, '4.7 kΩ DQ→3V3', vertical=True)
s.wire([(1235, ds['DQ'][1]), (1235, ds['DQ'][1] + 24)], C['ink'], 1.4)
s.wire([(1190, ds['VDD (3V3)'][1]), ds['VDD (3V3)']], C['3v3'], 1.8)
s.wire([(1210, ds['GND'][1]), ds['GND']], C['gnd'], 1.8)
s.wire([(1190, 830), (1190, ds['VDD (3V3)'][1])], C['3v3'], 1.8)
s.wire([(1210, 856), (1210, ds['GND'][1])], C['gnd'], 1.8)

# ---------- power (bottom) ----------
py0 = 1120
s.rect(560, py0 - 30, 1180, 104, '#fff8f2', C['12v'], 8, 1.2, '6 4')
s.text(575, py0 - 10, 'POWER', 13, weight='bold', color=C['12v'])
pw = [('12 V 2 A SMPS', 'IEC-rated, in shade', 600), ('Fuse 1 A T', '5×20 holder', 790), ('Rocker switch', '12 V DC', 950), ('MP1584 buck', '12 V → 5.0 V, 3 A', 1130)]
for title, sub, x in pw:
    s.rect(x, py0, 150, 44, '#ffffff', C['12v'], 5, 1.3)
    s.text(x + 75, py0 + 19, title, 12, 'middle', 'bold')
    s.text(x + 75, py0 + 35, sub, 10, 'middle', color=C['muted'])
s.wire([(750, py0 + 22), (790, py0 + 22)], C['12v'], 3)
s.wire([(940, py0 + 22), (950, py0 + 22)], C['12v'], 3)
s.wire([(1100, py0 + 22), (1130, py0 + 22)], C['12v'], 3)
s.wire([(1075, py0), (1075, py0 - 20), (1660, py0 - 20), (1660, 780), (BX + 300 + 7, 780)], C['12v'], 3, label='12 V → INA219 VIN+ → fan', lpos=(1500, py0 - 38))
s.wire([fan['2 +12 V'], (290, fan['2 +12 V'][1]), (290, 96), (1700, 96), (1700, 800), (BX + 300 + 7, 800)], C['12v'], 3, label='fan +12 V ← INA219 VIN−', lpos=(1000, 90))
s.wire([(1280, py0 + 22), (1320, py0 + 22), (1320, py0 - 60), (EX - 60, py0 - 60), (EX - 60, L['5V'][1]), L['5V']], C['5v'], 3, label='5 V → DevKitC 5V pin (not with USB connected)', lpos=(1040, py0 - 66))
s.wire([GNDL, (EX - 80, GNDL[1]), (EX - 80, 1210), (1205, 1210), (1205, py0 + 44)], C['gnd'], 3, label='common GND star', lpos=(980, 1226))
s.wire([fan['1 GND'], (270, fan['1 GND'][1]), (270, 1210), (EX - 80, 1210)], C['gnd'], 2)

# legend
lx, ly = 1450, 40
for i, (k, lab) in enumerate((('12v', '12 V'), ('5v', '5 V'), ('3v3', '3.3 V'), ('gnd', 'GND'), ('sda', 'I²C SDA'), ('scl', 'I²C SCL'), ('sig', 'GPIO signal'))):
    x = lx + (i % 4) * 85
    y = ly + (i // 4) * 20
    s.add(f"<line x1='{x}' y1='{y}' x2='{x + 22}' y2='{y}' stroke='{C[k]}' stroke-width='4'/>")
    s.text(x + 27, y + 4, lab, 11)
s.save('interfacing-diagram.svg', 'SAAYA Node interfacing diagram')

# ============================ 2. Dimensioned enclosure drawing ============================
E = P['enclosure']; W, H, D = E['W'], E['H'], E['D']
d = Svg(1700, 1180)
d.text(40, 46, 'SAAYA Node v1 - enclosure drilling and mounting drawing', 24, weight='bold')
d.text(40, 72, f'All dimensions in mm. Datum: front-left-bottom corner. Purchased IP65 ABS box {W} × {H} × {D} (ProtechT WPE16); machine holes to this plan.', 13, color=C['muted'])
SC = 3.0


def dim_h(sv, x1, x2, y, label, up=True):
    sv.add(f"<line x1='{x1}' y1='{y}' x2='{x2}' y2='{y}' stroke='{C['ink']}' stroke-width='1' marker-start='url(#ar)' marker-end='url(#ar)'/>")
    sv.text((x1 + x2) / 2, y - 6 if up else y + 15, label, 12, 'middle')


def dim_v(sv, x, y1, y2, label):
    sv.add(f"<line x1='{x}' y1='{y1}' x2='{x}' y2='{y2}' stroke='{C['ink']}' stroke-width='1' marker-start='url(#ar)' marker-end='url(#ar)'/>")
    sv.add(f"<text x='{x - 8}' y='{(y1 + y2) / 2}' font-size='12' text-anchor='middle' fill='{C['ink']}' transform='rotate(-90 {x - 8} {(y1 + y2) / 2})'>{e(label)}</text>")


d.add("<defs><marker id='ar' markerWidth='8' markerHeight='8' refX='4' refY='4' orient='auto-start-reverse'><path d='M0,1 L7,4 L0,7' fill='none' stroke='#1f2a26'/></marker></defs>")
# FRONT VIEW (X right, Z up) at origin (fx, fy) = bottom-left
fx, fy = 110, 470
d.text(fx, fy - H * SC - 40, 'FRONT VIEW (lid)', 15, weight='bold')
d.rect(fx, fy - H * SC, W * SC, H * SC, '#f4f5f1', C['ink'], 8, 1.8)
o = P['oled_window']
d.rect(fx + o['x'] * SC, fy - (o['z'] + o['h']) * SC, o['w'] * SC, o['h'] * SC, '#1e2a35', C['ink'], 2, 1.2)
d.text(fx + (o['x'] + o['w'] / 2) * SC, fy - (o['z'] + o['h']) * SC - 8, f"OLED window {o['w']}×{o['h']}", 11, 'middle')
for key, col, lab in (('help_button', '#c8372d', 'HELP Ø12'), ('mode_button', '#2f6f8f', 'MODE Ø12'), ('status_led', '#e04a3a', 'LED Ø8')):
    b = P[key]
    d.add(f"<circle cx='{fx + b['x'] * SC}' cy='{fy - b['z'] * SC}' r='{b['dia'] / 2 * SC}' fill='{col}' stroke='{C['ink']}'/>")
    d.text(fx + b['x'] * SC - b['dia'] / 2 * SC - 8, fy - b['z'] * SC + 4, lab, 11, 'end')
bzz = P['buzzer_grille']
for i in range(bzz['holes']):
    d.add(f"<circle cx='{fx + (bzz['x'] + (i - 2) * bzz['pitch']) * SC}' cy='{fy - bzz['z'] * SC}' r='{bzz['dia'] / 2 * SC}' fill='#333'/>")
d.text(fx + bzz['x'] * SC, fy - bzz['z'] * SC + 24, '5 × Ø2 buzzer, pitch 5', 11, 'middle')
dim_h(d, fx, fx + W * SC, fy + 40, f'{W}', up=False)
dim_v(d, fx - 30, fy, fy - H * SC, f'{H}')
dim_h(d, fx, fx + P['help_button']['x'] * SC, fy + 70, f"{P['help_button']['x']} (button/LED axis)", up=False)
dim_v(d, fx + W * SC + 30, fy, fy - P['help_button']['z'] * SC, f"{P['help_button']['z']}")
dim_v(d, fx + W * SC + 60, fy, fy - P['mode_button']['z'] * SC, f"{P['mode_button']['z']}")
dim_v(d, fx + W * SC + 90, fy, fy - P['status_led']['z'] * SC, f"{P['status_led']['z']}")
dim_h(d, fx + o['x'] * SC, fx + (o['x'] + o['w']) * SC, fy - o['z'] * SC + 20, f"x {o['x']}–{o['x'] + o['w']}, z {o['z']}–{o['z'] + o['h']}", up=False)

# BOTTOM VIEW (X right, Y down = into wall)
bx, by = 110, 640
g = P['glands_bottom']; v = P['vent_side']
d.text(bx, by - 18, 'BOTTOM VIEW (cable entries face the ground)', 15, weight='bold')
d.rect(bx, by, W * SC, D * SC, '#f4f5f1', C['ink'], 8, 1.8)
d.add(f"<line x1='{bx}' y1='{by + E['lid_depth'] * SC}' x2='{bx + W * SC}' y2='{by + E['lid_depth'] * SC}' stroke='{C['line']}' stroke-dasharray='6 4'/>")
d.text(bx + W * SC + 8, by + E['lid_depth'] * SC + 4, f"lid joint {E['lid_depth']}", 11)
for x, lab in zip(g['xs'], g['labels']):
    d.add(f"<circle cx='{bx + x * SC}' cy='{by + g['y'] * SC}' r='{g['dia'] / 2 * SC}' fill='#fff' stroke='{C['ink']}' stroke-width='1.4'/>")
    d.text(bx + x * SC, by + g['y'] * SC + 4, f'{x}', 10.5, 'middle')
    d.add(f"<text x='{bx + x * SC}' y='{by + D * SC + 18}' font-size='10.5' text-anchor='end' fill='{C['ink']}' transform='rotate(-35 {bx + x * SC} {by + D * SC + 18})'>{e(lab)}</text>")
dim_v(d, bx - 30, by + g['y'] * SC, by, f"{g['y']}")
dim_v(d, bx - 60, by + D * SC, by, f'{D}')
d.text(bx, by + D * SC + 92, f"5 × PG7 Ø{g['dia']} at x = {', '.join(map(str, g['xs']))} on y = {g['y']} (centre of the body). PG7 nut ≈19 across corners: 30 mm pitch leaves 11 mm for a spanner.", 12)
d.text(bx, by + D * SC + 110, f"M12 breathable vent Ø{v['dia']} on the LEFT wall at y = {v['y']}, z = {v['z']}.", 12)

# RIGHT SIDE VIEW
rx, ry = 760, 470
a = P['ack_button']
d.text(rx, ry - H * SC - 40, 'RIGHT SIDE VIEW (staff ACK button)', 15, weight='bold')
d.rect(rx, ry - H * SC, D * SC, H * SC, '#f4f5f1', C['ink'], 8, 1.8)
d.add(f"<line x1='{rx + E['lid_depth'] * SC}' y1='{ry - H * SC}' x2='{rx + E['lid_depth'] * SC}' y2='{ry}' stroke='{C['line']}' stroke-dasharray='6 4'/>")
d.add(f"<circle cx='{rx + a['y'] * SC}' cy='{ry - a['z'] * SC}' r='{a['dia'] / 2 * SC}' fill='#2b2b2b'/>")
d.text(rx + a['y'] * SC, ry - a['z'] * SC - 26, 'ACK Ø12', 11, 'middle')
dim_h(d, rx, rx + a['y'] * SC, ry + 40, f"{a['y']}", up=False)
dim_h(d, rx, rx + D * SC, ry + 70, f'{D}', up=False)
dim_v(d, rx + D * SC + 30, ry, ry - a['z'] * SC, f"{a['z']}")
d.text(rx, ry + 110, 'Front (lid) on the left. Bracket 3 mm behind the back face.', 11, color=C['muted'])

# BRACKET
bk = P['bracket']; kx, ky = 1090, 140; KS = 2.2
d.text(kx, ky - 14, 'BACK BRACKET (3 mm aluminium)', 15, weight='bold')
d.rect(kx, ky, bk['W'] * KS, bk['H'] * KS, '#e6eaee', C['ink'], 4, 1.6)
cxk, czk = kx + bk['W'] * KS / 2, ky + bk['H'] * KS / 2
for dx, dz in bk['wall_holes']:
    d.add(f"<circle cx='{cxk + dx * KS}' cy='{czk - dz * KS}' r='{bk['wall_hole_dia'] / 2 * KS}' fill='#fff' stroke='{C['ink']}'/>")
cs = bk['clamp_slots']
for dx in cs['xs']:
    for dz in cs['zs']:
        d.rect(cxk + (dx - cs['w'] / 2) * KS, czk - (dz + cs['h'] / 4) * KS, cs['w'] * KS, cs['h'] / 2 * KS, '#fff', C['ink'], 3, 1)
d.add(f"<rect x='{cxk - W / 2 * KS}' y='{czk - H / 2 * KS}' width='{W * KS}' height='{H * KS}' fill='none' stroke='{C['muted']}' stroke-dasharray='5 4'/>")
dim_h(d, kx, kx + bk['W'] * KS, ky + bk['H'] * KS + 28, f"{bk['W']}", up=False)
dim_v(d, kx - 22, ky + bk['H'] * KS, ky, f"{bk['H']}")
dim_h(d, cxk - 97 * KS, cxk + 97 * KS, ky + bk['H'] * KS + 58, '194 (wall holes Ø6.5)', up=False)
d.text(kx, ky + bk['H'] * KS + 100, '4 × Ø6.5 for M6 anchors, 194 × 90 centres', 12)
d.text(kx, ky + bk['H'] * KS + 118, '4 × 8 × 16 slots for two stainless hose clamps (post Ø 40–90)', 12)
d.text(kx, ky + bk['H'] * KS + 136, f'dashed: box outline {W} × {H}', 12, color=C['muted'])

# INTERNAL LAYOUT (looking at back plate from the front)
ix, iy = 1090, 940; IS = 2.6
d.text(ix, iy - H * IS - 18, f"INTERNAL LAYOUT (on {P['internal_plate']['w']} × {P['internal_plate']['h']} back plate)", 15, weight='bold')
d.rect(ix, iy - H * IS, W * IS, H * IS, '#fafbf8', C['ink'], 6, 1.2)
for key, col in (('main_board', '#3f7d4e'), ('esp32', '#26303a'), ('ina219', '#6b4fa0'), ('buck', '#2d5fa3'), ('fuse', '#b07a2a')):
    c = P[key]
    d.rect(ix + c['x'] * IS, iy - (c['z'] + c['h']) * IS, c['w'] * IS, c['h'] * IS, col, C['ink'], 2, 1)
    lab = {'main_board': '', 'esp32': 'ESP32-DevKitC', 'ina219': 'INA219', 'buck': 'MP1584', 'fuse': 'FUSE'}[key]
    d.text(ix + (c['x'] + c['w'] / 2) * IS, iy - (c['z'] + c['h'] / 2) * IS + 4, lab, 11, 'middle', 'bold', '#ffffff')
d.rect(ix + 20 * IS, iy - 20 * IS, 70 * IS, 10 * IS, '#1f6fb2', C['ink'], 2, 1)
d.text(ix + 55 * IS, iy - 13 * IS, 'field terminals', 10.5, 'middle', color='#fff')
d.text(ix + 55 * IS, iy - 80.5 * IS, 'perfboard 90 × 70: Q1, Q2, resistors, pull-ups', 10.5, 'middle', color=C['ink'])
d.text(ix, iy + 22, 'Antenna end of the WROOM can stays ≥15 mm from metal; cables enter from below only.', 11, color=C['muted'])
d.save('enclosure-drawing.svg', 'SAAYA Node enclosure drawing')

# ============================ 3. Installation elevation ============================
z = Svg(1460, 880)
z.add("<defs><marker id='ar' markerWidth='8' markerHeight='8' refX='4' refY='4' orient='auto-start-reverse'><path d='M0,1 L7,4 L0,7' fill='none' stroke='#1f2a26'/></marker></defs>")
z.text(40, 46, 'Installation - retrofit to an existing rest shade (side elevation, mm)', 24, weight='bold')
z.text(40, 72, 'Works on any shade with a post or wall: worksite rest shed, bus-stop shelter, FS-01 frame. Scale 1:25.', 13, color=C['muted'])
S25 = 1 / 4.2
gx, gy = 230, 800
X = lambda mm: gx + mm * S25
Y = lambda mm: gy - mm * S25
z.add(f"<line x1='40' y1='{gy}' x2='1440' y2='{gy}' stroke='#6b5b3e' stroke-width='3'/>")
z.text(50, gy + 22, 'ground (shaded ground cover preferred - see model)', 12, color='#6b5b3e')
# existing shade: post at x=0, roof at 2400
z.rect(X(0), Y(2400), 60 * S25 + 2, 2400 * S25, '#8a949b', C['ink'], 1, 1.2)
z.rect(X(-300), Y(2460), 3400 * S25, 60 * S25, '#c9cfc5', C['ink'], 2, 1.2)
z.text(X(1400), Y(2460) - 10, 'existing roof (paint underside / add lining)', 12, 'middle')
z.rect(X(2700), Y(2400), 60 * S25 + 2, 2400 * S25, '#8a949b', C['ink'], 1, 1.2)
# bench + seated person outline
z.rect(X(1100), Y(450), 1400 * S25, 40 * S25, '#ac805a', C['ink'], 2, 1)
z.add(f"<circle cx='{X(1500)}' cy='{Y(1150)}' r='{110 * S25}' fill='none' stroke='{C['muted']}' stroke-width='1.6'/>")
z.add(f"<path d='M{X(1500)},{Y(1040)} L{X(1500)},{Y(560)} L{X(1800)},{Y(520)}' fill='none' stroke='{C['muted']}' stroke-width='2'/>")
z.text(X(1500), Y(1300), 'seated worker', 11, 'middle', color=C['muted'])
# node box on post
z.rect(X(60), Y(1450), 70 * S25 + 2, 100 * S25, '#eef0ea', C['ink'], 2, 1.4)
z.text(X(150), Y(1500), 'SAAYA Node box', 12, weight='bold')
z.add(f"<line x1='{X(0) - 20}' y1='{Y(1400)}' x2='{X(0) - 20}' y2='{gy}' stroke='{C['ink']}' marker-start='url(#ar)' marker-end='url(#ar)'/>")
z.text(X(0) - 26, Y(700), '1400 (box centre)', 12, 'end')
# fan
z.rect(X(800), Y(1900), 25 * S25 + 3, 120 * S25, '#3b4048', C['ink'], 1, 1)
z.add(f"<path d='M{X(830)},{Y(1840)} L{X(1450)},{Y(1200)}' stroke='#5aa0d6' stroke-width='2' stroke-dasharray='8 6' marker-end='url(#ar)'/>")
z.text(X(840), Y(1960), '120 mm PWM fan, aimed at seat (~1 m, 30–45° down)', 12)
# seat sensor
z.rect(X(1950), Y(1150), 110 * S25, 70 * S25, '#f4f4ef', C['ink'], 2, 1.2)
z.text(X(2010), Y(1180), 'SHT31 seat (in shield)', 12, 'middle')
z.add(f"<line x1='{X(2110)}' y1='{Y(1100)}' x2='{X(2110)}' y2='{gy}' stroke='{C['ink']}' marker-start='url(#ar)' marker-end='url(#ar)'/>")
z.text(X(2090), Y(600), '1100 = seated head height', 12, 'end')
# roof probe
z.add(f"<circle cx='{X(1350)}' cy='{Y(2400) + 6}' r='6' fill='#6b4fa0'/>")
z.text(X(1370), Y(2290), 'DS18B20 bonded to roof underside, centre', 12)
# reference station outside
z.rect(X(4800), Y(1150), 110 * S25, 70 * S25, '#f4f4ef', C['ink'], 2, 1.2)
z.add(f"<line x1='{X(4855)}' y1='{Y(1080)}' x2='{X(4855)}' y2='{gy}' stroke='#8a949b' stroke-width='3'/>")
z.text(X(4855), Y(1230), 'SHT31 reference (in shield)', 12, 'middle')
z.add(f"<line x1='{X(2760)}' y1='{Y(300)}' x2='{X(4855)}' y2='{Y(300)}' stroke='{C['ink']}' marker-start='url(#ar)' marker-end='url(#ar)'/>")
z.text(X(3800), Y(300) - 8, '≥ 2000 from the shade edge, same 1100 height, ≤ 5 m cable', 12, 'middle')
# water
z.rect(X(300), Y(450), 250 * S25, 450 * S25, '#78aeb0', C['ink'], 3, 1)
z.text(X(425), Y(480), 'water can + float', 11, 'middle')
# cable route
z.add(f"<path d='M{X(95)},{Y(1400)} L{X(95)},{Y(2390)} L{X(2000)},{Y(2390)} L{X(2000)},{Y(1150)}' fill='none' stroke='{C['sig']}' stroke-width='1.6' stroke-dasharray='4 4'/>")
z.text(X(150), Y(2150), 'cables in UV conduit along post and roof; drip loop below box', 11, color=C['sig'])
z.save('installation-elevation.svg', 'SAAYA Node installation elevation')

site = ROOT / 'site' / 'node'
site.mkdir(exist_ok=True)
for f in OUT.glob('*.svg'):
    shutil.copy2(f, site / f.name)
print('Wrote', ', '.join(sorted(p.name for p in OUT.glob('*.svg'))))
