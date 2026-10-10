"""Fit an empirical distribution of normalized, surveyed 2024 path shapes."""
import json, math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/'dist' if (ROOT.parent/'dist').exists() else ROOT.parent
features=json.loads((ROOT/'cache'/'dat-2024.json').read_text());templates=[];skipped=0
for feature in features:
 a=feature['attributes'];paths=feature.get('geometry',{}).get('paths',[])
 # Do not bridge disconnected geometry or infer curvature from two endpoints.
 if len(paths)!=1 or len(paths[0])<3:skipped+=1;continue
 pts=np.array(paths[0],dtype=float)[:,:2];lat=pts[0,1];xy=(pts-pts[0])*np.array([111*math.cos(math.radians(lat)),111])
 chord=np.linalg.norm(xy[-1]);seg=np.linalg.norm(np.diff(xy,axis=0),axis=1);arc=np.r_[0,np.cumsum(seg)];length=arc[-1]
 if not 2<=length<=150 or chord<1 or length/chord>1.3:skipped+=1;continue
 direction=xy[-1]/chord;cross=np.array([-direction[1],direction[0]]);u=xy@direction/chord;v=xy@cross/chord
 if np.max(abs(v))>.25 or np.any(np.diff(u)<-.05):skipped+=1;continue
 s=np.linspace(0,1,33);shape=np.column_stack([np.interp(s,arc/length,u),np.interp(s,arc/length,v)])
 templates.append({'id':'DAT-'+str(a['objectid']),'event_name':str(a.get('event_id') or ''),'date':a.get('stormdate'),'length_km':round(float(length),3),'chord_km':round(float(chord),3),'sinuosity':round(float(length/chord),5),'max_lateral_fraction':round(float(np.max(abs(v))),5),'vertices':len(pts),'shape':np.round(shape,6).tolist()})
artifact={'version':1,'method':'Empirical normalized survey-path shapes; not a conditional atmospheric trajectory model','source':'https://services.dat.noaa.gov/arcgis/rest/services/nws_damageassessmenttoolkit/DamageViewer/MapServer/1','year':2024,'source_records':len(features),'excluded':skipped,'templates':templates}
(OUT/'track-shapes.json').write_text(json.dumps(artifact,separators=(',',':')))
print({'surveyed_records':len(features),'usable_shapes':len(templates),'median_sinuosity':float(np.median([t['sinuosity'] for t in templates]))})
