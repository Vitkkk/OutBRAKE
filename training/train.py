"""First retrospective environmental classifier; no test-year tuning."""
import json, math, re
from datetime import datetime,timedelta
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss,log_loss
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'dist' if (ROOT.parent/'dist').exists() else ROOT.parent
FEATURES=['log_cape','shear','srh','lcl_km','dewpoint','log_cin','cape_shear','cape_srh']
def predictors(df):
 c=np.log1p(df.cape.clip(lower=0));s=df.shear;h=df.srh.clip(-500,1500)
 return np.column_stack([c,s,h,df.lcl/1000,df.td,np.log1p(df.cin.abs()),c*s/25,c*h/150])
def haversine(lat,lon,lats,lons):
 a=np.sin(np.radians(lats-lat)/2)**2+np.cos(np.radians(lat))*np.cos(np.radians(lats))*np.sin(np.radians(lons-lon)/2)**2
 return 6371*2*np.arcsin(np.sqrt(np.clip(a,0,1)))
def reports():
 records=[];rejected=[];seen=set()
 for year in [2024,2025]:
  for r in json.loads((ROOT/'cache'/f'tornadoes-{year}.json').read_text())['rows']:
   if r['EVENT_ID'] in seen:continue
   seen.add(r['EVENT_ID'])
   try:
    local=datetime.strptime(r['BEGIN_DATE_TIME'],'%d-%b-%y %H:%M:%S');m=re.search(r'([+-]\d+)$',r['CZ_TIMEZONE']);assert m
    utc=local-timedelta(hours=int(m[1]));lat=float(r['BEGIN_LAT']);lon=float(r['BEGIN_LON']);assert 20<lat<55 and -130<lon<-60
    records.append({'id':r['EVENT_ID'],'time':utc.isoformat()+'Z','lat':lat,'lon':lon})
   except Exception:rejected.append(r['EVENT_ID'])
 return pd.DataFrame(records),rejected

def main():
 df=pd.DataFrame(json.loads((ROOT/'cache'/'features.json').read_text()));r,rejected=reports();r['dt']=pd.to_datetime(r.time,utc=True)
 labels=[];ids=[]
 for row in df.itertuples():
  t=pd.Timestamp(row.time);near=r[(r.dt>=t)&(r.dt<t+pd.Timedelta(hours=6))]
  matches=near[haversine(row.lat,row.lon,near.lat.to_numpy(),near.lon.to_numpy())<=150]
  labels.append(int(len(matches)>0));ids.append('|'.join(matches.id))
 df['target']=labels;df['report_ids']=ids
 train=df.year==2024;test=df.year==2025;assert set(df[train].time.str[:10]).isdisjoint(set(df[test].time.str[:10]))
 x=predictors(df);y=df.target.to_numpy();model=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000,random_state=1041026));model.fit(x[train],y[train]);p=model.predict_proba(x[test])[:,1]
 # Fair baseline: the old heuristic calibrated on the SAME training set.
 old=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000));old.fit(df.loc[train,['favor']],y[train]);oldp=old.predict_proba(df.loc[test,['favor']])[:,1]
 climate=np.full(test.sum(),y[train].mean())
 def metrics(pred):
  yy=y[test];event=pred>=.1;tp=int(((yy==1)&event).sum());fp=int(((yy==0)&event).sum());fn=int(((yy==1)&~event).sum())
  return {'brier':float(brier_score_loss(yy,pred)),'average_precision':float(average_precision_score(yy,pred)),'roc_auc':float(roc_auc_score(yy,pred)),'log_loss':float(log_loss(yy,pred)),'threshold':.1,'hits':tp,'false_alarms':fp,'misses':fn,'precision_at_threshold':tp/(tp+fp) if tp+fp else None,'recall_at_threshold':tp/(tp+fn) if tp+fn else None}
 scores={name:metrics(pr) for name,pr in [('learned',p),('heuristic',oldp),('climatology',climate)]}
 for name in ['learned','heuristic']:
  scores[name]['brier_skill_vs_climatology']=1-scores[name]['brier']/scores['climatology']['brier']
 # Paired day-block bootstrap reflects dependence among points/hours of a day.
 dates=df.loc[test,'time'].str[:10].to_numpy();unique=np.unique(dates);rng=np.random.default_rng(1041026);delta=[]
 daily=[np.where(dates==d)[0] for d in unique]
 for _ in range(500):
  ix=np.concatenate([daily[j] for j in rng.integers(0,len(daily),len(daily))]);yy=y[test][ix]
  delta.append(float(np.mean((oldp[ix]-yy)**2)-np.mean((p[ix]-yy)**2)))
 calibration=[]
 for ix in np.array_split(np.argsort(p),8):calibration.append({'n':len(ix),'predicted':float(p[ix].mean()),'observed':float(y[test][ix].mean())})
 scaler,lr=model.steps[0][1],model.steps[1][1]
 artifact={'version':1,'kind':'retrospective-environmental-classifier','model':'GFS global historical seamless','target':'At least one NCEI tornado county/event start within 150 km during the next 6 h','training_period':'2024-04-01 / 2024-05-31','test_period':'2025-04-01 / 2025-05-31','forecast_lead_hours':None,'features':FEATURES,'means':scaler.mean_.tolist(),'scales':scaler.scale_.tolist(),'coefficients':lr.coef_[0].tolist(),'intercept':float(lr.intercept_[0]),'training_rows':int(train.sum()),'test_rows':int(test.sum()),'training_positive':int(y[train].sum()),'test_positive':int(y[test].sum()),'training_days':int(df[train].time.str[:10].nunique()),'test_days':len(unique),'grid_points':int(df.point.nunique()),'scores':scores,'paired_day_bootstrap_brier_gain_95pct':np.quantile(delta,[.025,.975]).tolist(),'calibration':calibration,'rejected_report_records':len(rejected),'limitations':['Archive stitches model runs: this is not a fixed-lead operational forecast test.','16 fixed points, April–May only, central/eastern USA.','No-report labels include possible unreported events. NCEI rows are county/event records, not unique tornado counts.','Positive target uses report-segment starts, not complete damage corridors.','No radar or observed radiosondes in this first training.','Probabilities describe a 150 km / 6 h report target, not individual-cell tornadogenesis.'],'sources':json.loads((ROOT/'sources.json').read_text())}
 (OUT/'training-model.json').write_text(json.dumps(artifact,indent=2,allow_nan=False))
 df['split']=np.where(train,'train','test');df['probability']=model.predict_proba(x)[:,1];df.to_csv(ROOT/'dataset.csv',index=False,float_format='%.7g')
 # All held-out predictions available, not just selected successful cases.
 df[test].to_csv(OUT/'training-test.csv',index=False,float_format='%.7g')
 # Exact coefficients reproduce sklearn; used by app and offline tools.
 reproduced=1/(1+np.exp(-((x[test]-scaler.mean_)/scaler.scale_@lr.coef_[0]+lr.intercept_[0])));assert np.max(abs(reproduced-p))<1e-12
 print(json.dumps({k:artifact[k] for k in ['training_rows','test_rows','training_positive','test_positive','scores','paired_day_bootstrap_brier_gain_95pct']},indent=2))
if __name__=='__main__':main()
