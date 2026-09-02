#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const ORIGIN = 'https://arthratanmythology.com';
const esc = (v='') => String(v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const slug = (v='') => String(v).normalize('NFKD').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'') || 'untitled';
const readJSON = p => JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const write = (rel, body) => { const file=path.join(ROOT,rel); fs.mkdirSync(path.dirname(file),{recursive:true}); fs.writeFileSync(file,body); };
const sourceLink = p => `/${String(p).replace(/^\/+/, '')}`;
const shell = ({title,description,canonical,kind='Reference',body}) => `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="index,follow"><title>${esc(title)}</title><meta name="description" content="${esc(description)}"><link rel="canonical" href="${esc(canonical)}"><style>body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:76rem;margin:auto;padding:2rem;line-height:1.65;background:#0d0d10;color:#f4f0e8}a{color:#d9b35f}nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:2rem}.eyebrow{letter-spacing:.12em;text-transform:uppercase;color:#c7bca7;font-size:.78rem}.source{white-space:pre-wrap;background:#15151a;border:1px solid #3b3428;border-radius:.75rem;padding:1.25rem;overflow:auto}.meta{color:#c7bca7}.notice{border-left:3px solid #d9b35f;padding:.75rem 1rem;background:#15151a}h1{line-height:1.15}</style></head><body><nav><a href="/">Interactive Codex</a><a href="/crawl/">Crawler index</a></nav><main><article><p class="eyebrow">${esc(kind)}</p>${body}</article></main></body></html>`;

const routes=[];
const addRoute=(kind,key,url,source,title)=>routes.push({kind,key,url,source,title});

const zIndex=readJSON('data/zubaida-index.json');
const nonSource=readJSON('data/zubaida-nonsource.json');
const excluded=new Set((nonSource.ids||[]).map(x=>typeof x==='string'?x:x.id));
const sourceIds=(zIndex.ids||zIndex.source_transmissions?.map(x=>x.id)||[]).filter(id=>!excluded.has(id));
if(sourceIds.length!==118) throw new Error(`Expected 118 source-bearing Zubaida IDs; found ${sourceIds.length}`);
const zMeta=readJSON('data/zubaida-metadata.json');
const metaRecords=zMeta.records || zMeta.transmissions || [];
const metaById=new Map(metaRecords.map(r=>[r.transmission_id || r.id,r]));
for(const id of sourceIds){
  const m=metaById.get(id)||{};
  const source=m.source_file || `sources/zubaida/${id}.txt`;
  const text=fs.readFileSync(path.join(ROOT,source),'utf8');
  const heading=m.canonical_display_heading || m.subject || `Zubaida transmission ${id}`;
  const canonical=`${ORIGIN}/zubaida/${id}/`;
  const html=shell({title:`${heading} — Arthratan Mythology`,description:`Verbatim preserved Zubaida source transmission ${id}, with provenance and a link to the interactive Arthratan Mythology archive.`,canonical,kind:'Zubaida source transmission',body:`<h1>${esc(heading)}</h1><p class="meta">Transmission ID: <code>${esc(id)}</code>${m.source_date?.iso?` · ${esc(m.source_date.iso)}`:''}</p><p class="notice"><strong>Source canon.</strong> The text below is the preserved source, not a model-written summary. <a href="/#transmission:${encodeURIComponent(id)}">Open the enhanced interactive reader</a>.</p><h2>Verbatim preserved source</h2><pre class="source">${esc(text)}</pre><p class="meta">Provenance file: <a href="${sourceLink(source)}">${esc(source)}</a></p>`});
  write(`zubaida/${id}/index.html`,html);
  addRoute('zubaida',id,`/zubaida/${id}/`,source,heading);
}

const chars=readJSON('data/characters.json').characters || [];
for(const c of chars){
  const key=c.slug || slug(c.name); const canonical=`${ORIGIN}/characters/${key}/`;
  const sections=[['Aliases',c.aliases],['Titles',c.titles],['Appearance',c.appearance],['Personality',c.personality],['Abilities',c.abilities],['Feats',c.feats],['History',c.history],['Relationships',c.relationships],['Information not yet established',c.gaps]].filter(([,v])=>Array.isArray(v)&&v.length);
  const body=`<h1>${esc(c.name||key)}</h1>${c.classification?`<p class="meta">${esc(c.classification)}</p>`:''}${c.summary?`<p>${esc(c.summary)}</p>`:''}<dl>${[['Role',c.role],['Species / state',c.species],['Sex / gender',c.sex],['Clan',c.clan],['Allegiance',c.allegiance],['Status',c.status]].filter(([,v])=>v).map(([k,v])=>`<dt><strong>${esc(k)}</strong></dt><dd>${esc(v)}</dd>`).join('')}</dl>${sections.map(([k,v])=>`<h2>${esc(k)}</h2><ul>${v.map(x=>`<li>${esc(typeof x==='string'?x:JSON.stringify(x))}</li>`).join('')}</ul>`).join('')}<p class="notice">This crawlable page reflects the structured character dataset. Source canon and provenance remain separately retrievable in the interactive Codex.</p>`;
  write(`characters/${key}/index.html`,shell({title:`${c.name||key} — Arthratan Mythology`,description:c.summary||`Arthratan Mythology character reference for ${c.name||key}.`,canonical,kind:'Character encyclopedia',body}));
  addRoute('character',key,`/characters/${key}/`,'data/characters.json',c.name||key);
}

const divine=readJSON('data/divine.json');
(divine.sections||[]).forEach((s,i)=>{
  const n=i+1,key=String(n).padStart(3,'0'),heading=s.heading||s.title||`Divine v144 section ${n}`,canonical=`${ORIGIN}/divine/${key}/`;
  const paras=(s.paragraphs||[]).map(p=>`<p>${esc(typeof p==='string'?p:(p.text||JSON.stringify(p)))}</p>`).join('');
  const body=`<h1>${esc(heading)}</h1><p class="meta">Divine v144 · section ${n} of ${divine.sections.length}</p><div>${paras}</div><p class="meta">Structured source: <a href="/data/divine.json">data/divine.json</a></p>`;
  write(`divine/${key}/index.html`,shell({title:`${heading} — Divine v144`,description:`Crawlable Divine v144 source section ${n} in the Arthratan Mythology Codex.`,canonical,kind:'Divine v144 source archive',body}));
  addRoute('divine',key,`/divine/${key}/`,'data/divine.json',heading);
});

const hgl=readJSON('data/hgl-pages.json');
(hgl||[]).forEach((p,i)=>{
  const n=p.page||i+1,key=String(n).padStart(3,'0'),canonical=`${ORIGIN}/hgl/${key}/`,heading=`Hypergendered Logic — page ${n}`;
  const body=`<h1>${heading}</h1><p class="meta">Source PDF: ${esc(p.source_pdf||'Hypergendered Logic')}</p><pre class="source">${esc(p.text||'')}</pre><p class="meta">Structured source: <a href="/data/hgl-pages.json">data/hgl-pages.json</a></p>`;
  write(`hgl/${key}/index.html`,shell({title:`${heading} — Arthratan Mythology`,description:`Crawlable preserved Hypergendered Logic source page ${n}.`,canonical,kind:'HGL source archive',body}));
  addRoute('hgl',key,`/hgl/${key}/`,'data/hgl-pages.json',heading);
});

const grouped=routes.reduce((a,r)=>((a[r.kind]??=[]).push(r),a),{});
const indexBody=`<h1>Arthratan Mythology crawlable corpus</h1><p>This static index is provided for search engines, AI retrieval systems, accessibility tools and browsers that do not execute the interactive Codex JavaScript.</p>${Object.entries(grouped).map(([kind,rs])=>`<h2>${esc(kind)} (${rs.length})</h2><ul>${rs.map(r=>`<li><a href="${esc(r.url)}">${esc(r.title)}</a></li>`).join('')}</ul>`).join('')}`;
write('crawl/index.html',shell({title:'Arthratan Mythology — Crawlable Corpus Index',description:'Static, non-JavaScript index of Arthratan Mythology source and reference pages.',canonical:`${ORIGIN}/crawl/`,kind:'Crawler and accessibility index',body:indexBody}));
write('data/static-route-manifest.json',JSON.stringify({generated:new Date().toISOString(),origin:ORIGIN,count:routes.length,routes},null,2)+'\n');
console.log(`Generated ${routes.length} crawlable routes plus /crawl/.`);
