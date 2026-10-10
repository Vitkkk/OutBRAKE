'use strict';
(async()=>{const $=id=>document.getElementById(id);try{
 const [model,csv,shapes]=await Promise.all([fetch('training-model.json').then(r=>r.json()),fetch('training-test.csv').then(r=>r.text()),fetch('track-shapes.json').then(r=>r.json())]);
 const lines=csv.trim().split(/\r?\n/),headers=lines.shift().split(','),rows=lines.map(l=>Object.fromEntries(l.split(',').map((v,i)=>[headers[i],['point','time','report_ids','split'].includes(headers[i])?v:Number(v)])));
 $('trainCount').textContent=model.training_rows.toLocaleString('pt-BR');$('testCount').textContent=model.test_rows.toLocaleString('pt-BR');$('shapeCount').textContent=shapes.templates.length.toLocaleString('pt-BR');
 $('trainDetail').textContent=model.training_days+' dias · '+model.training_positive+' exemplos positivos · '+(model.training_rows-model.training_positive)+' sem registro no alvo.';
 $('testDetail').textContent=model.test_days+' dias inéditos · '+model.test_positive+' exemplos positivos · '+(model.test_rows-model.test_positive)+' sem registro no alvo.';
 $('trainingStatus').textContent='Primeiro resultado: misto. Pequena melhora no Brier; AP ligeiramente menor que a fórmula anterior. A diferença de Brier ainda é inconclusiva no intervalo por reamostragem de dias.';
 for(const [id,name] of [['learned','Modelo treinado'],['heuristic','Fórmula anterior ajustada'],['climatology','Frequência do treino']]){const m=model.scores[id],tr=document.createElement('tr');for(const v of [name,m.brier.toFixed(5),m.average_precision.toFixed(3),m.roc_auc.toFixed(3)]){const td=document.createElement('td');td.textContent=v;tr.append(td);}$('metricsRows').append(tr);}
 const m=model.scores.learned,b=model.scores.heuristic,ci=model.paired_day_bootstrap_brier_gain_95pct;
 $('comparisonText').textContent='Redução do Brier de '+(100*(1-m.brier/b.brier)).toFixed(1)+'% em relação à fórmula anterior ajustada. Intervalo de 95% do ganho absoluto: '+ci.map(x=>x.toFixed(5)).join(' a ')+', incluindo zero (500 reamostragens por dia).';
 $('thresholdText').textContent='No limiar fixo de 10%: '+m.hits+' acertos, '+m.false_alarms+' falsos alarmes e '+m.misses+' eventos perdidos. Não há ajuste desse limiar usando o teste.';
 for(const date of [...new Set(rows.map(r=>r.time.slice(0,10)))]){$('caseDate').add(new Option(date,date));}
 for(const point of model.sources.grid){$('casePoint').add(new Option(point.lat+'°N / '+Math.abs(point.lon)+'°W',point.id));}
 function update(){const r=rows.find(r=>r.time.slice(0,10)===$('caseDate').value&&r.point===$('casePoint').value&&r.time.slice(11,13)===$('caseHour').value);if(!r)return;
  const p=window.OutBRAKELearning.predict(model,r);$('caseProbability').textContent=(100*p).toFixed(1)+'%';$('probabilityFill').style.width=(100*p)+'%';$('caseObserved').textContent=r.target?'Com registro de tornado':'Sem registro no alvo';$('caseObserved').className=r.target?'positive-case':'';
  const end=new Date(Date.parse(r.time)+6*3600000);$('caseWindow').textContent=r.time.replace('T',' ')+' até '+end.toISOString().replace('T',' ').slice(0,16)+' UTC · raio 150 km';
  $('caseIngredients').textContent='CAPE '+Math.round(r.cape)+' J/kg · shear '+r.shear.toFixed(1)+' m/s · SRH '+Math.round(r.srh)+' m²/s² · LCL '+Math.round(r.lcl)+' m · CIN '+Math.round(r.cin)+' J/kg';$('caseReports').textContent=r.report_ids?'IDs NCEI: '+r.report_ids.split('|').join(', '):'Todos os ingredientes deste exemplo entraram na avaliação, mesmo sem registro de tornado.';
 }
 ['caseDate','casePoint','caseHour'].forEach(id=>$(id).onchange=update);$('randomCase').onclick=()=>{const r=rows[Math.floor(Math.random()*rows.length)];$('caseDate').value=r.time.slice(0,10);$('casePoint').value=r.point;$('caseHour').value=r.time.slice(11,13);update();};update();
 }catch(err){$('trainingStatus').textContent='Não foi possível carregar o experimento: '+err.message;}
})();
