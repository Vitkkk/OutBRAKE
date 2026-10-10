"""Reproducible public-data collection; caches downloads, no keys required."""
import concurrent.futures, csv, gzip, hashlib, io, json, re, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CACHE=ROOT/'cache'; CACHE.mkdir(exist_ok=True)
GRID=[{'id':f'{lat}_{lon}','lat':lat,'lon':lon} for lat in [31,35,39,43] for lon in [-100,-95,-90,-85]]
VARIABLES=['cape','convective_inhibition','temperature_2m','dew_point_2m','surface_pressure','wind_speed_10m','wind_direction_10m']
for p in [1000,925,850,700,600,500,400]:
 VARIABLES += [f'{v}_{p}hPa' for v in ['temperature','relative_humidity','geopotential_height','wind_speed','wind_direction']]
def read(url):
 with urllib.request.urlopen(url,timeout=90) as r:return r.read()
def weather(year):
 p=CACHE/f'gfs-{year}.json'
 q={'latitude':','.join(str(x['lat']) for x in GRID),'longitude':','.join(str(x['lon']) for x in GRID),'start_date':f'{year}-04-01','end_date':f'{year}-05-31','hourly':','.join(VARIABLES),'models':'gfs_global','wind_speed_unit':'ms','timezone':'GMT'}
 url='https://historical-forecast-api.open-meteo.com/v1/forecast?'+urllib.parse.urlencode(q)
 if not p.exists():p.write_bytes(read(url))
 d=json.loads(p.read_text());assert isinstance(d,list) and len(d)==len(GRID)
 print('GFS',year,len(d),'points',flush=True)
 return {'kind':'GFS historical seamless (not fixed forecast lead)','year':year,'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def reports(year,listing):
 base='https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/'
 f=sorted(set(re.findall(r'StormEvents_details-ftp_v1.0_d'+str(year)+r'_c\d+\.csv.gz',listing)))[-1];p=CACHE/f
 if not p.exists():p.write_bytes(read(base+f))
 rows=[r for r in csv.DictReader(io.StringIO(gzip.decompress(p.read_bytes()).decode('utf-8-sig'))) if r['EVENT_TYPE']=='Tornado']
 (CACHE/f'tornadoes-{year}.json').write_text(json.dumps({'source':base+f,'rows':rows}))
 print('NCEI',year,len(rows),'county/event records',flush=True)
 return {'kind':'NCEI Storm Events county/event records','year':year,'url':base+f,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def tracks():
 base='https://services.dat.noaa.gov/arcgis/rest/services/nws_damageassessmenttoolkit/DamageViewer/MapServer/1/query';features=[];page=0
 while True:
  p=CACHE/f'dat-2024-v2-page{page}.json'
  q={'where':"stormdate >= DATE '2024-01-01' AND stormdate < DATE '2025-01-01'",'outFields':'objectid,event_id,stormdate,starttime,endtime,startlat,startlon,endlat,endlon,length,width,efscale,efnum,maxwind','returnGeometry':'true','outSR':'4326','f':'json','resultRecordCount':1000,'resultOffset':page*1000,'orderByFields':'objectid'}
  if not p.exists():p.write_bytes(read(base+'?'+urllib.parse.urlencode(q)))
  d=json.loads(p.read_text());assert 'features' in d,d
  features.extend(d['features'])
  if not d.get('exceededTransferLimit'):break
  page+=1
 (CACHE/'dat-2024.json').write_text(json.dumps(features));print('DAT',len(features),'surveyed polylines',flush=True)
 return {'kind':'DAT 2024 surveyed polylines (preliminary survey data)','url':base,'records':len(features)}
if __name__=='__main__':
 manifest=[];listing=read('https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/').decode()
 for y in [2024,2025]:manifest.append(reports(y,listing))
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:manifest.extend(ex.map(weather,[2024,2025]))
 manifest.append(tracks())
 (ROOT/'sources.json').write_text(json.dumps({'grid':GRID,'period':'April–May 2024 train; April–May 2025 held-out test','sources':manifest},indent=2))
