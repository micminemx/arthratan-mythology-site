import json, re, unicodedata, pathlib, collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/'data'

def load(n): return json.load(open(D/n,encoding='utf-8'))
def norm(s):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(s or '')).replace('’',"'")).strip()
def snippet(s,n=200):
    s=norm(s); return s if len(s)<=n else s[:n].rsplit(' ',1)[0]+'…'
def tokens(s):
    return re.findall(r"[\w’'-]+", unicodedata.normalize('NFKC',s).lower())
def keyword_terms(*parts, limit=30):
    stop={'the','and','for','with','from','that','this','into','their','they','are','was','were','have','has','had','not','but','all','its','his','her','our','you','your','within','through','while','where','which','when','what','than','then','been','being','also','each','every','only','more','most','can','could','would','should','will','may','might','does','did','such','any','one','two','three','four','page','section','source','canon'}
    c=collections.Counter()
    for p in parts:
      for t in tokens(norm(p)):
       if len(t)>=3 and t not in stop and not t.isdigit(): c[t]+=1
    return [w for w,_ in c.most_common(limit)]

records=[]
def add(**r):
    r['title']=norm(r.get('title'))
    r['aliases']=[norm(x) for x in r.get('aliases',[]) if norm(x)]
    r['snippet']=snippet(r.get('snippet',''))
    r['keywords']=list(dict.fromkeys([norm(x).lower() for x in r.get('keywords',[]) if norm(x)]))[:100]
    r.pop('provenance',None)
    records.append(r)

chars=load('characters.json')['characters']
for c in chars:
    body=' '.join(sum([c.get(k,[]) if isinstance(c.get(k),list) else [c.get(k,'')] for k in ['summary','role','classification','titles','aliases','species','sex','clan','allegiance','family','status','appearance','personality','abilities','equipment','feats','history','relationships','records','arcs','gaps','canon_notes']],[]))
    add(id='character:'+c['slug'], type='character', title=c['name'], aliases=c.get('aliases',[])+c.get('titles',[]), route=f"/characters/{c['slug']}/", source_id=c['slug'], source_path='/data/characters.json', snippet=c.get('summary') or body, keywords=keyword_terms(c['name'],body))

for s in load('divine.json')['sections']:
    text=[]
    for b in s.get('blocks',[]):
      if b.get('type')=='p': text.append(b.get('text',''))
      elif b.get('type')=='table':
       for row in b.get('rows',[]):
        for cell in row: text.append(cell.get('t','') if isinstance(cell,dict) else str(cell))
    full=' '.join(text)
    add(id='divine:'+s['id'], type='divine', title=s['title'], aliases=[], route=f"/divine/{s['order']+1:03d}/", source_id=s['id'], source_path='/data/divine.json', snippet=full, keywords=keyword_terms(s['title'],full))

for pg in load('hgl-pages.json')['pages']:
    text=pg['text']; lines=[norm(x) for x in text.splitlines() if norm(x)]
    add(id=f"hgl:{pg['page']}", type='hgl', title=f"Hypergendered Logic — page {pg['page']}", aliases=[], route=f"/hgl/{pg['page']:03d}/", source_id=str(pg['page']), source_path='/data/hgl-pages.json', snippet=' '.join(lines[:8]), keywords=keyword_terms(text))

zi=load('zubaida-index.json'); srcdir=ROOT/'sources'/'zubaida'; existing={p.stem for p in srcdir.glob('*.txt')}; source_ids=[x for x in zi['ids'] if x in existing]
assert len(source_ids)==118, len(source_ids)
for pos,id_ in enumerate(source_ids,1):
    raw=(srcdir/f'{id_}.txt').read_text(encoding='utf-8',errors='replace'); lines=[norm(x) for x in raw.splitlines() if norm(x)]
    heading=next((x for x in lines if re.match(r'(?i)^(session|transmission|imperial transmission|arthratan|the )',x)), lines[0] if lines else id_)
    if heading.startswith('From:'): heading=next((x for x in lines if x.lower().startswith('session')), f'Zubaida transmission {pos}')
    add(id='zubaida:'+id_, type='zubaida', title=heading[:240], aliases=[], route=f"/zubaida/{id_}/", source_id=id_, source_path=f"/sources/zubaida/{id_}.txt", snippet=raw, keywords=keyword_terms(heading,raw,limit=35))

for s in load('new-canon.json').get('sections',[]):
    body=' '.join(s.get('body',[])); route={'negative-rewrite':'/#negative-rewrite','arthitean-states':'/#arthiteans','metagovernance':'/#scaling'}.get(s['id'],'/#scaling')
    add(id='living:'+s['id'], type='living-canon', title=s['title'], aliases=[], route=route, source_id=s['id'], source_path='/data/new-canon.json', snippet=body, keywords=keyword_terms(s['title'],s.get('kicker',''),body))

for c in load('causal-ontology.json').get('concepts',[]):
    body=' '.join(c.get('canon',[])+c.get('formal',[])+[c.get('summary',''),c.get('clarification','')]); route='/#negative-rewrite' if 'rewrite' in c['id'] else '/#scaling'
    add(id='concept:'+c['id'], type='concept', title=c['title'], aliases=[], route=route, source_id=c['id'], source_path='/data/causal-ontology.json', snippet=c.get('summary') or body, keywords=keyword_terms(c['title'],body))

hg=load('hgl-glossary.json')
for e in hg.get('entries',[]):
    body=' '.join([e.get('term',''),e.get('label',''),e.get('signature',''),e.get('definition','')]+e.get('typed_forms',[]))
    add(id='hgl-glossary:'+e['id'], type='concept', title=f"{e['term']} — {e.get('label','HGL glossary')}", aliases=[e.get('term','')], route='/hgl/', source_id=e['id'], source_path='/data/hgl-glossary.json', snippet=e.get('definition',''), keywords=keyword_terms(body))

for id_,title,route,path,snip in [('sources:zubaida','Zubaida source archive','/zubaida/','/data/zubaida-index.json','118 source-bearing Zubaida transmissions, each preserved once with exact source text and provenance.'),('sources:divine','Divine v144 source archive','/divine/','/data/divine.json','317 preserved Divine v144 structured source sections, including all source tables.'),('sources:hgl','Hypergendered Logic source archive','/hgl/','/data/hgl-pages.json','293 preserved HGL source pages with a separate structured TOC and explanatory layers.'),('sources:characters','Character encyclopedia','/characters/','/data/characters.json','Structured Arthratan mythology character encyclopedia with aliases, titles, abilities, relationships and source threads.')]:
    add(id=id_,type='provenance',title=title,aliases=[],route=route,source_id=id_,source_path=path,snippet=snip,keywords=keyword_terms(title,snip))

priority={'character':100,'concept':90,'living-canon':80,'zubaida':70,'divine':60,'hgl':50,'provenance':40}
for r in records: r['rank_priority']=priority.get(r['type'],10)
records.sort(key=lambda r:(-r['rank_priority'],r['title'].lower(),r['id']))
counts=collections.Counter(r['type'] for r in records)
meta={'version':1,'task':'SEARCH-001','generated_from_commit':'e1010e9cde4d476cc4367c1028d46625f3a1fe79','source_rule':'Discovery index only. Search snippets/keywords never replace source canon; follow route/source_path for canonical material.','normalization':'Unicode NFKC; whitespace collapsed; keywords lowercase token-frequency ranking.','records':len(records),'counts':dict(sorted(counts.items())),'coverage':{'characters':len(chars),'zubaida_source_transmissions':len(source_ids),'divine_sections':len(load('divine.json')['sections']),'hgl_pages':len(load('hgl-pages.json')['pages']),'living_canon_sections':len(load('new-canon.json').get('sections',[])),'causal_concepts':len(load('causal-ontology.json').get('concepts',[])),'hgl_glossary_entries':len(hg.get('entries',[]))},'validation':{'unique_ids':len({r['id'] for r in records})==len(records),'routes_present':all(r['route'] for r in records),'source_paths_present':all(r['source_path'] for r in records),'source_files_modified':False}}
shard_specs=[('characters',{'character'}),('zubaida',{'zubaida'}),('divine',{'divine'}),('hgl',{'hgl'}),('concepts-living',{'concept','living-canon','provenance'})]
shards=[]
for name,types in shard_specs:
    rs=[r for r in records if r['type'] in types]; path=f'data/search-index-{name}.json'; (ROOT/path).write_text(json.dumps({'version':1,'types':sorted(types),'records':rs},ensure_ascii=False,separators=(',',':')),encoding='utf-8'); shards.append({'name':name,'path':'/'+path,'types':sorted(types),'records':len(rs)})
meta['shards']=shards
manifest={'meta':meta,'shards':shards,'record_schema':['id','type','title','aliases','route','source_id','source_path','snippet','keywords','rank_priority']}
(D/'search-index.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(D/'search-index-meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(meta,indent=2))
