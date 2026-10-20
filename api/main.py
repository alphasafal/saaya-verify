import csv,io,json,os,secrets,sqlite3,time,uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Literal
from fastapi import FastAPI,HTTPException,Header,Query
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from .core import Sample,scenario,evaluate,aggregate,declaration_for
from . import thermal
class ScenarioRequest(BaseModel):
    name:Literal['normal','humid','fan_failure','sensor_failure','low_water','no_power','reference_mismatch']
    seed:int=Field(default=1,ge=0,le=100000)
class StepRequest(BaseModel):
    run_id:str
    count:int=Field(default=1,ge=1,le=60)
class ExperimentRequest(BaseModel):
    run_id:str
    endpoint:Literal['roof_temp','air_speed']
    # Optional smallest meaningful difference, locked before any sample is collected.
    margin:float|None=Field(default=None,gt=0,le=100)
class AggregateRequest(BaseModel):
    experiment_ids:list[str]=Field(min_length=1,max_length=200)
def create_app(db_path=None,token=None):
    app=FastAPI(title='SAAYA VERIFY bench API',version='0.3.0')
    path=db_path or os.getenv('SAAYA_DB','saaya.db');token=token if token is not None else os.getenv('SAAYA_DEVICE_TOKEN')
    @contextmanager
    def db():
        # One connection per request; commit on success, roll back on error, ALWAYS close.
        # (sqlite3's own context manager commits but never closes -> leaked file handles.)
        conn=sqlite3.connect(path,timeout=5);conn.row_factory=sqlite3.Row
        try:
            yield conn;conn.commit()
        except BaseException:
            conn.rollback();raise
        finally:conn.close()
    with db() as con:
        con.execute('PRAGMA journal_mode=WAL')  # bridge writes while the dashboard reads
        con.executescript('CREATE TABLE IF NOT EXISTS samples(device TEXT,session TEXT,seq INTEGER,received REAL,payload TEXT,UNIQUE(device,session,seq)); CREATE TABLE IF NOT EXISTS clocks(device TEXT,session TEXT,origin REAL,PRIMARY KEY(device,session)); CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,name TEXT,seed INTEGER,cursor INTEGER); CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY,run TEXT,endpoint TEXT,result TEXT); CREATE INDEX IF NOT EXISTS samples_session ON samples(session,seq); CREATE INDEX IF NOT EXISTS samples_received ON samples(received);')
        if 'declaration' not in [c['name'] for c in con.execute('PRAGMA table_info(experiments)')]:
            con.execute('ALTER TABLE experiments ADD COLUMN declaration TEXT')  # migrate v0.2 databases
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
        now=time.time()
        if s.source!='MEASURED':raise HTTPException(422,'Device ingestion accepts MEASURED records only; simulation is generated server-side')
        if s.emitted_ms<s.acquired_ms:raise HTTPException(422,'Emission precedes acquisition')
        with db() as con:
            result=con.execute('INSERT OR IGNORE INTO samples VALUES(?,?,?,?,?)',(s.device_id,s.session_id,s.seq,now,s.model_dump_json()))
            if result.rowcount:
                con.execute('INSERT INTO clocks VALUES(?,?,?) ON CONFLICT(device,session) DO UPDATE SET origin=MIN(origin,excluded.origin)',(s.device_id,s.session_id,now-s.emitted_ms/1000))
        return {'inserted':result.rowcount==1}
    @app.get('/latest')
    def latest(source:Literal['SIMULATED','MEASURED']='MEASURED'):
        with db() as con:rows=con.execute("SELECT samples.*,clocks.origin FROM samples LEFT JOIN clocks ON samples.device=clocks.device AND samples.session=clocks.session WHERE json_extract(payload,'$.source')=? ORDER BY received DESC,seq DESC LIMIT 1",(source,)).fetchall()
        for row in rows:
            s=json.loads(row['payload'])
            if s['source']==source:
                age=max(0,time.time()-row['received'])+max(0,s['emitted_ms']-s['acquired_ms'])/1000
                if row['origin'] is not None:age=max(age,time.time()-(row['origin']+s['acquired_ms']/1000))
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
            declaration=declaration_for(req.endpoint,req.margin);declaration['declared_at']=time.time()
            con.execute('INSERT INTO experiments(id,run,endpoint,result,declaration) VALUES(?,?,?,NULL,?)',(eid,req.run_id,req.endpoint,json.dumps(declaration)))
        return {'id':eid,'run_id':req.run_id,'endpoint':req.endpoint,'declaration':declaration,'expected_samples':60,'cadence_seconds':1,'minimum_samples':48}
    def get_exp(con,eid):
        row=con.execute('SELECT * FROM experiments WHERE id=?',(eid,)).fetchone()
        if not row:raise HTTPException(404,'Experiment not found')
        return row
    @app.post('/experiments/{eid}/finish')
    def finish(eid:str):
        with db() as con:
            con.execute('BEGIN IMMEDIATE');e=get_exp(con,eid)
            if e['result']:return json.loads(e['result'])
            samples=stored(con,e['run']);declaration=json.loads(e['declaration']) if e['declaration'] else declaration_for(e['endpoint'])
            result={'id':eid,'run_id':e['run'],'endpoint':e['endpoint'],'evidence':evaluate(samples,e['endpoint'],declaration,day=f"synthetic-day-{fetch_run(con,e['run'])['seed']}"),'samples':samples,'finished_at':time.time(),'configuration':{'expected_samples':60,'cadence_seconds':1,'minimum_samples':48,'settling_seconds':0,'settling_note':'Demonstration only; physical protocol requires settling and an independent reference'}}
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
    @app.post('/evidence/aggregate')
    def combine(req:AggregateRequest):
        if len(set(req.experiment_ids))!=len(req.experiment_ids):raise HTTPException(422,'Duplicate experiment ids')
        results=[]
        for eid in req.experiment_ids:
            data=get(eid)
            if data.get('status')=='collecting':raise HTTPException(409,f'Experiment {eid} is not finished')
            results.append(data['evidence'])
        try:return aggregate(results)
        except ValueError as e:raise HTTPException(422,str(e))
    @app.get('/model/thermal')
    def thermal_model():return thermal.report()
    @app.get('/analysis/status')
    def analysis_status():return {'ai_enabled':bool(os.getenv('SAAYA_AI_MODEL')),'reason':'Optional local model; no autonomous control. Availability requires a running local server.'}
    @app.post('/experiments/{eid}/explain')
    def analyst(eid:str):
        from .analysis import explain,AnalystUnavailable
        record=get(eid)
        if record.get('status')=='collecting':raise HTTPException(409,'Finish experiment before analysis')
        source_path=Path(__file__).resolve().parents[1]/'research/evidence.json'
        sources=json.loads(source_path.read_text()) if source_path.exists() else []
        try:return explain({'id':record['id'],'evidence':record['evidence']},sources)
        except AnalystUnavailable as e:raise HTTPException(503,str(e))
    site=Path(__file__).resolve().parents[1]/'site'
    if site.exists():app.mount('/',StaticFiles(directory=site,html=True),name='site')
    return app
app=create_app()
