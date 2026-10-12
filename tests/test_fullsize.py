from pathlib import Path
import json,zipfile
R=Path(__file__).parents[1];O=R/'cad/fullsize/exports'
def test_fullsize_solid_review_export_integrity():
    report=json.loads((O/'validation.json').read_text());bom=json.loads((O/'bom.json').read_text());assembly=json.loads((O/'assembly.json').read_text())
    assert report['all_solids_valid'] and report['construction_release'] is False
    assert len(bom)==report['parts'] and len(assembly['instances'])==report['instances']
    assert sum(r['quantity'] for r in bom)==len(assembly['instances'])
    for r in bom:
        assert (O/(r['part']+'.step')).read_text().startswith('ISO-10303-21;')
        assert (O/(r['part']+'.stl')).stat().st_size>100
    clash=json.loads((O/'interference.json').read_text());assert clash['invalid_reimported_parts']==[] and clash['intersections']==[]

def test_fullsize_cost_and_package_are_not_false_approval():
    cost=json.loads((O/'cost-screening.json').read_text())
    assert cost['total_low']==sum(r['estimate_low'] for r in cost['items'])
    assert 'NOT DEMONSTRATED' in cost['cost_target']
    with zipfile.ZipFile(R/'site/fullsize/review-package.zip') as z:
        assert 'cad/exports/SAAYA_FS01_assembly.step' in z.namelist()
        assert 'review/REVIEW.md' in z.namelist()

def test_every_seat_slat_has_transverse_support():
    a=json.loads((O/'assembly.json').read_text())['instances']
    supports=[i for i in a if i['part']=='ST04_bench_crossrail']
    seats=[i for i in a if i['part']=='ST03_seat_slat']
    assert len(supports)==3 and len(seats)==6
    for seat in seats:
        x,y,z=seat['position']
        for rail in supports:
            rx,ry,rz=rail['position']
            assert rail['rotation_z']==90 and rz+40==z
            assert x<rx-20<x+1400 and ry<=y and y+70<=ry+450
