"""VIT-format project report for SAAYA Node (A4 portrait).

Two passes: the body is printed first, chapter/section/figure/table positions are read back
from hidden markers, then the front matter (with real page numbers in the contents) is printed
and both are merged. Page numbers are stamped afterwards: roman for front matter (title page
unnumbered), arabic from Chapter 1.

    python scripts/build_report.py      (needs node + playwright, pypdf, reportlab)
"""
from pathlib import Path
import html, json, re, runpy, subprocess, io

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'report'
IMG = OUT / 'img'
e = html.escape

g = runpy.run_path(str(ROOT / 'scripts' / 'build_node_pdf.py'))   # BOM, SPEC, PINS, POWER, SEL, DS, SRC, totals
P = g['P']; E = P['enclosure']
T = json.loads((ROOT / 'site/data/thermal-model.json').read_text())
H = T['headline']

# ----------------------------------------------------------------------------- placeholders
STUDENT = 'Safal Gupta'
REGNO = '[Register Number]'
GUIDE = '[Guide Name]'
GUIDE_DESIG = '[Designation], School of Computer Science and Engineering'
COURSE = '[Course Code – Course Title]'
HOD = '[Head of Department]'
MONTH = 'October 2026'
TITLE = 'SAAYA: AN IoT-ENABLED COOL SHELTER FOR OUTDOOR WORKERS'
TITLE_CASE = 'SAAYA: An IoT-Enabled Cool Shelter for Outdoor Workers'

# ----------------------------------------------------------------------------- helpers
toc, figs, tabs = [], [], []
chap_no = 0
sec_no = 0
fig_no = 0
tab_no = 0


def mk(key):
    return f'<span class="mk">QQ{key}QQ</span>'


def chapter(title):
    global chap_no, sec_no, fig_no, tab_no
    chap_no += 1; sec_no = 0; fig_no = 0; tab_no = 0
    key = f'C{chap_no}'
    toc.append((key, 0, f'{chap_no}', title))
    return f'<section class="chapter">{mk(key)}<div class="chap-no">CHAPTER {chap_no}</div><h1>{e(title.upper())}</h1>'


def section(title):
    global sec_no
    sec_no += 1
    key = f'S{chap_no}_{sec_no}'
    toc.append((key, 1, f'{chap_no}.{sec_no}', title))
    return f'<h2>{mk(key)}{chap_no}.{sec_no}&nbsp;&nbsp;{e(title)}</h2>'


def sub(title):
    return f'<h3>{e(title)}</h3>'


def para(*ps):
    return ''.join(f'<p>{p}</p>' for p in ps)


def figure(src, caption, width='100%', cls=''):
    global fig_no
    fig_no += 1
    label = f'{chap_no}.{fig_no}'
    key = f'F{label}'
    figs.append((key, label, caption))
    return (f'<figure class="{cls}">{mk(key)}<img src="{(IMG / src).as_uri()}" style="width:{width}" alt="{e(caption)}">'
            f'<figcaption><b>Fig. {label}:</b> {e(caption)}</figcaption></figure>')


def rotated_figure(src, caption):
    global fig_no
    fig_no += 1
    label = f'{chap_no}.{fig_no}'
    key = f'F{label}'
    figs.append((key, label, caption))
    return (f'<figure class="rot">{mk(key)}<img src="{(IMG / src).as_uri()}" alt="{e(caption)}">'
            f'<figcaption><b>Fig. {label}:</b> {e(caption)}</figcaption></figure>')


def table(caption, headers, rows, widths=None, cls=''):
    global tab_no
    tab_no += 1
    label = f'{chap_no}.{tab_no}'
    key = f'T{label}'
    tabs.append((key, label, caption))
    cg = ''.join(f'<col style="width:{w}">' for w in widths) if widths else ''
    head = ''.join(f'<th>{h}</th>' for h in headers)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return (f'<div class="tbl {cls}">{mk(key)}<div class="tcap"><b>Table {label}:</b> {e(caption)}</div>'
            f'<table><colgroup>{cg}</colgroup><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')


def ref(*keys):
    return '[' + ', '.join(f'@@{k}@@' for k in keys) + ']'


def number_refs(body):
    order = []
    for k in re.findall(r'@@([a-z0-9]+)@@', body):
        if k not in order:
            order.append(k)
    order += [k for k in KEYS if k not in order]
    num = {k: i + 1 for i, k in enumerate(order)}
    body = re.sub(r'@@([a-z0-9]+)@@', lambda m: str(num[m.group(1)]), body)
    return body, [REFS[KEYS.index(k)] for k in order]


# ----------------------------------------------------------------------------- references (IEEE)
REFS = [
    'International Labour Organization, <i>Working on a Warmer Planet: The Impact of Heat Stress on Labour Productivity and Decent Work</i>. Geneva: ILO, 2019.',
    'M. Romanello <i>et al.</i>, “The 2025 report of the Lancet Countdown on health and climate change,” <i>The Lancet</i>, 2025.',
    'National Disaster Management Authority, Government of India, <i>Guidelines for Cooling Centers</i> (draft), New Delhi, May 2025.',
    'N. M. Ravanelli, S. G. Hodder, G. Havenith and O. Jay, “Heart rate and body temperature responses to extreme heat and humidity with and without electric fans,” <i>JAMA</i>, vol. 313, no. 7, pp. 724–725, 2015.',
    'D. Gagnon, S. A. Romero, M. N. Cramer, O. Jay and C. G. Crandall, “Age modulates physiological responses during fan use under extreme heat and humidity,” <i>JAMA</i>, vol. 316, no. 9, pp. 989–991, 2016.',
    'N. B. Morris, T. English, L. Hospers, A. Capon and O. Jay, “The effects of electric fan use under differing resting heat index conditions: a clinical trial,” <i>Annals of Internal Medicine</i>, 2019.',
    'N. B. Morris <i>et al.</i>, “Electric fan use for cooling during hot weather: a biophysical modelling study,” <i>The Lancet Planetary Health</i>, vol. 5, no. 6, 2021.',
    'World Health Organization, “Climate change, heat and health,” fact sheet. [Online]. Available: https://www.who.int/news-room/fact-sheets/detail/climate-change-heat-and-health',
    'A. Middel and E. S. Krayenhoff, “Micrometeorological determinants of pedestrian thermal exposure during record-breaking heat in Tempe, Arizona,” <i>Science of the Total Environment</i>, vol. 687, pp. 137–151, 2019.',
    'Mahila Housing Trust, <i>Combating Climate Change Induced Heat Stress in Ahmedabad: Cool Roof Interventions</i>, Ahmedabad, 2017–2022.',
    'E. Teitelbaum <i>et al.</i>, “Addressing a systematic error correcting for free and mixed convection when measuring mean radiant temperature with globe thermometers,” <i>Scientific Reports</i>, vol. 12, art. 6473, 2022.',
    'W. C. Swinbank, “Long-wave radiation from clear skies,” <i>Quarterly Journal of the Royal Meteorological Society</i>, vol. 89, pp. 339–348, 1963.',
    'J. H. Watmuff, W. W. S. Charters and D. Proctor, “Solar and wind induced external coefficients for solar collectors,” <i>COMPLES</i>, no. 2, p. 56, 1977.',
    'Espressif Systems, <i>ESP32-WROOM-32E &amp; ESP32-WROOM-32UE Datasheet</i>, v2.1. [Online]. Available: https://documentation.espressif.com/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf',
    'Espressif Systems, <i>ESP32 Series Datasheet</i>, v5.3, and <i>ESP32-DevKitC V4 User Guide</i>. [Online]. Available: https://docs.espressif.com',
    'Sensirion AG, <i>Datasheet SHT3x-DIS: Humidity and Temperature Sensor</i>, v7, Dec. 2022.',
    'Analog Devices (Maxim Integrated), <i>DS18B20 Programmable Resolution 1-Wire Digital Thermometer</i>, datasheet.',
    'Texas Instruments, <i>INA219 Zerø-Drift, Bidirectional Current/Power Monitor With I²C Interface</i>, datasheet SBOS448.',
    'Solomon Systech, <i>SSD1306 128 × 64 Dot Matrix OLED/PLED Segment/Common Driver with Controller</i>, Rev 1.1.',
    'onsemi, <i>2N3904 General Purpose Transistor, NPN Silicon</i>, datasheet.',
    'Monolithic Power Systems, <i>MP1584 3 A, 1.5 MHz, 28 V Step-Down Converter</i>, datasheet r1.1.',
    'Intel Corporation, <i>4-Wire Pulse Width Modulation (PWM) Controlled Fans Specification</i>, Rev. 1.2, Jul. 2004.',
    'Noctua, <i>PWM Specifications White Paper</i>. [Online]. Available: https://noctua.at',
    'Wokwi, “ESP32 simulation” and “Diagram format” documentation. [Online]. Available: https://docs.wokwi.com',
    'India Meteorological Department, climatological normals for Vellore (station 43303), 1991–2020, as tabulated in “Vellore,” Wikipedia.',
]
KEYS = [k for k in ('ilo', 'lancet', 'ndma', 'ravanelli', 'gagnon', 'morris19', 'morris21', 'who', 'middel', 'mht', 'teitelbaum', 'swinbank', 'watmuff', 'esp32e', 'esp32', 'sht3x', 'ds18b20', 'ina219', 'ssd1306', '2n3904', 'mp1584', 'intel', 'noctua', 'wokwi', 'imd')]
R = {k: k for k in KEYS}   # resolved to numbers in order of first citation

# ----------------------------------------------------------------------------- body
import sys
sys.path.insert(0, str(ROOT / 'scripts'))
import report_body
_costs = json.loads((ROOT / 'research/costs.json').read_text())
g['FULL'] = [(x['item'], x['estimate_low'], x['estimate_high']) for x in _costs['full_size']]
b = report_body.build(chapter, section, sub, para, figure, rotated_figure, table, ref, R, g, P, E, H, T, e)
b.append('@@REFLIST@@')
toc.append(('REF', 0, '', 'References'))

# Appendix
chap_no = 'A'; sec_no = 0; fig_no = 0; tab_no = 0
toc.append(('APPA', 0, '', 'Appendix A: Bill of Materials'))
bom_rows = [(e(a), e(m), str(q), f'₹{u:,}', f'₹{q * u:,}', e(s)) for a, m, q, u, s, _ in g['BOM']]
bom_rows.append(('<b>Total</b>', f'listed prices ₹{g["listed"]:,}; estimates ₹{g["total"] - g["listed"]:,}', '', '', f'<b>₹{g["total"]:,}</b>', 'excluding shipping and labour'))
b.append('<section class="chapter">' + mk('APPA') + '<h1 class="unnum">APPENDIX A<br>BILL OF MATERIALS</h1>'
         + para('Prices were read from Indian supplier websites on 20 October 2026 and include GST where it was shown. Items marked “allowance” are estimates.')
         + table('Bill of materials and cost', ['Function', 'Part', 'Qty', 'Unit', 'Amount', 'Status'], bom_rows, ['18%', '36%', '6%', '10%', '11%', '19%'], 'small')
         + para('Supplier pages: ' + '; '.join(f'{e(v)}' for v in g['SRC'].values()) + '.').replace('<p>', '<p class="srcs">')
         + '</section>')
toc.append(('APPB', 0, '', 'Appendix B: Shelter Cost Estimate'))
chap_no = 'B'; tab_no = 0
fl = sum(x[1] for x in g['FULL']); fh_ = sum(x[2] for x in g['FULL'])
b.append('<section class="chapter">' + mk('APPB') + '<h1 class="unnum">APPENDIX B<br>SHELTER COST ESTIMATE</h1>'
         + para('The figures below are planning allowances worked out from the quantities in the 3D model (about 161 kg of structural steel at an assumed ₹80 to ₹140 per kg) and typical local rates. They are not supplier quotations and must be replaced by a dated fabrication quote before any decision is made.')
         + table('First-article cost estimate of the cool shelter (₹)', ['Item', 'Low', 'High'], [(e(i), f'₹{lo:,}', f'₹{hi:,}') for i, lo, hi in g['FULL']] + [('<b>Total</b>', f'<b>₹{fl:,}</b>', f'<b>₹{fh_:,}</b>')], ['60%', '20%', '20%'], 'small')
         + para('The electronics line in this table is a broad allowance; the detailed electronics bill in Appendix A comes to about ₹' + f"{g['total']:,}" + '. For comparison, a 1.5-ton inverter split air conditioner lists at about ₹36,990 for the equipment alone, but an air conditioner cannot cool an open shelter, so the two are not equivalent.')
         + '</section>')

BODY, ORDERED_REFS = number_refs(''.join(b))
BODY = BODY.replace('@@REFLIST@@', '<section class="chapter">' + mk('REF') + '<h1 class="unnum">REFERENCES</h1><ol class="refs">' + ''.join(f'<li><span class="rn">[{i}]</span>{r}</li>' for i, r in enumerate(ORDERED_REFS, 1)) + '</ol></section>')

CSS = """
@page{size:A4;margin:25.4mm 25.4mm 27mm 38.1mm}
*{box-sizing:border-box}
html{font-family:'Times New Roman','Liberation Serif','Tinos',serif;font-size:12pt;color:#000}
body{margin:0;line-height:1.5;text-align:justify;hyphens:auto}
p{margin:0 0 8pt;text-indent:0}
.chapter{break-before:page}
.chap-no{text-align:center;font-weight:bold;font-size:16pt;margin-top:4mm}
h1{text-align:center;font-size:16pt;margin:2mm 0 10mm;line-height:1.3}
h1.unnum{margin-top:4mm}
h2{font-size:14pt;margin:12pt 0 6pt;break-after:avoid;text-align:left}
h3{font-size:12pt;margin:8pt 0 4pt;break-after:avoid}
ul,ol{margin:0 0 8pt;padding-left:9mm}
li{margin:0 0 3pt}
figure{margin:8pt 0 10pt;text-align:center;break-inside:avoid}
figure img{display:block;margin:0 auto}
figcaption{font-size:11pt;margin-top:4pt;text-align:center}
figure.rot{break-before:page;break-after:page;height:228mm;display:flex;flex-direction:column;justify-content:center;margin:0}
figure.rot img{max-height:212mm;max-width:100%;width:auto}
.pair{display:flex;gap:6mm;align-items:flex-end}.pair figure.half{flex:1}
.tbl{margin:8pt 0 10pt;break-inside:auto}
.tcap{text-align:center;font-size:11pt;margin-bottom:4pt;break-after:avoid}
table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:10pt;line-height:1.3;text-align:left}
th,td{border:.6pt solid #000;padding:2.5pt 4pt;vertical-align:top;word-wrap:break-word}
th{background:#e6e6e6;font-weight:bold}
thead{display:table-header-group}
tr{break-inside:avoid}
.small table{font-size:9.5pt}
.refs{list-style:none;padding-left:11mm;font-size:11pt;text-align:left}.refs li{margin-bottom:5pt;position:relative}.refs .rn{position:absolute;left:-11mm}
.srcs{font-size:9pt;text-align:left;word-break:break-all;line-height:1.35}
.mk{font-size:1pt;color:#fff;line-height:0}
"""


def front(pages_toc, pages_fig, pages_tab):
    def leader(label, title, page, lvl):
        ind = 'padding-left:9mm' if lvl else ''
        wt = 'font-weight:bold' if lvl == 0 else ''
        lab = f'{label}&nbsp;&nbsp;' if label else ''
        return f'<div class="tl" style="{ind};{wt}"><span>{lab}{e(title)}</span><span class="dots"></span><span>{page}</span></div>'
    toc_html = ''.join(leader(lbl if lvl else (f'{lbl}' if lbl else ''), t if lvl else (t.upper() if lbl else t.upper()), pages_toc.get(k, ''), lvl)
                       for k, lvl, lbl, t in toc)
    fig_html = ''.join(leader(f'Fig. {lbl}', cap, pages_fig.get(k, ''), 1).replace('padding-left:9mm', '') for k, lbl, cap in figs)
    tab_html = ''.join(leader(f'Table {lbl}', cap, pages_tab.get(k, ''), 1).replace('padding-left:9mm', '') for k, lbl, cap in tabs)
    abbr = [('ABS', 'Acrylonitrile butadiene styrene'), ('ACK', 'Acknowledge'), ('API', 'Application programming interface'), ('CAD', 'Computer-aided design'),
            ('CFM', 'Cubic feet per minute'), ('GPIO', 'General-purpose input/output'), ('I²C', 'Inter-Integrated Circuit bus'), ('IMD', 'India Meteorological Department'),
            ('IoT', 'Internet of Things'), ('IP65', 'Ingress protection: dust-tight, protected against water jets'), ('LDO', 'Low-dropout regulator'), ('MRT', 'Mean radiant temperature'), ('RHS / SHS', 'Rectangular / square hollow section (steel tube)'),
            ('NDMA', 'National Disaster Management Authority'), ('OLED', 'Organic light-emitting diode'), ('PWM', 'Pulse-width modulation'), ('RH', 'Relative humidity'),
            ('STEP', 'Standard for the Exchange of Product model data'), ('STP', 'Shielded twisted pair'), ('WHO', 'World Health Organization')]
    abbr_html = '<table class="abbr"><tbody>' + ''.join(f'<tr><td><b>{e(a)}</b></td><td>{e(bb)}</td></tr>' for a, bb in abbr) + '</tbody></table>'
    abstract = (
        f'Workers on Indian construction sites and farms take their rest breaks under whatever shade is available, usually a bare metal sheet that becomes hot in the afternoon sun. Nobody measures whether these shades help, fans fitted to them fail without anyone noticing, and a worker who feels unwell has no reliable way to call for help. This project presents the SAAYA cool shelter, a demountable rest shelter for four to six workers. Its 2.4 m × 2.0 m steel frame carries a reflective upper roof skin, a ventilated gap of about 120 mm and a painted lower lining, with a 200 mm overhang, a louvred side screen and a bench. An IoT system called SAAYA Node, built around an ESP32 microcontroller, reads two Sensirion SHT30 temperature and humidity sensors (at seat height and outside the shelter as a reference), a DS18B20 probe on the roof lining, a float switch in the water can, the tachometer of a 120 mm PWM fan and an INA219 power monitor. Workers use three weatherproof buttons and an OLED display; a help request is latched in flash memory and can be cleared only by staff. Guided by medical studies showing that fans can add heat in very hot air, the controller stops automatic fan operation at 39 °C while leaving manual control to the worker. A screening heat model predicts that the cool roof keeps its lining about 26 °C cooler than a weathered metal sheet, and showed that shade, overhang and the ground around the shelter matter more than any single roof detail. The report documents the selection of materials and components, technical specifications, the interfacing circuit, dimensioned CadQuery 3D models of the shelter and the {E["W"]} × {E["H"]} × {E["D"]} mm IP65 electronics enclosure, and a deployment plan for a worksite in Vellore. The electronics cost about ₹{g["total"]:,}. The firmware compiles and its control logic passes automated tests; fabrication and field testing are the next stage.')
    return f"""
<section class="fm title">
<div class="t1">{e(TITLE)}</div>
<div class="t2">A PROJECT REPORT</div>
<div class="t3"><i>Submitted in partial fulfilment of the requirements for the course</i><br>{e(COURSE)}</div>
<div class="t3"><i>by</i></div>
<div class="t4">{e(STUDENT.upper())}<br>{e(REGNO)}</div>
<div class="t3"><i>Under the guidance of</i><br><b>{e(GUIDE)}</b><br>{e(GUIDE_DESIG)}</div>
<div class="t5">SCHOOL OF COMPUTER SCIENCE AND ENGINEERING<br>VELLORE INSTITUTE OF TECHNOLOGY<br>VELLORE – 632 014, TAMIL NADU, INDIA</div>
<div class="t6">{MONTH.upper()}</div>
</section>
<section class="fm"><h1>DECLARATION</h1>
<p>I hereby declare that the project report entitled “{e(TITLE_CASE)}”, submitted by me to the School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, in partial fulfilment of the requirements for the course {e(COURSE)}, is a record of original work carried out by me under the guidance of {e(GUIDE)}. I further declare that the work reported in this project has not been submitted, either in part or in full, for the award of any other degree or diploma in this institute or any other institute or university.</p>
<div class="sig"><div>Place: Vellore<br>Date:</div><div>Signature of the Candidate<br><b>{e(STUDENT)}</b><br>{e(REGNO)}</div></div>
</section>
<section class="fm"><h1>CERTIFICATE</h1>
<p>This is to certify that the project report entitled “{e(TITLE_CASE)}”, submitted by <b>{e(STUDENT)} ({e(REGNO)})</b>, School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, for the course {e(COURSE)}, is a record of bona fide work carried out by the student under my supervision during the period July 2026 to October 2026. The contents of this report have not been submitted elsewhere for the award of any degree or diploma, and the report meets the requirements of the course.</p>
<div class="sig"><div>Signature of the Guide<br><b>{e(GUIDE)}</b><br>{e(GUIDE_DESIG)}</div><div>Signature of the Head of Department<br><b>{e(HOD)}</b><br>School of Computer Science and Engineering</div></div>
<div class="sig" style="margin-top:22mm"><div>Internal Examiner</div><div>External Examiner</div></div>
</section>
<section class="fm"><h1>ACKNOWLEDGEMENT</h1>
<p>I am grateful to my guide, {e(GUIDE)}, for the time and patient advice given throughout this project, and especially for the questions that pushed me to check each claim against a measurement or a source.</p>
<p>I thank the Head of the Department and the faculty of the School of Computer Science and Engineering, Vellore Institute of Technology, for the facilities and the encouragement to work on a problem outside the usual software projects. I also thank the management of VIT for providing an environment in which an idea like this can be tried.</p>
<p>The design depends on published research and on openly available datasheets and tools. I acknowledge the authors of the heat and fan-use studies cited in this report, and the developers of CadQuery, PlatformIO, the ESP32 Arduino core and the Wokwi simulator.</p>
<p>Finally, I thank my family and friends for their support, and the workers whose working conditions in the Vellore summer were the reason for starting this project.</p>
<div class="sig" style="justify-content:flex-end"><div><b>{e(STUDENT)}</b></div></div>
</section>
<section class="fm"><h1>ABSTRACT</h1><p>{abstract}</p>
<p><b>Keywords:</b> cool shelter, Internet of Things, ESP32, heat stress, outdoor workers, cool roof, PWM fan control, Vellore.</p></section>
<section class="fm"><h1>TABLE OF CONTENTS</h1>
<div class="tl" style="font-weight:bold"><span>Title</span><span class="dots" style="border:0"></span><span>Page No.</span></div>
<div class="tl"><span>Declaration</span><span class="dots"></span><span>ii</span></div>
<div class="tl"><span>Certificate</span><span class="dots"></span><span>iii</span></div>
<div class="tl"><span>Acknowledgement</span><span class="dots"></span><span>iv</span></div>
<div class="tl"><span>Abstract</span><span class="dots"></span><span>v</span></div>
<div class="tl"><span>List of Figures</span><span class="dots"></span><span>{{LOF}}</span></div>
<div class="tl"><span>List of Tables</span><span class="dots"></span><span>{{LOT}}</span></div>
<div class="tl"><span>List of Abbreviations</span><span class="dots"></span><span>{{LOA}}</span></div>
{toc_html}</section>
<section class="fm">{mk('LOF')}<h1>LIST OF FIGURES</h1>{fig_html}</section>
<section class="fm">{mk('LOT')}<h1>LIST OF TABLES</h1>{tab_html}</section>
<section class="fm">{mk('LOA')}<h1>LIST OF ABBREVIATIONS</h1>{abbr_html}</section>
"""


FCSS = CSS + """
.fm{break-before:page}.fm:first-child{break-before:auto}
.title{text-align:center;display:flex;flex-direction:column;justify-content:space-between;height:240mm;padding:6mm 0}
.t1{font-size:17pt;font-weight:bold;line-height:1.35}
.t2{font-size:14pt;font-weight:bold;letter-spacing:.06em}
.t3{font-size:12pt;line-height:1.5}
.t4{font-size:14pt;font-weight:bold;line-height:1.5}
.t5{font-size:13pt;font-weight:bold;line-height:1.6}
.t6{font-size:13pt;font-weight:bold}
.sig{display:flex;justify-content:space-between;margin-top:30mm;text-align:left;line-height:1.5}
.sig>div:last-child{text-align:right}
.tl{display:flex;align-items:baseline;gap:2mm;line-height:1.6;text-align:left}
.tl .dots{flex:1;border-bottom:1pt dotted #000;transform:translateY(-3pt)}
.abbr{font-size:11pt}.abbr td{border:0;padding:2pt 4pt}.abbr td:first-child{width:22%}
"""


def page_doc(css, body, title):
    return f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{e(title)}</title><style>{css}</style></head><body>{body}</body></html>"


def print_pdf(html_path, pdf_path):
    subprocess.run(['node', str(ROOT / 'scripts' / 'print_report.cjs'), str(html_path), str(pdf_path)], check=True)


def find_markers(pdf_path):
    from pypdf import PdfReader
    pages = {}
    for i, pg in enumerate(PdfReader(str(pdf_path)).pages):
        for m in re.findall(r'QQ([A-Za-z0-9_.]+?)QQ', re.sub(r'\s+', '', pg.extract_text() or '')):
            pages.setdefault(m, i)
    return pages


def roman(n):
    vals = [(10, 'x'), (9, 'ix'), (5, 'v'), (4, 'iv'), (1, 'i')]
    out = ''
    for v, s in vals:
        while n >= v:
            out += s; n -= v
    return out


def stamp(pdf_in, pdf_out, front_pages):
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    reader = PdfReader(str(pdf_in)); writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        label = None
        if i < front_pages:
            if i > 0:
                label = roman(i + 1)
        else:
            label = str(i - front_pages + 1)
        if label:
            buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=A4)
            c.setFont('Times-Roman', 11)
            # centre of the text block (left margin 38.1 mm, right 25.4 mm)
            x = (38.1 + (210 - 25.4)) / 2 * 72 / 25.4
            c.drawCentredString(x, 14 * 72 / 25.4, label); c.save(); buf.seek(0)
            page.merge_page(PdfReader(buf).pages[0])
        writer.add_page(page)
    writer.add_metadata({'/Title': 'SAAYA: An IoT-Enabled Cool Shelter for Outdoor Workers', '/Author': STUDENT, '/Subject': 'VIT project report'})
    with open(pdf_out, 'wb') as f:
        writer.write(f)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    body_html = OUT / 'body.html'; body_pdf = OUT / 'body.pdf'
    body_html.write_text(page_doc(CSS, BODY, 'SAAYA Node report body'))
    print_pdf(body_html, body_pdf)
    bp = find_markers(body_pdf)
    toc_pages = {k: bp[k] + 1 for k, *_ in toc if k in bp}
    fig_pages = {k: bp[k] + 1 for k, *_ in figs if k in bp}
    tab_pages = {k: bp[k] + 1 for k, *_ in tabs if k in bp}
    missing = [k for k, *_ in toc + figs + tabs if k not in bp]
    if missing:
        print('WARNING markers not found:', missing)
    fh = front(toc_pages, fig_pages, tab_pages)
    front_html = OUT / 'front.html'; front_pdf = OUT / 'front.pdf'
    # first pass of front matter to learn where LOF/LOT/LOA land, then fill them
    front_html.write_text(page_doc(FCSS, fh.replace('{LOF}', '').replace('{LOT}', '').replace('{LOA}', ''), 'front'))
    print_pdf(front_html, front_pdf)
    fp = find_markers(front_pdf)
    fh = fh.replace('{LOF}', roman(fp.get('LOF', 0) + 1)).replace('{LOT}', roman(fp.get('LOT', 0) + 1)).replace('{LOA}', roman(fp.get('LOA', 0) + 1))
    front_html.write_text(page_doc(FCSS, fh, 'front'))
    print_pdf(front_html, front_pdf)
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter()
    nf = len(PdfReader(str(front_pdf)).pages)
    for src in (front_pdf, body_pdf):
        for pg in PdfReader(str(src)).pages:
            w.add_page(pg)
    merged = OUT / 'merged.pdf'
    with open(merged, 'wb') as f:
        w.write(f)
    final = OUT / 'SAAYA_Cool_Shelter_Project_Report_VIT.pdf'
    stamp(merged, final, nf)
    for p in (merged, body_pdf, front_pdf):
        p.unlink()
    print(f'Report: {final} ({nf} front pages + {len(PdfReader(str(final)).pages) - nf} body pages)')
