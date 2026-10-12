"""Transparent screening, not a site-specific structural design or certification."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;O=R/'exports'
area=2.8*2.4;rho=1.225;cp=1.5;span=2.4;E=200e9
b=.06;h=.08;t=.003;I=(b*h**3-(b-2*t)*(h-2*t)**3)/12
cases=[]
for speed in [30,40,50]:
 q=.5*rho*speed**2;up=q*cp*area;line=up/2/span;moment=line*span**2/8;stress=moment*(h/2)/I/1e6;deflection=5*line*span**4/(384*E*I)*1000
 cases.append(dict(assumed_speed_m_s=speed,dynamic_pressure_Pa=q,assumed_net_coefficient=cp,gross_roof_uplift_N=round(up),crossbeam_stress_MPa=round(stress,1),crossbeam_deflection_mm=round(deflection,1),screening_span_240_limit_mm=10,screening_deflection_exceeded=deflection>10))
data=dict(status='SCREENING ONLY / NOT CODE CHECKED',model='Two simply supported 2.4 m RHS 80x60x3 crossbeams, each carrying half of uniform roof uplift; elastic small-deflection beam equations',assumptions={'air_density_kg_m3':rho,'steel_E_Pa':E,'roof_projected_area_m2':area,'section_I_m4':I},cases=cases,excluded=['Site basic wind speed, terrain/topography/risk factors and load combinations','Local roof edge suction, cladding spans, roof connections and purlin stability','Lateral loading, torsion, frame joint stiffness, fatigue, corrosion and seismic effects','Anchor tension/shear interaction, embedment, concrete breakout, soil bearing and overturning','Occupant impact and bench strength/creep'],decision='No construction release. Qualified local structural engineer must determine governing loads, connections and foundations. A low screening stress is not approval.')
(O/'feasibility.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))
