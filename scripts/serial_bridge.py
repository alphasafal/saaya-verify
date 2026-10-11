"""Forward USB serial JSON to the loopback bench API. No serial contents are executed."""
import argparse,json,os,time
import serial,httpx
p=argparse.ArgumentParser();p.add_argument('port');p.add_argument('--baud',type=int,default=115200);args=p.parse_args()
token=os.getenv('SAAYA_DEVICE_TOKEN')
if not token:raise SystemExit('Set SAAYA_DEVICE_TOKEN in both API and bridge environments.')
with serial.Serial(args.port,args.baud,timeout=2) as stream,httpx.Client(timeout=5) as client:
    while True:
        # Discard accumulated frames before waiting for the next acquisition.
        stream.reset_input_buffer()
        line=stream.readline(8193)
        if len(line)>8192:print('Rejected oversized serial frame');continue
        try:
            data=json.loads(line)
            if not isinstance(data,dict) or data.get('source')!='MEASURED':continue
            res=client.post('http://127.0.0.1:8765/telemetry',json=data,headers={'X-Device-Token':token})
            if res.status_code!=200:print('API rejected frame:',res.status_code)
        except (json.JSONDecodeError,UnicodeDecodeError):continue
        except httpx.HTTPError:print('API unavailable; frame not stored');time.sleep(1)
