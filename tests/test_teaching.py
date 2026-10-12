from pathlib import Path
import json,re,html
R=Path(__file__).parents[1]
def test_every_cad_part_has_placement_and_connection_explanation():
    guide=json.loads((R/'site/component-guide.json').read_text())
    assembly=json.loads((R/'site/fullsize/assembly.json').read_text())['instances']
    assert set(guide['parts'])=={i['part'] for i in assembly}
    for item in assembly:
        d={**guide['parts'][item['part']],**guide['instances'].get(item['name'],{})}
        for field in ('title','role','placement','connection','validation','limitation'):
            assert len(d[field])>8,(item['name'],field)
    assert set(guide['instances'])<={i['name'] for i in assembly}

def test_architecture_targets_real_instances_and_marks_hardware_gaps():
    page=html.unescape((R/'site/explain.html').read_text())
    ids={i['name'] for i in json.loads((R/'site/fullsize/assembly.json').read_text())['instances']}
    targets=re.findall(r'fullsize-model.html\?part=([A-Za-z0-9_]+)',page)
    assert len(targets)>=9 and set(targets)<=ids
    assert 'discrete parts not in CAD' in page
    assert 'USB serial' in page and 'not an implemented feature' in page
    assert '250 mA' in page and 'NOT full-size' in page
