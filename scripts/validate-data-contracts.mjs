#!/usr/bin/env node
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const dataRoot = path.join(root, "data");
const docs = new Map();
const errors = [];
const warnings = [];
const A = (v) => Array.isArray(v) ? v : [];
const O = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const task = (d) => d?.task_id ?? d?.task ?? "unscoped";
const idNum = (s, prefix) => typeof s === "string" && s.startsWith(prefix) && /^\d+$/.test(s.slice(prefix.length))
  ? Number(s.slice(prefix.length)) : null;
const between = (n, a, b) => Number.isInteger(n) && n >= a && n <= b;
const norm = (s) => String(s).normalize("NFKC").trim().toLowerCase().replace(/\s+/g, " ");

function report(bucket, file, record, message) {
  bucket.push({ file, record: record || "-", task: task(docs.get(file)), message });
}
const fail = (f, r, m) => report(errors, f, r, m);
const warn = (f, r, m) => report(warnings, f, r, m);

async function walk(dir) {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...await walk(full));
    else if (entry.isFile() && entry.name.endsWith(".json")) out.push(full);
  }
  return out;
}

async function load() {
  let files;
  try { files = await walk(dataRoot); }
  catch (x) { console.error(`::error file=data/::cannot enumerate data JSON: ${x.message}`); process.exit(1); }
  for (const full of files.sort()) {
    const file = path.relative(root, full).replaceAll(path.sep, "/");
    try { docs.set(file, JSON.parse(await readFile(full, "utf8"))); }
    catch (x) { errors.push({ file, record: "-", task: "parse", message: `invalid JSON: ${x.message}` }); }
  }
}

function need(file) {
  const d = docs.get(file);
  if (!d) fail(file, "-", "required dataset missing or unparsable");
  return d;
}
function pointer(owner, record, p) {
  if (typeof p !== "string" || !p) fail(owner, record, "source pointer must be a non-empty path");
  else if (!docs.has(p)) fail(owner, record, `source pointer does not resolve: ${p}`);
}
function uniqueStrings(file, record, values) {
  const set = new Set();
  for (const [i, value] of A(values).entries()) {
    if (typeof value !== "string" || !value.trim()) fail(file, `${record}[${i}]`, "must be a non-empty string");
    else if (set.has(value)) fail(file, `${record}[${i}]`, `duplicate value: ${value}`);
    else set.add(value);
  }
  return set;
}

function zubaidaBase() {
  const fi = "data/zubaida-index.json", fn = "data/zubaida-nonsource.json";
  const index = need(fi), non = need(fn);
  if (!index || !non) return null;
  const all = uniqueStrings(fi, "ids", index.ids);
  const excluded = new Set();
  for (const [i, row] of A(non.ids).entries()) {
    if (!O(row) || typeof row.id !== "string" || !row.id) { fail(fn, `ids[${i}]`, "exclusion requires id"); continue; }
    if (excluded.has(row.id)) fail(fn, `ids[${i}]`, `duplicate exclusion: ${row.id}`);
    excluded.add(row.id);
    if (!all.has(row.id)) fail(fn, `ids[${i}]`, `excluded id absent from index: ${row.id}`);
    if (typeof row.classification !== "string" || !row.classification.trim()) fail(fn, `ids[${i}]`, "classification required");
  }
  const source = new Set([...all].filter((x) => !excluded.has(x)));
  const audit = index.audit ?? {};
  if (audit.sender_messages !== all.size) fail(fi, "audit.sender_messages", `${audit.sender_messages} != indexed ${all.size}`);
  if (audit.source_bearing_transmissions !== source.size) fail(fi, "audit.source_bearing_transmissions", `${audit.source_bearing_transmissions} != derived ${source.size}`);
  return { all, excluded, source };
}

const rels = new Set(["defines","expands","applies","corrects","supersedes","example-of","prerequisite-for","contrasts-with","related-to","explicit-possessor","example-subject"]);

function zubaidaCrossrefs(base) {
  const f = "data/zubaida-crossrefs.json", d = docs.get(f);
  if (!d) return;
  const concepts = uniqueStrings(f, "concepts", d.concepts);
  const map = new Map();
  if (!O(d.rel)) fail(f, "rel", "relationship map must be an object");
  for (const [code, name] of Object.entries(d.rel ?? {})) {
    if (!rels.has(name)) fail(f, `rel.${code}`, `unsupported relationship: ${name}`);
    map.set(code, name);
  }
  if (!Array.isArray(d.coverage) || d.coverage.length < 7 || d.coverage.some((n) => !Number.isInteger(n) || n < 0)) fail(f, "coverage", "expected >=7 non-negative integer fields");
  const rows = typeof d.edges === "string" && d.edges ? d.edges.split(";").filter(Boolean) : [];
  const seenSources = new Set();
  for (const [i, row] of rows.entries()) {
    const p = row.split(".");
    if (p.length !== 6) { fail(f, `edges[${i}]`, `expected 6 encoded fields, got ${p.length}`); continue; }
    const [s36, c36, rc, para36, start36, end36] = p;
    const nums = [s36,c36,para36,start36,end36].map((x) => Number.parseInt(x, 36));
    if (!nums.every(Number.isInteger)) { fail(f, `edges[${i}]`, "invalid base36 numeric field"); continue; }
    const [s,c,para,start,end] = nums;
    if (base && !between(s,0,base.source.size-1)) fail(f, `edges[${i}]`, `source index ${s} outside corpus`);
    if (!between(c,0,concepts.size-1)) fail(f, `edges[${i}]`, `concept index ${c} outside registry`);
    if (!map.has(rc)) fail(f, `edges[${i}]`, `unknown relationship code ${rc}`);
    if (para < 0 || start < 0 || end < start) fail(f, `edges[${i}]`, "invalid paragraph/character locator");
    seenSources.add(s);
  }
  if (Array.isArray(d.coverage)) {
    if (base && d.coverage[0] !== base.source.size) fail(f, "coverage[0]", `${d.coverage[0]} != source corpus ${base.source.size}`);
    if (d.coverage[4] !== rows.length) fail(f, "coverage[4]", `${d.coverage[4]} != encoded edges ${rows.length}`);
    if (d.coverage[5] !== concepts.size) fail(f, "coverage[5]", `${d.coverage[5]} != concepts ${concepts.size}`);
    if (d.coverage[3] > d.coverage[0] || seenSources.size > d.coverage[3]) fail(f, "coverage[3]", "reviewed-source coverage is inconsistent");
  }
}

function zubaidaCharacters(base) {
  const f = "data/zubaida-character-links.json", d = docs.get(f);
  if (!d) return;
  for (const k of ["reviewed","expected","remaining"]) if (!Number.isInteger(d[k]) || d[k] < 0) fail(f,k,"must be non-negative integer");
  if (Number.isInteger(d.reviewed) && Number.isInteger(d.remaining) && d.reviewed + d.remaining !== d.expected) fail(f,"coverage","reviewed + remaining != expected");
  if (base && Number.isInteger(d.expected) && d.expected !== base.source.size) fail(f,"expected",`${d.expected} != source corpus ${base.source.size}`);
  if (["complete","finished"].includes(d.status) && d.remaining !== 0) fail(f,"status",`${d.status} requires remaining=0`);
  if (!O(d.entity)) fail(f,"entity","entity registry must be object");
  const alias = new Map();
  for (const [key,e] of Object.entries(d.entity ?? {})) {
    if (!/^[a-z0-9][a-z0-9-]*$/.test(key)) fail(f,`entity.${key}`,"unstable entity key syntax");
    if (!O(e) || typeof e.n !== "string" || !e.n.trim() || typeof e.k !== "string" || !e.k.trim()) fail(f,`entity.${key}`,"entity requires n/name and k/kind");
    for (const a of [e?.n,...A(e?.a)].filter((x)=>typeof x==="string"&&x.trim())) {
      const n = norm(a); if (!alias.has(n)) alias.set(n,new Set()); alias.get(n).add(key);
    }
  }
  for (const [a,owners] of alias) if (owners.size > 1) warn(f,`alias:${a}`,`duplicate normalized alias maps to: ${[...owners].join(", ")}`);
  if (!O(d.tx)) fail(f,"tx","transmission map must be object");
  const tx = Object.entries(d.tx ?? {});
  if (Number.isInteger(d.reviewed) && tx.length !== d.reviewed) fail(f,"reviewed",`${d.reviewed} != transmission records ${tx.length}`);
  for (const [id,row] of tx) {
    if (base && !base.source.has(id)) fail(f,`tx.${id}`,"not a source-bearing transmission");
    if (!O(row)) { fail(f,`tx.${id}`,"record must be object"); continue; }
    if (row.sha !== undefined && (typeof row.sha !== "string" || !/^[0-9a-f]{40}$/i.test(row.sha))) fail(f,`tx.${id}.sha`,"invalid Git SHA");
    for (const [i,k] of A(row.e).entries()) if (!d.entity?.[k]) fail(f,`tx.${id}.e[${i}]`,`unknown entity target: ${k}`);
  }
}

function divineCore() {
  const f="data/divine.json", d=need(f);
  if (!d || !Array.isArray(d.sections)) { if (d) fail(f,"sections","must be array"); return null; }
  const ids=new Set(), numbered=new Set();
  for (const [i,s] of d.sections.entries()) {
    if (!O(s) || typeof s.id!=="string" || !s.id) { fail(f,`sections[${i}]`,"section requires id"); continue; }
    if (ids.has(s.id)) fail(f,`sections[${i}]`,`duplicate section id: ${s.id}`); ids.add(s.id);
    const n=idNum(s.id,"divine-"); if (n!==null) numbered.add(n);
  }
  for (const s of d.sections) {
    if (s?.parent_id && !ids.has(s.parent_id)) fail(f,s.id,`orphan parent ${s.parent_id}`);
    for (const c of A(s?.children)) if (!ids.has(c)) fail(f,s.id,`orphan child ${c}`);
  }
  const manifest=docs.get("data/manifest.json")?.stats?.divine_sections;
  if (Number.isInteger(manifest) && d.sections.length!==manifest) fail(f,"sections",`${d.sections.length} != manifest divine_sections ${manifest}`);
  const max=numbered.size?Math.max(...numbered):0;
  for(let n=1;n<=max;n++) if(!numbered.has(n)) fail(f,`divine-${n}`,"missing numbered section");
  return {ids,max};
}

function divineExp(divine) {
  for (const [f,d] of docs) {
    if (!/^data\/divine-explanations-\d{3}-\d{3}\.json$/.test(f)) continue;
    if (!O(d.source)) fail(f,"source","source contract required");
    else { pointer(f,"source.dataset",d.source.dataset); if(d.source.immutable!==true) fail(f,"source.immutable","must be true"); }
    const c=d.coverage??{}, target=c.target_sections, done=c.completed_sections;
    if (!Number.isInteger(target)||target<=0||!Number.isInteger(done)||done<0||done>target) fail(f,"coverage","invalid target/completed counts");
    if (!Array.isArray(d.sections)) fail(f,"sections","must be array");
    if (Number.isInteger(done)&&A(d.sections).length!==done) fail(f,"coverage.completed_sections",`${done} != records ${A(d.sections).length}`);
    if (["complete","finished"].includes(c.status??d.status)&&done!==target) fail(f,"coverage.status","complete status requires target coverage");
    const r=A(d.source?.source_id_range), a=idNum(r[0],"divine-"), b=idNum(r[1],"divine-");
    if (r.length===2 && (!Number.isInteger(a)||!Number.isInteger(b)||a>b)) fail(f,"source.source_id_range","invalid batch range");
    if (r.length===2 && Number.isInteger(target) && Number.isInteger(a)&&Number.isInteger(b)&&b-a+1!==target) fail(f,"coverage.target_sections","does not match batch range");
    const vocab=new Set(A(d.relationship_vocabulary));
    const seen=new Set();
    for (const [i,s] of A(d.sections).entries()) {
      const rec=s?.section_id??`sections[${i}]`;
      if(!O(s)||typeof s.section_id!=="string"){fail(f,rec,"section_id required");continue;}
      if(seen.has(s.section_id))fail(f,rec,"duplicate section_id");seen.add(s.section_id);
      if(divine&&!divine.ids.has(s.section_id))fail(f,rec,"section locator absent from data/divine.json");
      const n=idNum(s.section_id,"divine-");
      if(Number.isInteger(a)&&Number.isInteger(b)&&!between(n,a,b))fail(f,rec,"section outside owned range");
      if(Number.isInteger(s.source_order)&&Number.isInteger(n)&&s.source_order!==n)fail(f,rec,"source_order does not match section id");
      for(const x of [...A(s.prerequisites),...A(s.related_sections)])if(typeof x!=="string"||(divine&&!divine.ids.has(x)))fail(f,rec,`invalid Divine locator: ${x}`);
      for(const [j,l] of A(s.concept_links).entries()){
        if(!O(l)||typeof l.label!=="string"||!l.label.trim())fail(f,`${rec}.concept_links[${j}]`,"label required");
        if(!O(l)||typeof l.relationship!=="string"||(vocab.size&&!vocab.has(l.relationship)))fail(f,`${rec}.concept_links[${j}]`,"relationship absent from vocabulary");
        if(O(l?.target)){if(l.target.dataset)pointer(f,`${rec}.target.dataset`,l.target.dataset);if(l.target.section_id&&divine&&!divine.ids.has(l.target.section_id))fail(f,rec,`invalid target ${l.target.section_id}`);}
      }
      for(const [j,l] of A(s.character_links).entries())if(!O(l)||typeof l.label!=="string"||!l.label.trim()||(l.relationship&&vocab.size&&!vocab.has(l.relationship)))fail(f,`${rec}.character_links[${j}]`,"invalid character link");
    }
  }
}

function hglCore() {
  const fp="data/hgl-pages.json", ft="data/hgl-toc.json", p=need(fp), t=need(ft);
  const pageSet=new Set(), tocSet=new Set(), stats=docs.get("data/manifest.json")?.stats??{};
  for(const [i,x] of A(p?.pages).entries()){
    if(!Number.isInteger(x?.page)||x.page<1)fail(fp,`pages[${i}]`,"invalid page");
    else if(pageSet.has(x.page))fail(fp,`pages[${i}]`,`duplicate page ${x.page}`);else pageSet.add(x.page);
  }
  const expectedPages=Number.isInteger(stats.hgl_pages)?stats.hgl_pages:293;
  if(pageSet.size!==expectedPages)fail(fp,"pages",`${pageSet.size} != expected ${expectedPages}`);
  for(let n=1;n<=expectedPages;n++)if(!pageSet.has(n))fail(fp,`page:${n}`,"missing page");
  for(const [i,x] of A(t?.toc).entries()){
    if(typeof x?.id!=="string"||!x.id)fail(ft,`toc[${i}]`,"id required");
    else if(tocSet.has(x.id))fail(ft,`toc[${i}]`,`duplicate id ${x.id}`);else tocSet.add(x.id);
    if(!between(x?.page,1,expectedPages))fail(ft,`toc[${i}]`,`invalid page locator ${x?.page}`);
  }
  const expectedToc=Number.isInteger(stats.hgl_toc_entries)?stats.hgl_toc_entries:1037;
  if(tocSet.size!==expectedToc)fail(ft,"toc",`${tocSet.size} != expected ${expectedToc}`);
  return {pages:expectedPages,parts:Number.isInteger(stats.hgl_major_parts)?stats.hgl_major_parts:95};
}
function hpart(p){
  const n=p?.major_part_number??p?.n,id=p?.source_part_id??p?.id;
  const range=O(p?.source_page_range)?[p.source_page_range.start,p.source_page_range.end]:A(p?.pages);
  return {n,id,start:range[0],end:range[1]};
}
function hglExp(core) {
  for(const [f,d] of docs){
    if(!/^data\/hgl-explanations-parts-\d{3}-\d{3}\.json$/.test(f))continue;
    const rr=d.owned_major_part_range??d.owned,r=Array.isArray(rr)?{start:rr[0],end:rr[1]}:rr,maxParts=core?.parts??95;
    if(!O(r)||!between(r.start,1,maxParts)||!between(r.end,1,maxParts)||r.start>r.end){fail(f,"owned_major_part_range","invalid range");continue;}
    const width=r.end-r.start+1,s=d.source_contract??d.source??{};
    const toc=s.toc_source??s.toc,pages=s.page_source??s.pages,count=s.source_page_count??s.source_pages??s.count,immutable=s.source_is_immutable??s.source_immutable??s.immutable,separate=s.explanation_layer_only??s.explanations_separate??s.explanation_only;
    pointer(f,"source_contract.toc",toc);pointer(f,"source_contract.pages",pages);
    if(count!==(core?.pages??293))fail(f,"source_contract.source_pages",`${count} != ${core?.pages??293}`);
    if(immutable!==true||separate!==true)fail(f,"source_contract","source must be immutable and explanations separate");
    const c=d.coverage??{},done=A(c.completed_major_parts??c.completed??c.done),remaining=A(c.remaining_major_parts??c.remaining),dc=c.completed_major_part_count??c.count,oc=c.owned_major_part_count??c.owned;
    if(dc!==done.length||oc!==width)fail(f,"coverage","declared counts do not match lists/range");
    const D=new Set(done),R=new Set(remaining);
    if(D.size!==done.length||R.size!==remaining.length)fail(f,"coverage","duplicate completed/remaining part");
    for(const n of D)if(!between(n,r.start,r.end))fail(f,"coverage.completed",`part ${n} outside range`);
    for(const n of R)if(!between(n,r.start,r.end)||D.has(n))fail(f,"coverage.remaining",`invalid/overlapping part ${n}`);
    if(D.size+R.size!==width)fail(f,"coverage","completed + remaining does not cover owned range");
    if(["complete","finished","complete_pending_verification"].includes(d.status)&&R.size)fail(f,"status","complete status has remaining parts");
    if(A(d.parts).length!==D.size)fail(f,"parts",`${A(d.parts).length} records != completed ${D.size}`);
    const seenN=new Set(),seenId=new Set();
    for(const [i,p] of A(d.parts).entries()){
      const x=hpart(p),rec=x.id??`parts[${i}]`;
      if(!between(x.n,r.start,r.end)||seenN.has(x.n)||!D.has(x.n))fail(f,rec,"invalid/duplicate/uncovered major-part number");seenN.add(x.n);
      if(typeof x.id!=="string"||!/^hgl-part-\d+$/.test(x.id))fail(f,rec,`invalid part id ${x.id}`);
      else{if(seenId.has(x.id))fail(f,rec,"duplicate part id");seenId.add(x.id);if(idNum(x.id,"hgl-part-")!==x.n-1)fail(f,rec,"part id does not match major-part number");}
      if(!between(x.start,1,core?.pages??293)||!between(x.end,1,core?.pages??293)||x.start>x.end)fail(f,rec,`invalid page range ${x.start}..${x.end}`);
      const links=Array.isArray(p?.crosslinks)?p.crosslinks:(p?.crosslink?[p.crosslink]:(p?.link!==undefined?[p.link]:[]));
      for(const [j,l] of links.entries()){
        if(Number.isInteger(l)){if(!between(l,1,maxParts))fail(f,`${rec}.crosslinks[${j}]`,`invalid major-part link ${l}`);continue;}
        const target=typeof l==="string"?l:l?.target,n=idNum(target,"hgl-part-");
        if(!between(n,0,maxParts-1))fail(f,`${rec}.crosslinks[${j}]`,`invalid target ${target}`);
      }
    }
  }
}

function generic() {
  for(const [f,d] of docs){
    if((f.includes("explanations-")||f.includes("crossrefs")||f.includes("character-links"))&&!(d?.task||d?.task_id))fail(f,"-","generated dataset lacks task provenance");
    for(const [k,v] of Object.entries(O(d)?d:{})){
      if(!Array.isArray(v)||!v.length||!v.every(O)||!v.some((x)=>Object.hasOwn(x,"id")))continue;
      const seen=new Set();for(const [i,x] of v.entries()){if(x.id===undefined)continue;if(typeof x.id!=="string"||!x.id.trim())fail(f,`${k}[${i}].id`,"stable id required");else if(seen.has(x.id))fail(f,`${k}[${i}].id`,`duplicate id ${x.id}`);else seen.add(x.id);}
    }
  }
}
function output(){
  for(const x of warnings)console.warn(`::warning file=${x.file}::${x.task} ${x.record} — ${x.message}`);
  for(const x of errors)console.error(`::error file=${x.file}::${x.task} ${x.record} — ${x.message}`);
  console.log(`QA-006 data-contract validation: ${docs.size} JSON files; ${errors.length} error(s); ${warnings.length} warning(s).`);
}

await load();
if(!errors.some((x)=>x.task==="parse")){
  const z=zubaidaBase();zubaidaCrossrefs(z);zubaidaCharacters(z);
  const d=divineCore();divineExp(d);
  const h=hglCore();hglExp(h);
  generic();
}
output();
if(errors.length)process.exit(1);
