import html
import json
import pathlib
import re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'search'
OUT.mkdir(exist_ok=True)


def esc(value):
    return html.escape(str(value or ''), quote=True)


def slug(value):
    value = re.sub(r'[^a-zA-Z0-9]+', '-', str(value)).strip('-').lower()
    return value[:100] or 'record'


manifest = json.load(open(DATA / 'search-index.json', encoding='utf-8'))
records = []
for shard in manifest['shards']:
    payload = json.load(open(ROOT / shard['path'].lstrip('/'), encoding='utf-8'))
    records.extend(payload['records'])

records.sort(key=lambda r: (-int(r.get('rank_priority', 0)), r.get('title', '').casefold(), r.get('id', '')))
counts = Counter(r['type'] for r in records)
assert len(records) == manifest['meta']['records']
assert len({r['id'] for r in records}) == len(records)

cards = []
for i, r in enumerate(records, 1):
    aliases = [a for a in r.get('aliases', []) if a]
    alias_html = ''
    if aliases:
        alias_html = '<p class="aliases"><strong>Aliases / titles:</strong> ' + esc(' · '.join(aliases)) + '</p>'
    canon_status = r.get('canon_status', 'unspecified')
    search_blob = ' '.join([
        r.get('title', ''),
        ' '.join(aliases),
        r.get('snippet', ''),
        ' '.join(r.get('keywords', [])),
        r.get('source_id', ''),
        r.get('type', ''),
        canon_status,
    ]).casefold()
    if r.get('type') == 'crossscaling':
        provenance_label = '<strong>NONCANON analytical record.</strong> Use its linked Myth/primary evidence for canonical proof.'
    elif r.get('type') == 'myth':
        provenance_label = '<strong>Canonical narrative realization.</strong> Primary evidence linked from the Myth controls feats and outcomes.'
    else:
        provenance_label = 'Discovery excerpt — not a replacement for source canon.'
    cards.append(f'''<article class="result" id="result-{i}-{slug(r['id'])}" data-type="{esc(r['type'])}" data-search="{esc(search_blob)}">
  <div class="result-meta"><span class="type">{esc(r['type'])}</span><span class="canon-status">{esc(canon_status)}</span><span class="source-id">{esc(r.get('source_id',''))}</span></div>
  <h2><a href="{esc(r['route'])}">{esc(r['title'])}</a></h2>
  {alias_html}
  <p class="snippet">{esc(r.get('snippet',''))}</p>
  <p class="provenance"><span>{provenance_label}</span> <a href="{esc(r.get('source_path',''))}">Indexed record/page</a></p>
</article>''')

options = ['<option value="">All source/entity types</option>']
for typ, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
    options.append(f'<option value="{esc(typ)}">{esc(typ)} ({count})</option>')

count_summary = ' · '.join(f'{esc(k)} {v}' for k, v in sorted(counts.items()))
meta = manifest['meta']

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="index,follow,max-snippet:-1">
<meta name="description" content="Complete crawlable Arthratan Mythology search corpus across characters, Myths, Crossscaling, Zubaida transmissions, Divine v144, Hypergendered Logic, living canon, concepts and provenance. JavaScript is not required.">
<link rel="canonical" href="https://arthratanmythology.com/search/">
<link rel="search" type="application/opensearchdescription+xml" title="Arthitean Codex" href="/search/opensearch.xml">
<title>Search the Arthitean Codex · Arthratan Mythology</title>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"The Arthitean Codex","url":"https://arthratanmythology.com/","potentialAction":{{"@type":"SearchAction","target":"https://arthratanmythology.com/search/?q={{search_term_string}}","query-input":"required name=search_term_string"}}}}</script>
<style>
:root{{--bg:#0b0910;--panel:#15111d;--panel2:#1d1728;--text:#f6f0ff;--muted:#b9abc9;--accent:#d7a6ff;--line:#3a2d48;--link:#f0c7ff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}a{{color:var(--link)}}header,main,footer{{max-width:1180px;margin:auto;padding:20px}}header{{padding-top:32px}}nav{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:30px}}nav a{{text-decoration:none;border:1px solid var(--line);padding:8px 12px;border-radius:999px;background:var(--panel)}}h1{{font-size:clamp(2rem,6vw,4.2rem);line-height:1.05;margin:.2em 0}}.lede{{max-width:850px;color:var(--muted);font-size:1.08rem}}.notice{{border-left:4px solid var(--accent);background:var(--panel);padding:14px 16px;margin:22px 0;border-radius:8px}}.tools{{position:sticky;top:0;z-index:3;background:rgba(11,9,16,.96);backdrop-filter:blur(8px);padding:14px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:minmax(220px,2fr) minmax(180px,1fr);gap:10px}}input,select{{width:100%;font:inherit;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--panel);color:var(--text)}}.status{{grid-column:1/-1;color:var(--muted);font-size:.92rem}}.machine{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 28px}}.result{{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:14px;padding:18px;margin:12px 0;scroll-margin-top:130px}}.result h2{{font-size:1.25rem;margin:5px 0 8px}}.result-meta{{display:flex;gap:8px;flex-wrap:wrap;color:var(--muted);font-size:.78rem;text-transform:uppercase;letter-spacing:.06em}}.type{{color:var(--accent);font-weight:700}}.canon-status{{border:1px solid var(--line);border-radius:999px;padding:0 .4rem}}.aliases,.snippet,.provenance{{margin:.45rem 0}}.aliases,.provenance{{color:var(--muted);font-size:.9rem}}.provenance{{border-top:1px solid var(--line);padding-top:8px}}mark{{background:#f4d35e;color:#130f17;padding:0 .08em;border-radius:.12em}}[hidden]{{display:none!important}}footer{{color:var(--muted);border-top:1px solid var(--line);margin-top:32px}}@media(max-width:650px){{.tools{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header>
<nav aria-label="Codex discovery"><a href="/">Sanctuary</a><a href="/characters/">Characters</a><a href="/myths/">Myths</a><a href="/crossscaling/">Crossscaling</a><a href="/zubaida/">Zubaida</a><a href="/divine/">Divine v144</a><a href="/hgl/">HGL</a><a href="/crawl/">Crawl index</a></nav>
<p class="eyebrow">Cross-source discovery · source-preserving</p>
<h1>Search the Arthitean Codex</h1>
<p class="lede">This page contains the complete unified search corpus in its <strong>initial HTML response</strong>. JavaScript is optional: it only filters and highlights what is already present. AI agents, text browsers and crawlers can read and follow every result without executing scripts. Myth and Crossscaling records carry explicit canon-status labels so analytical constructs cannot silently become canon.</p>
<div class="notice"><strong>{len(records)} searchable records.</strong> {count_summary}. Source snippets are discovery aids; primary canonical evidence remains separately retrievable through each result's route and provenance graph.</div>
<form class="tools" action="/search/" method="get" role="search">
<label><span class="visually-hidden">Search terms</span><input id="q" name="q" type="search" autocomplete="off" placeholder="Try Othrys, Dyvane Redalious, Hypernegative Rewrite, Qintara…"></label>
<label><span class="visually-hidden">Type</span><select id="type" name="type">{''.join(options)}</select></label>
<div class="status" id="status" aria-live="polite">All {len(records)} records are present below.</div>
<noscript><div class="status"><strong>JavaScript is disabled.</strong> All {len(records)} records remain visible; use your browser/agent text-find function. Query parameters do not hide records server-side.</div></noscript>
</form>
<div class="machine"><a href="/search/index.txt">Plain-text machine index</a><a href="/data/search-index.json">JSON manifest</a><a href="/llms.txt">LLM discovery guide</a></div>
</header>
<main id="results" aria-label="Search corpus">
{''.join(cards)}
</main>
<footer>Generated from SEARCH-003 corpus snapshot {esc(meta.get('generated_from_commit','unknown'))}. Search is progressive enhancement: content access never depends on JavaScript.</footer>
<script>
(()=>{{
 const q=document.getElementById('q'), type=document.getElementById('type'), status=document.getElementById('status');
 const cards=[...document.querySelectorAll('.result')];
 const params=new URLSearchParams(location.search);
 q.value=params.get('q')||params.get('s')||'';
 type.value=params.get('type')||'';
 const norm=s=>(s||'').toLocaleLowerCase().normalize('NFKC').trim();
 function clearMarks(root){{for(const m of root.querySelectorAll('mark'))m.replaceWith(document.createTextNode(m.textContent));root.normalize();}}
 function highlightText(root,raw){{
   const needle=norm(raw); if(!needle)return;
   const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
   const nodes=[]; while(walker.nextNode())nodes.push(walker.currentNode);
   for(const node of nodes){{
     const original=node.nodeValue, folded=norm(original); let start=0, hit=folded.indexOf(needle,start);
     if(hit<0)continue;
     const frag=document.createDocumentFragment(); let cursor=0;
     while(hit>=0){{
       frag.append(document.createTextNode(original.slice(cursor,hit)));
       const mark=document.createElement('mark'); mark.textContent=original.slice(hit,hit+raw.length); frag.append(mark);
       cursor=hit+raw.length; hit=folded.indexOf(needle,cursor);
     }}
     frag.append(document.createTextNode(original.slice(cursor))); node.replaceWith(frag);
   }}
 }}
 function apply(){{
   const raw=q.value.trim(), needle=norm(raw), typ=type.value;
   let shown=0;
   for(const card of cards){{
     clearMarks(card);
     const okText=!needle||card.dataset.search.includes(needle), okType=!typ||card.dataset.type===typ;
     card.hidden=!(okText&&okType);
     if(okText&&okType){{shown++;if(needle)for(const el of card.querySelectorAll('h2 a,.aliases,.snippet'))highlightText(el,raw);}}
   }}
   status.textContent=needle||typ?`${{shown}} of ${{cards.length}} records match. All records remain encoded in the initial HTML.`:`All ${{cards.length}} records are present below.`;
   const url=new URL(location.href); needle?url.searchParams.set('q',raw):url.searchParams.delete('q'); typ?url.searchParams.set('type',typ):url.searchParams.delete('type'); url.searchParams.delete('s'); history.replaceState(null,'',url);
 }}
 q.addEventListener('input',apply); type.addEventListener('change',apply); apply();
}})();
</script>
</body>
</html>'''

plain = [
    '# Arthitean Codex unified search index',
    f'# {len(records)} records; JavaScript not required',
    '# Format: title | type | canon_status | route | aliases | source/data path',
    '# Canonical site: https://arthratanmythology.com/',
    '',
]
for r in records:
    plain.append(' | '.join([
        str(r.get('title','')).replace('\n',' '),
        str(r.get('type','')),
        str(r.get('canon_status','')),
        str(r.get('route','')),
        '; '.join(r.get('aliases',[])).replace('\n',' '),
        str(r.get('source_path','')),
    ]))

opensearch = '''<?xml version="1.0" encoding="UTF-8"?>
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
  <ShortName>Arthitean Codex</ShortName>
  <Description>Search Arthratan mythology across the source-preserving Arthitean Codex.</Description>
  <InputEncoding>UTF-8</InputEncoding>
  <Url type="text/html" template="https://arthratanmythology.com/search/?q={searchTerms}"/>
</OpenSearchDescription>
'''

(OUT / 'index.html').write_text(page, encoding='utf-8')
(OUT / 'index.txt').write_text('\n'.join(plain) + '\n', encoding='utf-8')
(OUT / 'opensearch.xml').write_text(opensearch, encoding='utf-8')

assert 'Dyvane Redalious' in page
assert 'href="/characters/dyvane-redalious/"' in page
assert f'All {len(records)} records are present below.' in page
assert 'highlightText' in page and '<mark>' not in page
assert 'NONCANON analytical record.' in page
assert 'canonical-narrative' in page
assert len(plain) == len(records) + 5
print(f'generated static /search/ with {len(records)} initial-HTML records')
