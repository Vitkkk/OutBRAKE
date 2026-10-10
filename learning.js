'use strict';
// Exported logistic model and empirical geometry; no training in the browser.
(function(scope){
 function features(e){const c=Math.log1p(Math.max(0,e.cape)),s=e.shear,h=Math.max(-500,Math.min(1500,e.srh));return [c,s,h,e.lcl/1000,e.td,Math.log1p(Math.abs(e.cin)),c*s/25,c*h/150];}
 function predict(model,e){const x=features(e);if(!x.every(Number.isFinite)||e.cin===null)throw Error('Ingredientes incompletos');const z=model.intercept+x.reduce((sum,v,i)=>sum+(v-model.means[i])/model.scales[i]*model.coefficients[i],0);return 1/(1+Math.exp(-z));}
 function shapeAt(template,p){const points=template.shape,q=Math.max(0,Math.min(1,p))*(points.length-1),i=Math.min(points.length-2,Math.floor(q)),t=q-i;
  // Catmull–Rom interpolation follows the surveyed vertices continuously.
  const a=points[Math.max(0,i-1)],b=points[i],c=points[i+1],d=points[Math.min(points.length-1,i+2)];
  return [0,1].map(k=>.5*(2*b[k]+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t));
 }
 scope.OutBRAKELearning={features,predict,shapeAt};
})(typeof window!=='undefined'?window:globalThis);
