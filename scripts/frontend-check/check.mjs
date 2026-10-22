import {JSDOM} from 'jsdom';
import {build} from 'esbuild';
import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../../',import.meta.url)).replace(/\/$/,'');
const base=process.env.NEERWATCH_BASE_URL||'http://127.0.0.1:8010';
const bundle=await build({entryPoints:[root+'/frontend/src/main.jsx'],bundle:true,write:false,format:'iife',loader:{'.css':'empty'},logLevel:'silent'});
const rows=(await(await fetch(base+'/api/reservoirs')).json()).items;
const checks=[];
for(let pass=0;pass<2;pass++){
 const dom=new JSDOM('<div id="root"></div>',{url:base,runScripts:'outside-only',pretendToBeVisual:true});
 const w=dom.window;w.AbortController=globalThis.AbortController;w.HTMLElement.prototype.scrollIntoView=function(){};
 const old=w.document.createElementNS.bind(w.document);w.document.createElementNS=(ns,tag)=>{const e=old(ns,tag);if(tag==='svg')e.createSVGRect=()=>({});return e};
 w.fetch=(url,options)=>fetch(new URL(url,base),options);
 w.eval(bundle.outputFiles[0].text);
 async function until(fn){for(let i=0;i<300;i++){if(fn())return;await new Promise(r=>setTimeout(r,50))}throw Error('Frontend state deadline: '+w.document.body.textContent.slice(-1800))}
 await until(()=>w.document.querySelectorAll('.reservoir-button').length===rows.length);
 await until(()=>w.document.querySelectorAll('.map path[data-reservoir-id]').length===rows.length);
 if(w.document.querySelectorAll('#comparison tbody tr').length!==rows.length)throw Error('Missing comparison rows');
 if(w.document.body.textContent.includes('Inventory coordinate; boundary unavailable'))throw Error('Pending inventory leaked');
 for(const r of rows){
  console.log('checking',pass,r.id);
  const button=[...w.document.querySelectorAll('.reservoir-button')].find(b=>b.querySelector('b').textContent===r.name);button.click();
  await until(()=>w.document.querySelector('.reservoir-title h2')?.textContent.startsWith(r.name));
  const text=w.document.querySelector('.stats').textContent;
  if(/Unavailable|Not processed/.test(text))throw Error('Incomplete workspace '+r.id);
  const detail=await(await fetch(base+'/api/reservoirs/'+r.id)).json();
  if(!text.includes(Number(detail.sentinel2.chlorophyll_a).toLocaleString('en-IN',{maximumFractionDigits:2})))throw Error('Wrong concentration '+r.id);
  const map=w.document.querySelector('.map');await until(()=>map.querySelector(`path[data-reservoir-id="${r.id}"]`));
  const polygon=map.querySelector(`path[data-reservoir-id="${r.id}"]`);polygon.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  await until(()=>map.querySelector('.leaflet-popup-content')?.textContent.startsWith(r.name+' · '));
  await until(()=>polygon.getAttribute('stroke-width')==='2.5');
  const imageSrc=w.document.querySelector('.reservoir-photo').getAttribute('src');
  if(!imageSrc.includes('scene_id='+detail.sentinel2.latest.item_id))throw Error('Unpinned scene '+r.id);
  const popup=map.querySelector('.leaflet-popup-content').textContent;
  if(!popup.includes('µg/L')||!popup.includes(detail.sentinel2.classification.name))throw Error('Missing popup evidence '+r.id);
  checks.push({reservoir:r.id,reopen_pass:pass+1,display:'PASS',map_svg_present:'PASS',polygon_popup_and_click:'PASS',image_src:w.document.querySelector('.reservoir-photo')?.getAttribute('src'),stats:text});
 }
 const sorter=w.document.querySelector('[aria-label="Sort comparison"]');
 for(const mode of ['name','concentration','increase','decrease','category']){
  sorter.value=mode;sorter.dispatchEvent(new w.Event('change',{bubbles:true}));await new Promise(r=>setTimeout(r,25));
  const sorted=[...rows].sort((a,b)=>mode==='name'?a.name.localeCompare(b.name):mode==='increase'?b.monitoring.change.percent-a.monitoring.change.percent:mode==='decrease'?a.monitoring.change.percent-b.monitoring.change.percent:mode==='category'?b.monitoring.classification.rank-a.monitoring.classification.rank:b.monitoring.chlorophyll_a-a.monitoring.chlorophyll_a);
  if(w.document.querySelector('#comparison tbody tr .table-reservoir').textContent!==sorted[0].name)throw Error('Incorrect sort '+mode);
 }
 dom.window.close();
}
await fs.writeFile(root+'/output/public-frontend-state-verification.json',JSON.stringify(checks,null,2));
console.log('PASS',checks.length,'real React workspace loads across two fresh DOM sessions; visual layout not checked.');
