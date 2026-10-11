import pytest
from api.analysis import analysis_payload,explain,AnalystUnavailable
from api.core import scenario,evaluate

def test_ai_disabled_without_model(monkeypatch):
    monkeypatch.delenv('SAAYA_AI_MODEL',raising=False)
    with pytest.raises(AnalystUnavailable):explain({'evidence':evaluate(scenario('normal',1))},[])

def test_prompt_carries_uncertainty_and_source():
    record={'id':'x','evidence':evaluate(scenario('normal',1))}
    payload=analysis_payload(record,[{'id':'R1','title':'Study','url':'https://example.org','limitations':'Not SAAYA'}],'local-model')
    assert payload['stream'] is False
    prompt=payload['messages'][1]['content'];assert 'SIMULATED' in prompt and 'Not established' in prompt
    assert 'cannot control' in payload['messages'][0]['content']
