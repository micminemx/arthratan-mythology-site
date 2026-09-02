(()=>{
const TX_PER_PAGE=20;
let txIndex=null,txAttachments=null,txNonSource=null,txSessionModel=null,txPage=1,txQuery='';
const txCache=new Map();
const txEsc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const txPath=id=>`sources/zubaida/${id}.txt`;
const txAttachmentPath=(id,name)=>`sources/zubaida/attachments/${encodeURIComponent(id)}/${encodeURIComponent(name).replace(/'/g,'%27')}`;
function txRoute(){return (location.hash||'').slice(1)}
function txOwnRoute(h=txRoute()){return h==='stories'||h.startsWith('transmission:')||h.startsWith('session:')||h.startsWith('unit:')}
function txParseTransmission(text){
 const raw=String(text||'');
 const marker='[NON-QUOTED ZUBAIDA TRANSMISSION]';
 const markerAt=raw.indexOf(marker);
 let envelope='',body=raw;
 if(markerAt>=0){envelope=raw.slice(0,markerAt).trim();body=raw.slice(markerAt+marker.length).trim()}
 else{
  const lines=raw.split(/\r?\n/);let i=0;
  while(i<lines.length&&(!lines[i].trim()||/^(From|Subject|Message-ID|Thread-ID|Source):/i.test(lines[i].trim())))i++;
  body=lines.slice(i).join('\n').trim();
 }
 const meta={};
 envelope.split(/\r?\n/).forEach(line=>{const m=line.match(/^([^:]+):\s*(.*)$/);if(m)meta[m[1].trim().toLowerCase()]=m[2].trim()});
 return{raw,body,meta};
}
function txFirstLine(text){const {body}=txParseTransmission(text);return body.split(/\r?\n/).map(x=>x.trim()).find(Boolean)||'Zubaida transmission'}
function txExcerpt(text){const {body}=txParseTransmission(text),lines=body.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);return (lines.slice(1).join(' ')||lines[0]||'').slice(0,260)}
async function txLoadIndex(){if(txIndex)return txIndex;const r=await fetch('data/zubaida-index.json',{cache:'no-store'});if(!r.ok)throw new Error('Correspondence index unavailable');txIndex=await r.json();return txIndex}
async function txLoadAttachments(){if(txAttachments)return txAttachments;try{const r=await fetch('data/zubaida-attachments.json',{cache:'no-store'});txAttachments=r.ok?await r.json():{}}catch{txAttachments={}}return txAttachments}
async function txLoadNonSource(){if(txNonSource)return txNonSource;try{const r=await fetch('data/zubaida-nonsource.json',{cache:'no-store'});txNonSource=r.ok?await r.json():{non_source_records:[]}}catch{txNonSource={non_source_records:[]}}return txNonSource}
async function txLoad(id){if(txCache.has(id))return txCache.get(id);const p=fetch(txPath(id),{cache:'no-store'}).then(async r=>{if(!r.ok)return null;return await r.text()}).catch(()=>null);txCache.set(id,p);return p}
function txB36(value){const n=parseInt(String(value||''),36);return Number.isFinite(n)?n:0}
function txRows(value){return String(value||'').split(/\r?\n/).filter(Boolean).map(row=>row.split('\t'))}
async function txLoadSessionModel(){
 if(txSessionModel)return txSessionModel;
 const [sessionsRes,routesRes]=await Promise.all([
  fetch('data/zubaida-sessions.json',{cache:'no-store'}),
  fetch('data/zubaida-session-routes.json',{cache:'no-store'})
 ]);
 if(!sessionsRes.ok||!routesRes.ok)throw new Error('Session navigation manifest unavailable');
 const data=await sessionsRes.json(),routes=await routesRes.json();
 const transmissions=txRows(data.t).map((row,i)=>({order:i+1,id:row[0],headingLine:txB36(row[2])}));
 const parentByOrder=new Map(transmissions.map(row=>[row.order,row]));
 const types=Array.isArray(data?.codec?.types)?data.codec.types:[];
 const sessions=txRows(data.s).map(row=>{
  const [o,l,end,num,group]=row,order=txB36(o),line=txB36(l),parent=parentByOrder.get(order);
  return{kind:'session',targetId:`zs-${o}-${l}`,hash:`#session:zs-${o}-${l}`,order,line,end:txB36(end),number:num,group:group==='1',parentId:parent?.id||''};
 });
 const units=txRows(data.u).map(row=>{
  const [o,l,parentLine,typeCode]=row,order=txB36(o),line=txB36(l),parent=parentByOrder.get(order),typeIndex=txB36(typeCode);
  return{kind:'unit',targetId:`zu-${o}-${l}`,hash:`#unit:zu-${o}-${l}`,order,line,parentLine:txB36(parentLine),unitType:types[typeIndex]||'source unit',parentId:parent?.id||''};
 });
 const all=[...sessions,...units].sort((a,b)=>a.order-b.order||a.line-b.line||(a.kind==='session'?-1:1));
 const byTarget=new Map(all.map(row=>[row.targetId,row]));
 const byParent=new Map();all.forEach(row=>{if(!byParent.has(row.parentId))byParent.set(row.parentId,[]);byParent.get(row.parentId).push(row)});
 const sessionNav=sessions.slice().sort((a,b)=>a.order-b.order||a.line-b.line);
 const unitNav=units.slice().sort((a,b)=>a.order-b.order||a.line-b.line);
 const expected=Number(routes?.coverage?.targets||0);
 if(expected&&expected!==all.length)console.warn(`Session route coverage mismatch: expected ${expected}, decoded ${all.length}`);
 if(all.some(row=>!row.parentId))console.warn('Session route manifest contains orphan parent references');
 txSessionModel={data,routes,transmissions,sessions,units,all,byTarget,byParent,sessionNav,unitNav};
 return txSessionModel;
}
function txNonSourceRows(data){return data?.non_source_records||data?.ids||[]}
function txNonSourceMap(data){return new Map(txNonSourceRows(data).map(row=>[row.id,row]))}
function txSourceIds(index,nonsource){const non=txNonSourceMap(nonsource);return (index?.ids||[]).filter(id=>!non.has(id))}
function txAttachmentFiles(att,id){
 if(Array.isArray(att?.messages)){
  const row=att.messages.find(x=>x.message_id===id);
  if(!row||row.repository_status!=='preserved')return[];
  return (row.files||[]).map(name=>({name,path:txAttachmentPath(id,name)}));
 }
 return Array.isArray(att?.[id])?att[id]:[];
}
function txSetCrumb(label){try{setCrumb(label)}catch{const c=document.querySelector('#crumbs');if(c)c.textContent=label}}
function txShell(){return document.querySelector('#main')}
function txLineLabel(raw,line){const value=String(raw||'').split(/\r?\n/)[Math.max(0,line-1)]??'';return value.trim()||`Source line ${line}`}
function txTargetLabel(target,raw){
 const exact=txLineLabel(raw,target.line);
 if(target.kind==='session')return target.number?`Session ${target.number}: ${exact}`:exact;
 return `${String(target.unitType||'source unit').replace(/_/g,' ')}: ${exact}`;
}
function txTargetHref(target){return target.kind==='session'?`#session:${target.targetId}`:`#unit:${target.targetId}`}
function txSessionIndex(model,id,raw,focus){
 const rows=model?.byParent?.get(id)||[];if(!rows.length)return'';
 const sessions=rows.filter(row=>row.kind==='session'),units=rows.filter(row=>row.kind==='unit');
 const renderGroup=(title,list)=>list.length?`<div class="tx-session-group"><h3>${txEsc(title)}</h3><div class="tx-session-links">${list.map(row=>`<a class="tx-session-link${focus?.targetId===row.targetId?' is-current':''}" href="${txTargetHref(row)}"${focus?.targetId===row.targetId?' aria-current="location"':''}><span>${txEsc(txTargetLabel(row,raw))}</span><small>line ${row.line} · ${txEsc(row.targetId)}</small></a>`).join('')}</div></div>`:'';
 return `<details class="tx-session-index"${rows.length<=10?' open':''}><summary><span>Sessions &amp; source units</span><small>${sessions.length} session target${sessions.length===1?'':'s'} · ${units.length} subunit target${units.length===1?'':'s'}</small></summary><div class="tx-session-index-body"><p>These links point into the complete preserved transmission. Labels are read directly from the source line; no missing boundaries are invented.</p>${renderGroup('Sessions',sessions)}${renderGroup('Source-supported subunits',units)}</div></details>`;
}
function txFocusNav(model,target,raw){
 const list=target.kind==='session'?model.sessionNav:model.unitNav,index=list.findIndex(row=>row.targetId===target.targetId),prev=index>0?list[index-1]:null,next=index>=0&&index<list.length-1?list[index+1]:null,kindLabel=target.kind==='session'?'session':'source unit';
 return `<section class="tx-focus-card" aria-label="Deep-link context"><div><div class="eyebrow">Source-supported ${txEsc(kindLabel)} deep link</div><h2>${txEsc(txTargetLabel(target,raw))}</h2><p>This target is anchored to source line ${target.line} inside the complete parent transmission. The source panel below remains the full preserved transmission.</p></div><nav class="tx-focus-nav" aria-label="${txEsc(kindLabel)} navigation">${prev?`<a class="tx-source-link" href="${txTargetHref(prev)}">← Previous ${txEsc(kindLabel)}</a>`:''}<a class="tx-source-link" href="#transmission:${txEsc(target.parentId)}">Parent transmission</a>${next?`<a class="tx-source-link" href="${txTargetHref(next)}">Next ${txEsc(kindLabel)} →</a>`:''}</nav></section>`;
}
function txRenderSource(raw,focus){
 if(!focus)return txEsc(raw);
 const lines=String(raw||'').split(/\r?\n/);
 return lines.map((line,i)=>i+1===focus.line?`<span class="tx-source-focus" id="${txEsc(focus.targetId)}" tabindex="-1">${txEsc(line)}</span>`:txEsc(line)).join('\n');
}
function txScrollFocus(target){if(!target)return;requestAnimationFrame(()=>requestAnimationFrame(()=>document.getElementById(target.targetId)?.scrollIntoView({block:'center'})))}
async function renderStories(){
 const [data,nonsource]=await Promise.all([txLoadIndex(),txLoadNonSource()]);
 const sourceIds=txSourceIds(data,nonsource),nonCount=txNonSourceRows(nonsource).length;
 txSetCrumb('Story & Thread Archive');const main=txShell();
 main.innerHTML=`<div class="transmission-shell"><section class="transmission-hero"><div><div class="eyebrow">Zubaida correspondence · source-preserving canon layer</div><h1>Story & Thread Archive</h1><p>Every source-bearing Zubaida transmission is retained once, in source wording. Quoted reply chains are not multiplied into false duplicate sessions. Explanatory crosslinks sit around the source; they do not replace it.</p></div><div class="transmission-stats"><div class="transmission-stat"><b>${data.audit.sender_messages}</b><span>sender messages indexed</span></div><div class="transmission-stat"><b>${sourceIds.length}</b><span>source transmissions preserved</span></div><div class="transmission-stat"><b>${nonCount}</b><span>admin / reply-shell records</span></div></div></section><div class="tx-note"><b>Preservation rule:</b> ${txEsc(data.audit.preservation_rule)} Non-source administrative and reply-shell messages remain in the provenance dataset without appearing as phantom missing sessions.</div><div class="transmission-toolbar"><input class="transmission-search" id="txSearch" value="${txEsc(txQuery)}" placeholder="Search transmission titles or type 3+ characters for full-corpus search…"><div class="transmission-status" id="txStatus">Loading source cards…</div></div><div class="transmission-grid" id="txGrid"></div><div class="transmission-pager" id="txPager"></div></div>`;
 const input=document.querySelector('#txSearch');let timer;input?.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>{txQuery=input.value.trim();txPage=1;txPaintList()},220)});await txPaintList();
}
async function txPaintList(){
 const [data,nonsource]=await Promise.all([txLoadIndex(),txLoadNonSource()]),grid=document.querySelector('#txGrid'),pager=document.querySelector('#txPager'),status=document.querySelector('#txStatus');if(!grid)return;
 let ids=txSourceIds(data,nonsource);const q=txQuery.toLowerCase();
 if(q.length>=3){status.textContent='Searching preserved source corpus…';const rows=[];let cursor=0;const workers=Array.from({length:6},async()=>{while(cursor<ids.length){const i=cursor++,id=ids[i],text=await txLoad(id);if(text&&(text.toLowerCase().includes(q)||id.includes(q)))rows.push([i,id])}});await Promise.all(workers);ids=rows.sort((a,b)=>a[0]-b[0]).map(x=>x[1]);}
 const pages=Math.max(1,Math.ceil(ids.length/TX_PER_PAGE));txPage=Math.min(txPage,pages);const shown=ids.slice((txPage-1)*TX_PER_PAGE,txPage*TX_PER_PAGE);
 grid.innerHTML=shown.map((id,i)=>`<button class="transmission-card" data-id="${id}"><div class="tx-num">Transmission ${(txPage-1)*TX_PER_PAGE+i+1}</div><h3>Loading source heading…</h3><p>Retrieving preserved transmission text.</p><div class="tx-id">${id}</div></button>`).join('')||`<div class="tx-missing">No preserved transmissions matched this search.</div>`;
 grid.querySelectorAll('.transmission-card').forEach(card=>{card.onclick=()=>location.hash=`#transmission:${card.dataset.id}`;txHydrateCard(card)});
 status.textContent=`${ids.length} matching preserved transmission${ids.length===1?'':'s'} · page ${txPage}/${pages}`;
 pager.innerHTML=`<button ${txPage<=1?'disabled':''} id="txPrev">← Previous</button><span>${txPage} / ${pages}</span><button ${txPage>=pages?'disabled':''} id="txNext">Next →</button>`;
 document.querySelector('#txPrev')?.addEventListener('click',()=>{if(txPage>1){txPage--;txPaintList();window.scrollTo({top:0,behavior:'smooth'})}});document.querySelector('#txNext')?.addEventListener('click',()=>{if(txPage<pages){txPage++;txPaintList();window.scrollTo({top:0,behavior:'smooth'})}});
}
async function txHydrateCard(card){const id=card.dataset.id,text=await txLoad(id);if(!card.isConnected)return;const h=card.querySelector('h3'),p=card.querySelector('p');if(text){h.textContent=txFirstLine(text);p.textContent=txExcerpt(text)||'Verbatim source transmission.'}else{h.textContent='Preservation integrity warning';p.textContent='This source-bearing ID is indexed but its source file did not load.';card.classList.add('source-pending')}}
function txRenderNonSource(record){
 const represented=record?.represented_by?`<a class="tx-source-link" href="#transmission:${txEsc(record.represented_by)}">Open represented source transmission</a>`:'';
 return `<div class="tx-reader"><button class="tx-back" onclick="location.hash='#stories'">← Story & Thread Archive</button><div class="eyebrow" style="margin-top:22px">Zubaida correspondence · provenance-only record</div><h1>${txEsc(record?.classification||'Non-source correspondence record')}</h1><div class="tx-provenance"><span>Gmail source ID ${txEsc(record?.id||'')}</span><span>not counted as a source transmission</span></div><div class="tx-note" style="margin-top:18px">${txEsc(record?.note||record?.reason||'This message contains no new Zubaida-authored canon source body after reply-chain deduplication.')}</div>${represented}</div>`;
}
async function renderTransmission(id,focus=null){
 txSetCrumb(focus?`Zubaida ${focus.kind==='session'?'Session':'Source Unit'}`:'Zubaida Transmission');const main=txShell();main.innerHTML=`<div class="tx-reader"><button class="tx-back" id="txBack">← Story & Thread Archive</button><div class="tx-missing" style="margin-top:18px">Loading preserved source…</div></div>`;document.querySelector('#txBack').onclick=()=>location.hash='#stories';
 const [text,att,nonsource,sessionModel]=await Promise.all([txLoad(id),txLoadAttachments(),txLoadNonSource(),txLoadSessionModel().catch(err=>{console.warn(err);return null})]);
 const expected=focus?`${focus.kind}:${focus.targetId}`:`transmission:${id}`;if(txRoute()!==expected)return;
 if(!text){const record=txNonSourceMap(nonsource).get(id);if(record){main.innerHTML=txRenderNonSource(record);return}main.innerHTML=`<div class="tx-reader"><button class="tx-back" onclick="location.hash='#stories'">← Story & Thread Archive</button><div class="tx-missing" style="margin-top:18px"><b>Integrity warning:</b> ${txEsc(id)}<br><br>This ID is neither a preserved source transmission nor a classified non-source correspondence record.</div></div>`;return}
 const parsed=txParseTransmission(text),title=txFirstLine(text),files=txAttachmentFiles(att,id),sessionIndex=sessionModel?txSessionIndex(sessionModel,id,parsed.raw,focus):'',focusCard=focus&&sessionModel?txFocusNav(sessionModel,focus,parsed.raw):'';
 main.innerHTML=`<div class="tx-reader"><div class="tx-reader-head"><button class="tx-back" id="txBack2">← Story & Thread Archive</button><div class="eyebrow" style="margin-top:22px">Zubaida transmission · verbatim source layer</div><h1>${txEsc(title)}</h1><div class="tx-provenance"><span>Gmail source ID ${txEsc(id)}</span><span>quoted reply-chain removed</span><span>source wording retained</span>${parsed.meta.subject?`<span>${txEsc(parsed.meta.subject)}</span>`:''}</div></div>${focusCard}<div class="tx-note">The source below is kept separate from Codex explanation. Crossreferential explanation may be added around it, but this panel is the preservation layer.</div>${sessionIndex}<pre class="tx-source">${txRenderSource(parsed.raw,focus)}</pre>${files.length?`<section class="tx-attachments"><h2>Original attachments</h2>${files.map(f=>`<a class="tx-source-link" href="${txEsc(f.path)}" target="_blank" rel="noopener">${txEsc(f.name)}</a>`).join('')}</section>`:''}</div>`;document.querySelector('#txBack2').onclick=()=>location.hash='#stories';txScrollFocus(focus);
}
async function renderSessionTarget(kind,targetId){
 const model=await txLoadSessionModel(),target=model.byTarget.get(targetId),main=txShell();
 if(!target||target.kind!==kind){txSetCrumb('Zubaida Session Navigation');main.innerHTML=`<div class="tx-reader"><button class="tx-back" onclick="location.hash='#stories'">← Story & Thread Archive</button><div class="tx-missing" style="margin-top:18px"><b>Session-route integrity warning:</b> ${txEsc(targetId)}<br><br>This target is not established by the committed Zubaida session manifest.</div></div>`;return}
 return renderTransmission(target.parentId,target);
}
async function txHandle(){const h=txRoute();if(h==='stories')return renderStories();if(h.startsWith('transmission:'))return renderTransmission(h.slice('transmission:'.length));if(h.startsWith('session:'))return renderSessionTarget('session',h.slice('session:'.length));if(h.startsWith('unit:'))return renderSessionTarget('unit',h.slice('unit:'.length))}
window.addEventListener('hashchange',e=>{const h=txRoute();if(txOwnRoute(h)){e.stopImmediatePropagation();txHandle().catch(err=>{console.error(err);txShell().innerHTML=`<div class="card"><h3>Archive rendering error</h3><p>${txEsc(err.message)}</p></div>`})}},true);
if(txOwnRoute())[0,120,500,950].forEach(ms=>setTimeout(()=>{if(txOwnRoute())txHandle()},ms));
})();
