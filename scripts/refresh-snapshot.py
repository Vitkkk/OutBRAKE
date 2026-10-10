import urllib.request, urllib.parse, json, math, datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'dist' if (root/'dist').is_dir() else root
regions=[
('Rio Grande do Sul',-29.5,-53),('Oeste do Paraná',-25,-53.5),('Santa Catarina',-27,-51),('São Paulo',-22.5,-48.5),('Corrientes',-28,-58),('Santa Fé',-31.5,-60.5),('Córdoba',-32,-64),('Uruguai',-33,-56),('Paraguai',-25.5,-57),('Bolívia oriental',-18,-62),
('Oklahoma',35.5,-98),('Texas',32,-99),('Kansas',38,-98),('Nebraska',41,-99),('Iowa',42,-94),('Illinois',40,-89),('Mississippi',33,-90),('Alabama',33,-86),('Flórida',28,-82),('Carolina do Norte',35,-79),('Dakota do Sul',44,-100),
('França',46,2),('Alemanha',50,10),('Itália',44,11),('Polônia',51,19),('Turquia',39,33),('África do Sul',-28,28),('Austrália oriental',-28,150),('Austrália ocidental',-31,117),('Bangladesh',24,90),('Índia oriental',23,87),('China oriental',31,117),('Japão',35,137),('México',25,-100),('Canadá',50,-100),('Nova Zelândia',-43,172)]
def get(endpoint,locations,variables):
 p={'latitude':','.join(str(x[1]) for x in locations),'longitude':','.join(str(x[2]) for x in locations),'hourly':','.join(variables),'wind_speed_unit':'ms','timezone':'GMT','forecast_days':3}
 u='https://api.open-meteo.com/v1/'+endpoint+'?'+urllib.parse.urlencode(p)
 with urllib.request.urlopen(u,timeout=50) as r:return json.load(r)
def uv(s,d):
 a=d*math.pi/180
 return (-s*math.sin(a),-s*math.cos(a))
def score(h,i):
 vals=[h.get(k,[None]*len(h['time']))[i] for k in ['cape','temperature_2m','dew_point_2m','wind_speed_10m','wind_direction_10m','wind_speed_500hPa','wind_direction_500hPa']]
 if any(v is None for v in vals):return 0
 c,t,td,s,d,s5,d5=vals
 u,v=uv(s,d);u5,v5=uv(s5,d5)
 sh=math.hypot(u5-u,v5-v)
 cin=(h.get('convective_inhibition') or [0]*len(h['time']))[i] or 0
 return round(100*min(1,c/1800)**.5*min(1,sh/24)*min(1,max(0,td+5)/22)*math.exp(-abs(cin)/220),1)
now=datetime.datetime.now(datetime.timezone.utc)
variables=['cape','convective_inhibition','temperature_2m','dew_point_2m','wind_speed_10m','wind_direction_10m','wind_speed_500hPa','wind_direction_500hPa']
data=get('gfs',regions,variables)
rank=[]
for reg,d in zip(regions,data):
 h=d['hourly'];inds=[i for i,t in enumerate(h['time']) if 0<=(datetime.datetime.fromisoformat(t).replace(tzinfo=datetime.timezone.utc)-now).total_seconds()<=86400]
 if not inds:continue
 i=max(inds,key=lambda i:score(h,i))
 rank.append({'name':reg[0],'lat':reg[1],'lon':reg[2],'index':score(h,i),'time':h['time'][i]+'Z','cape':h['cape'][i]})
rank.sort(key=lambda r:r['index'],reverse=True)
chosen=rank[0];reg=(chosen['name'],chosen['lat'],chosen['lon'])
levels=[1000,975,950,925,900,850,800,700,600,500,400,300]
fullvars=variables+['surface_pressure']+[f'{v}_{p}hPa' for p in levels for v in ['temperature','relative_humidity','geopotential_height','wind_speed','wind_direction']]
full=get('gfs',[reg],fullvars)
boot={'retrievedAt':now.isoformat(),'selection':'36 pontos amostrados, próximas 24 h; índice experimental, sem probabilidade calibrada','ranking':rank,'region':chosen,'data':full}
(out/'bootstrap.json').write_text(json.dumps(boot,separators=(',',':')))
print(json.dumps({'selected':chosen,'retrievedAt':boot['retrievedAt'],'top5':rank[:5]},ensure_ascii=False))
