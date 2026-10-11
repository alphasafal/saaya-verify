from pathlib import Path
import json
import trimesh

def test_printable_parts_are_closed_and_positive():
    p=Path('cad/exports');files=list(p.glob('*.stl'))
    assert len(files)>=10
    for f in files:
        m=trimesh.load(f,force='mesh')
        assert m.is_watertight,f.name
        assert m.volume>0,f.name
        assert all(m.extents<=221),f.name

def test_box_dimensions():
    m=trimesh.load('cad/exports/enclosure_base.stl',force='mesh')
    assert tuple(round(x,1) for x in m.extents)==(120,90,42.5)
