(async function(){
  var P=[{"pid": "10559152", "name": "Limba romana"}, {"pid": "10512022", "name": "Limba romana"}, {"pid": "10466319", "name": "Limba romana"}, {"pid": "10331323", "name": "Limba romana"}, {"pid": "10558992", "name": "Neurochirurgie"}, {"pid": "10334312", "name": "Limba romana"}, {"pid": "10635451", "name": "Limba romana - indrumar lexico-gramatical"}, {"pid": "10524844", "name": "Limba romana (fonetica, lexic, gramatica, stilistica)"}, {"pid": "10331680", "name": "Limba romana"}, {"pid": "10558056", "name": "Limba romana"}, {"pid": "10649500", "name": "Limba romana"}, {"pid": "10520006", "name": "Limba romana"}, {"pid": "10235854", "name": "Limba romana"}, {"pid": "10601106", "name": "Limba romana"}, {"pid": "9642311", "name": "Romana"}, {"pid": "10520024", "name": "Limba romana literara"}, {"pid": "10435080", "name": "Teste de limba romana"}, {"pid": "10520200", "name": "Teste de limba romana"}, {"pid": "10374797", "name": "Teste de limba romana"}, {"pid": "10546377", "name": "Teste de limba romana"}, {"pid": "10442381", "name": "100 de teste de limba romana"}, {"pid": "9819635", "name": "Limba romana artistica"}, {"pid": "9512018", "name": "Succes la limba romana"}, {"pid": "10257226", "name": "Admitere. Limba romana"}, {"pid": "10519137", "name": "Negatia"}, {"pid": "10589997", "name": "Indreptar"}, {"pid": "10622665", "name": "Literatura Limba romana"}, {"pid": "9890070", "name": "Limba romana (compendiu)"}, {"pid": "10493759", "name": "Bacalaureat limba romana"}, {"pid": "10152522", "name": "Evaluare nationala"}, {"pid": "10440535", "name": "Limba si literatra romana"}, {"pid": "10502704", "name": "Limba Romana Contemporana"}, {"pid": "10461563", "name": "Limba romana(sintaxa)"}, {"pid": "10573963", "name": "Limba si lteratura romana"}, {"pid": "10611217", "name": "Limba romana contemporana"}, {"pid": "10415357", "name": "Limba romana contemporana"}, {"pid": "10130920", "name": "Limba si literatura romana"}, {"pid": "10383299", "name": "Limba si literatura romana"}, {"pid": "10137733", "name": "Limba si literatura romana"}, {"pid": "10261261", "name": "Limba si literatura romana"}, {"pid": "10011918", "name": "Limba si literatura romana"}, {"pid": "10599200", "name": "Studii de lingvistica si stilistica"}, {"pid": "9999515", "name": "Limba si literatura romana"}];
  var D=500,ok=0,fail=0,errs=[];
  if(!window.location.hostname.includes('targulcartii.ro')){
    alert('Acest script trebuie rulat pe targulcartii.ro!\nDeschide targulcartii.ro, apoi F12 > Console > paste.');
    return;
  }
  var sd=document.createElement('div');
  sd.style.cssText='position:fixed;bottom:0;left:0;right:0;z-index:99999;background:#1a1a2e;color:#e0e0e0;padding:12px 20px;font-family:monospace;font-size:14px;box-shadow:0 -2px 10px rgba(0,0,0,0.5)';
  sd.innerHTML='<div id="tcp">Pornire... 0/'+P.length+'</div><div style="background:#333;height:6px;margin-top:8px;border-radius:3px"><div id="tcf" style="background:#e94560;height:100%;width:0%;border-radius:3px;transition:width 0.3s"></div></div><div id="tcc" style="margin-top:5px;font-size:11px;color:#888"></div>';
  document.body.appendChild(sd);
  function up(m,c){document.getElementById('tcp').textContent=m;document.getElementById('tcf').style.width=((ok+fail)/P.length*100).toFixed(1)+'%';if(c)document.getElementById('tcc').textContent=c}
  function sl(ms){return new Promise(function(r){setTimeout(r,ms)})}
  for(var i=0;i<P.length;i++){
    var p=P[i];
    up('Adaugare: '+(i+1)+'/'+P.length+' (OK:'+ok+' Erori:'+fail+')',p.name);
    try{
      var r=await fetch('/index.php?route=checkout/cart/update',{
        method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
        body:'product_id='+p.pid+'&quantity=1'
      });
      var j=await r.json();
      if(j&&!j.error){ok++}else{fail++;errs.push(p.name)}
    }catch(e){fail++;errs.push(p.name)}
    await sl(D);
  }
  document.getElementById('tcf').style.background=fail>0?'#e67e22':'#2ecc71';
  document.getElementById('tcf').style.width='100%';
  if(errs.length)console.log('Erori:',errs);
  up('GATA! '+ok+'/'+P.length+' adaugate. Redirectionare la cos in 3s...',' ');
  await sl(3000);
  window.location.href='/index.php?route=checkout/cart';
})();
