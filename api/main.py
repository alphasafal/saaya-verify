import csv,io,json,os,secrets,sqlite3,time,uuid
from pathlib import Path
from typing import Literal
from fastapi import FastAPI,HTTPException,Header,Query
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from .core import Sample,scenario,evaluate
class ScenarioRequest(BaseModel):
    name:Literal['normal','humid','fan_failure','sensor_failure','low_water','no_power','reference_mismatch']
    seed:int=Field(default=1,ge=0,le=100000)
class StepRequest(BaseModel):
    run_id:str
    count:int=Field(default=1,ge=1,le=60)
class ExperimentRequest(BaseModel):
    run_id:str
    endpoint:Literal['roof_temp','air_speed']
def create_app(db_path=None,token=None):
    app=FastAPI(title='SAAYA VERIFY bench API',version='0.2.0')
    path=db_path or os.getenv('SAAYA_DB','saaya.db');token=token if token is not None else os.getenv('SAAYA_DEVICE_TOKEN')
    def db():
        conn=sqlite3.connect(path);conn.row_factory=sqlite3.Row;return conn
    with db() as con:con.executescript('CREATE TABLE IF NOT EXISTS samples(device TEXT,session TEXT,seq INTEGER,received REAL,payload TEXT,UNIQUE(device,session,seq)); CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,name TEXT,seed INTEGER,cursor INTEGER); CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY,run TEXT,endpoint TEXT,result TEXT);')
    def fetch_run(con,rid):
        row=con.execute('SELECT * FROM runs WHERE id=?',(rid,)).fetchone()
        if not row:raise HTTPException(404,'Run not found')
        return row
    def stored(con,rid):return [json.loads(x['payload']) for x in con.execute('SELECT payload FROM samples WHERE session=? ORDER BY seq',(rid,))]
    @app.get('/health')
    def health():return {'status':'ok','mode':'local-bench','measured_ingestion_enabled':bool(token)}
    @app.post('/telemetry')
    def ingest(s:Sample,x_device_token:str|None=Header(default=None)):
        if not token or not x_device_token or not secrets.compare_digest(token,x_device_token):raise HTTPException(401,'Configured device credential required')
        with db() as con:result=con.execute('INSERT OR IGNORE INTO samples VALUES(?,?,?,?,?)',(s.device_id,s.session_id,s.seq,time.time(),s.model_dump_json()))
        return {'inserted':result.rowcount==1}
    @app.get('/latest')
    def latest(source:Literal['SIMULATED','MEASURED']='MEASURED'):
        with db() as con:rows=con.execute('SELECT * FROM samples ORDER BY received DESC LIMIT 1000').fetchall()
        for row in rows:
            s=json.loads(row['payload'])
            if s['source']==source:
                age=max(0,time.time()-row['received'])+max(0,s['emitted_ms']-s['acquired_ms'])/1000
                return {'sample':s,'age_seconds':age,'stale':age>5}
        return {'sample':None,'age_seconds':None,'stale':True}
    @app.get('/history')
    def history(run_id:str|None=None,limit:int=Query(60,ge=1,le=1000)):
        with db() as con:
            if run_id:rows=con.execute('SELECT payload FROM samples WHERE session=? ORDER BY seq DESC LIMIT ?',(run_id,limit)).fetchall()
            else:rows=con.execute('SELECT payload FROM samples ORDER BY received DESC LIMIT ?',(limit,)).fetchall()
        return [json.loads(x['payload']) for x in reversed(rows)]
    @app.post('/sim/scenario')
    def start(req:ScenarioRequest):
        rid=str(uuid.uuid4())
        with db() as con:con.execute('INSERT INTO runs VALUES(?,?,?,0)',(rid,req.name,req.seed))
        return {'run_id':rid,'source':'SIMULATED','cursor':0}
    @app.post('/sim/step')
    def step(req:StepRequest):
        with db() as con:
            con.execute('BEGIN IMMEDIATE');run=fetch_run(con,req.run_id);end=min(60,run['cursor']+req.count);rows=scenario(run['name'],run['seed'])[run['cursor']:end]
            for s in rows:
                s['session_id']=req.run_id;con.execute('INSERT OR IGNORE INTO samples VALUES(?,?,?,?,?)',(s['device_id'],s['session_id'],s['seq'],time.time(),json.dumps(s)))
            con.execute('UPDATE runs SET cursor=? WHERE id=?',(end,req.run_id))
        return {'cursor':end,'samples':rows}
    @app.post('/experiments')
    def experiment(req:ExperimentRequest):
        eid=str(uuid.uuid4())
        with db() as con:
            con.execute('BEGIN IMMEDIATE');run=fetch_run(con,req.run_id)
            if run['cursor']:raise HTTPException(409,'Declare experiment before collecting samples')
            con.execute('INSERT INTO experiments VALUES(?,?,?,NULL)',(eid,req.run_id,req.endpoint))
        return {'id':eid,'run_id':req.run_id,'endpoint':req.endpoint,'expected_samples':60,'cadence_seconds':1,'minimum_samples':48}
    def get_exp(con,eid):
        row=con.execute('SELECT * FROM experiments WHERE id=?',(eid,)).fetchone()
        if not row:raise HTTPException(404,'Experiment not found')
        return row
    @app.post('/experiments/{eid}/finish')
    def finish(eid:str):
        with db() as con:
            con.execute('BEGIN IMMEDIATE');e=get_exp(con,eid)
            if e['result']:return json.loads(e['result'])
            samples=stored(con,e['run']);result={'id':eid,'run_id':e['run'],'endpoint':e['endpoint'],'evidence':evaluate(samples,e['endpoint']),'samples':samples,'finished_at':time.time(),'configuration':{'expected_samples':60,'cadence_seconds':1,'minimum_samples':48,'settling_seconds':0,'settling_note':'Demonstration only; physical protocol requires settling and an independent reference'}}
            con.execute('UPDATE experiments SET result=? WHERE id=?',(json.dumps(result),eid))
        return result
    @app.get('/experiments/{eid}')
    def get(eid:str):
        with db() as con:e=get_exp(con,eid)
        return json.loads(e['result']) if e['result'] else {'id':eid,'status':'collecting','run_id':e['run']}
    @app.get('/experiments/{eid}/export')
    def export(eid:str,format:Literal['json','csv']='json'):
        data=get(eid)
        if data.get('status')=='collecting':raise HTTPException(409,'Finish experiment first')
        if format=='json':return data
        out=io.StringIO();writer=csv.DictWriter(out,fieldnames=list(Sample.model_fields));writer.writeheader();writer.writerows(data['samples'])
        return Response(out.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="saaya-{eid}.csv"'})
    @app.get('/analysis/status')
    def analysis_status():return {'ai_enabled':False,'reason':'No external model configured. Evidence exports support read-only analysis. No autonomous control.'}
    site=Path(__file__).resolve().parents[1]/'site'
    if site.exists():app.mount('/',StaticFiles(directory=site,html=True),name='site')
    return app
app=create_app()
