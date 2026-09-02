(()=>{
const TX_PER_PAGE=20;
let txIndex=null,txAttachments=null,txPage=1,txQuery='';
const txCache=new Map();
const txEsc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const txPath=id=>`sources/zubaida/${id}.txt`;
function txRoute(){return (location.hash||'').slice(1)}
function txFirstLine(text){return String(text||'').split(/\r?\n/).map(x=>x.trim()).find(Boolean)||'Zubaida transmission'}
function txExcerpt(text){const lines=String(text||'').split(/\r?\n/).map(x=>x.trim()).filter(Boolean);return (lines.slice(1).join(' ')||lines[0]||'').slice(0,260)}
async function txLoadIndex(){if(txIndex)return txIndex;const r=await fetch('data/zubaida-index.json',{cache:'no-store'});if(!r.ok)throw new Error('Correspondence index unavailable');txIndex=await r.json();return txIndex}
async function txLoadAttachments(){if(txAttachments)return txAttachments;try{const r=await fetch('data/zubaida-attachments.json',{cache:'no-store'});txAttachments=r.ok?await r.json():{}}catch{txAttachments={}}return txAttachments}
async function txLoad(id){if(txCache.has(id))return txCache.get(id);const p=fetch(txPath(id),{cache:'no-store'}).then(async r=>{if(!r.ok)return null;return await r.text()}).catch(()=>null);txCache.set(id,p);return p}
function txSetCrumb(label){try{setCrumb(label)}catch{const c=document.querySelector('#crumbs');if(c)c.textContent=label}}
function txShell(){return document.querySelector('#main')}
async function renderStories(){
 const data=await txLoadIndex();txSetCrumb('Story & Thread Archive');const main=txShell();
 main.innerHTML=`<div class="transmission-shell"><section class="transmission-hero"><div><div class="eyebrow">Zubaida correspondence · source-preserving canon layer</div><h1>Story & Thread Archive</h1><p>New Zubaida-authored transmissions are retained once, in source wording. Quoted reply chains are not multiplied into false duplicate sessions. Explanatory crosslinks sit around the source; they do not replace it.</p></div><div class="transmission-stats"><div class="transmission-stat"><b>${data.audit.sender_messages}</b><span>sender messages indexed</span></div><div class="transmission-stat"><b>${data.audit.source_bearing_transmissions}</b><span>source-bearing transmissions</span></div><div class="transmission-stat"><b>1×</b><span>quote-chain deduplication</span></div></div></section><div class="tx-note"><b>Preservation rule:</b> ${txEsc(data.audit.preservation_rule)} Administrative messages remain indexable in the correspondence layer so that provenance is not silently discarded.</div><div class="transmission-toolbar"><input class="transmission-search" id="txSearch" value="${txEsc(txQuery)}" placeholder="Search loaded transmission titles or type 3+ characters for full-corpus search…"><div class="transmission-status" id="txStatus">Loading source cards…</div></div><div class="transmission-grid" id="txGrid"></div><div class="transmission-pager" id="txPager"></div></div>`;
 const input=document.querySelector('#txSearch');let timer;input?.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>{txQuery=input.value.trim();txPage=1;txPaintList()},220)});await txPaintList();
}
async function txPaintList(){
 const data=await txLoadIndex(),grid=document.querySelector('#txGrid'),pager=document.querySelector('#txPager'),status=document.querySelector('#txStatus');if(!grid)return;
 let ids=[...data.ids];const q=txQuery.toLowerCase();
 if(q.length>=3){status.textContent='Searching source corpus…';const rows=[];let cursor=0;const workers=Array.from({length:6},async()=>{while(cursor<ids.length){const i=cursor++,id=ids[i],text=await txLoad(id);if(text&&(text.toLowerCase().includes(q)||id.includes(q)))rows.push([i,id])}});await Promise.all(workers);ids=rows.sort((a,b)=>a[0]-b[0]).map(x=>x[1]);}
 const pages=Math.max(1,Math.ceil(ids.length/TX_PER_PAGE));txPage=Math.min(txPage,pages);const shown=ids.slice((txPage-1)*TX_PER_PAGE,txPage*TX_PER_PAGE);
 grid.innerHTML=shown.map((id,i)=>`<button class="transmission-card" data-id="${id}"><div class="tx-num">Transmission ${(txPage-1)*TX_PER_PAGE+i+1}</div><h3>Loading source heading…</h3><p>Retrieving preserved transmission text.</p><div class="tx-id">${id}</div></button>`).join('')||`<div class="tx-missing">No preserved transmissions matched this search.</div>`;
 grid.querySelectorAll('.transmission-card').forEach(card=>{card.onclick=()=>location.hash=`#transmission:${card.dataset.id}`;txHydrateCard(card)});
 status.textContent=`${ids.length} matching correspondence record${ids.length===1?'':'s'} · page ${txPage}/${pages}`;
 pager.innerHTML=`<button ${txPage<=1?'disabled':''} id="txPrev">← Previous</button><span>${txPage} / ${pages}</span><button ${txPage>=pages?'disabled':''} id="txNext">Next →</button>`;
 document.querySelector('#txPrev')?.addEventListener('click',()=>{if(txPage>1){txPage--;txPaintList();window.scrollTo({top:0,behavior:'smooth'})}});document.querySelector('#txNext')?.addEventListener('click',()=>{if(txPage<pages){txPage++;txPaintList();window.scrollTo({top:0,behavior:'smooth'})}});
}
async function txHydrateCard(card){const id=card.dataset.id,text=await txLoad(id);if(!card.isConnected)return;const h=card.querySelector('h3'),p=card.querySelector('p');if(text){h.textContent=txFirstLine(text);p.textContent=txExcerpt(text)||'Verbatim source transmission.'}else{h.textContent='Correspondence record';p.textContent='Indexed provenance record; source text is not yet present in the publication package.';card.classList.add('source-pending')}}
async function renderTransmission(id){
 txSetCrumb('Zubaida Transmission');const main=txShell();main.innerHTML=`<div class="tx-reader"><button class="tx-back" id="txBack">← Story & Thread Archive</button><div class="tx-missing" style="margin-top:18px">Loading preserved source…</div></div>`;document.querySelector('#txBack').onclick=()=>location.hash='#stories';
 const [text,att]=await Promise.all([txLoad(id),txLoadAttachments()]);if(txRoute()!==`transmission:${id}`)return;
 if(!text){main.innerHTML=`<div class="tx-reader"><button class="tx-back" onclick="location.hash='#stories'">← Story & Thread Archive</button><div class="tx-missing" style="margin-top:18px"><b>Indexed source record:</b> ${txEsc(id)}<br><br>The correspondence index retains this message ID, but its public source-text file is not present yet.</div></div>`;return}
 const title=txFirstLine(text),files=att?.[id]||[];main.innerHTML=`<div class="tx-reader"><div class="tx-reader-head"><button class="tx-back" id="txBack2">← Story & Thread Archive</button><div class="eyebrow" style="margin-top:22px">Zubaida transmission · verbatim source layer</div><h1>${txEsc(title)}</h1><div class="tx-provenance"><span>Gmail source ID ${txEsc(id)}</span><span>quoted reply-chain removed</span><span>source wording retained</span></div></div><div class="tx-note">The source below is kept separate from Codex explanation. Crossreferential explanation may be added around it, but this panel is the preservation layer.</div><pre class="tx-source">${txEsc(text)}</pre>${files.length?`<section class="tx-attachments"><h2>Original attachments</h2>${files.map(f=>`<a class="tx-source-link" href="${txEsc(f.path)}" target="_blank" rel="noopener">${txEsc(f.name)}</a>`).join('')}</section>`:''}</div>`;document.querySelector('#txBack2').onclick=()=>location.hash='#stories';
}
async function txHandle(){const h=txRoute();if(h==='stories')return renderStories();if(h.startsWith('transmission:'))return renderTransmission(h.slice('transmission:'.length))}
window.addEventListener('hashchange',e=>{const h=txRoute();if(h==='stories'||h.startsWith('transmission:')){e.stopImmediatePropagation();txHandle().catch(err=>{console.error(err);txShell().innerHTML=`<div class="card"><h3>Archive rendering error</h3><p>${txEsc(err.message)}</p></div>`})}},true);
if(txRoute()==='stories'||txRoute().startsWith('transmission:'))[0,120,500,950].forEach(ms=>setTimeout(()=>{if(txRoute()==='stories'||txRoute().startsWith('transmission:'))txHandle()},ms));
})();
