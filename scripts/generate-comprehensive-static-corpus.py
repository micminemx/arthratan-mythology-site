# -*- coding: utf-8 -*-
"""
Comprehensive Static Route Prerenderer & Schema Generator
Generates crawlable, static HTML entrypoints returning direct HTTP 200
for all 907 canonical URLs across the Arthratan Mythology Codex.
"""
import os
import json
import re
import html
import sys

sys.stdout.reconfigure(encoding='utf-8')

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_dir = os.path.join(repo_root, "data")
ORIGIN = "https://arthratanmythology.com"

print(f"Building Comprehensive Static Corpus in {repo_root}...")

def esc(v):
    if v is None:
        return ""
    return html.escape(str(v))

def slug(v):
    return re.sub(r'[^a-z0-9]+', '-', str(v).lower()).strip('-') or 'untitled'

def write_page(rel_path, content):
    full_path = os.path.join(repo_root, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

def make_shell(title, description, canonical_url, kind, body_html, json_ld=None, breadcrumbs=None):
    schema_script = ""
    if json_ld:
        schema_script = f'\n  <script type="application/ld+json">\n{json.dumps(json_ld, indent=2, ensure_ascii=False)}\n  </script>'
        
    bc_links = ""
    if breadcrumbs:
        bc_links = '<nav class="breadcrumbs" aria-label="Breadcrumb">' + ' &rsaquo; '.join([f'<a href="{esc(u)}">{esc(l)}</a>' for l, u in breadcrumbs]) + '</nav>'

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index,follow">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical_url)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical_url)}">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <link rel="stylesheet" href="/styles.css">
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; max-width: 76rem; margin: auto; padding: 2rem; line-height: 1.65; background: #0d0d10; color: #f4f0e8; }}
    a {{ color: #d9b35f; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    nav.top-nav {{ display: flex; gap: 1.25rem; flex-wrap: wrap; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #2a2824; font-size: 0.95rem; }}
    nav.breadcrumbs {{ font-size: 0.85rem; color: #a99f8d; margin-bottom: 1.5rem; }}
    .eyebrow {{ letter-spacing: 0.12em; text-transform: uppercase; color: #c7bca7; font-size: 0.78rem; font-weight: 600; margin-bottom: 0.5rem; }}
    .source {{ white-space: pre-wrap; background: #15151a; border: 1px solid #3b3428; border-radius: 0.75rem; padding: 1.25rem; overflow: auto; font-size: 0.95rem; }}
    .meta {{ color: #a99f8d; font-size: 0.9rem; margin-top: 0.5rem; margin-bottom: 1rem; }}
    .notice {{ border-left: 3px solid #d9b35f; padding: 0.75rem 1rem; background: #15151a; border-radius: 0 0.5rem 0.5rem 0; margin-bottom: 1.5rem; }}
    h1 {{ line-height: 1.2; margin-top: 0.25rem; margin-bottom: 0.75rem; color: #fbf7ee; }}
    h2 {{ color: #e8caa4; margin-top: 2rem; margin-bottom: 0.75rem; border-bottom: 1px solid #22201c; padding-bottom: 0.25rem; }}
    h3 {{ color: #d9b35f; margin-top: 1.25rem; }}
    dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 0.5rem 1.5rem; background: #15151a; padding: 1rem; border-radius: 0.5rem; border: 1px solid #2a2824; }}
    dt {{ font-weight: 600; color: #c7bca7; }}
    dd {{ margin: 0; }}
    ul {{ padding-left: 1.5rem; }}
    li {{ margin-bottom: 0.35rem; }}
  </style>{schema_script}
</head>
<body>
  <nav class="top-nav" aria-label="Main Navigation">
    <a href="/">Interactive Codex</a>
    <a href="/crawl/">Crawler Index</a>
    <a href="/search/">Search Corpus</a>
    <a href="/clans/">Clans</a>
    <a href="/provenance/">Provenance</a>
    <a href="/chronology/">Chronology</a>
  </nav>
  {bc_links}
  <main>
    <article>
      <p class="eyebrow">{esc(kind)}</p>
      {body_html}
    </article>
  </main>
</body>
</html>"""

routes = []
def add_route(kind, key, url, source, title):
    routes.append({"kind": kind, "key": key, "url": url, "source": source, "title": title})

# ==============================================================================
# 1. CHARACTERS (43)
# ==============================================================================
chars_file = os.path.join(data_dir, "characters.json")
with open(chars_file, "r", encoding="utf-8") as f:
    chars = json.load(f).get("characters", [])

for c in chars:
    key = c.get("slug") or slug(c.get("name"))
    canonical = f"{ORIGIN}/characters/{key}/"
    name = c.get("name") or key
    summary = c.get("summary") or f"Canonical dossier for {name} in the Arthratan Mythology Codex."
    
    sections = [
        ("Aliases", c.get("aliases", [])),
        ("Titles", c.get("titles", [])),
        ("Appearance", c.get("appearance", [])),
        ("Personality", c.get("personality", [])),
        ("Abilities", c.get("abilities", [])),
        ("Feats", c.get("feats", [])),
        ("History", c.get("history", [])),
        ("Relationships", c.get("relationships", [])),
        ("Information Not Yet Established", c.get("gaps", []))
    ]
    
    sec_html = ""
    for title, items in sections:
        if items and len(items) > 0:
            sec_html += f"<h2>{esc(title)}</h2><ul>"
            for it in items:
                sec_html += f"<li>{esc(it if isinstance(it, str) else json.dumps(it))}</li>"
            sec_html += "</ul>"
            
    meta_pairs = [
        ("Role", c.get("role")),
        ("Species", c.get("species")),
        ("Clan", c.get("clan")),
        ("Allegiance", c.get("allegiance")),
        ("Status", c.get("status"))
    ]
    dl_html = "<dl>" + "".join([f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in meta_pairs if v]) + "</dl>"
    
    # If Dyvane Redalious, append the complete canonical battle chronicles and grand feats
    dyvane_chronicles_html = ""
    if key == "dyvane-redalious":
        dyvane_chronicles_html = """<h2>Source-Grounded Battle Chronicles & Grand Feats</h2>
<p class="notice"><strong>Epistemic Classification Note:</strong> The four narrative chronicles below represent structured, source-grounded battle syntheses derived directly from preserved canonical transmissions. Unedited, verbatim primary source transmissions remain separately retrievable via the direct provenance file links in each chronicle entry.</p>

<article class="chronicle-card" style="background:#15151a; border:1px solid #3b3428; border-radius:0.75rem; padding:1.5rem; margin-bottom:1.5rem;">
  <h3 style="color:#f5d061; margin-top:0;">Chronicle 1: The Crucible of the Null-Bringer (Duel with Xael-Gath)</h3>
  <p class="meta">Location: Ke'enmon Subdimension ("Galaxies are merely dust beneath boots; Transtime shatters and reforms with every step") · Adversary: Xael-Gath (Veyndarion-spawned Transadversial Opponent) · Provenance: <a href="/sources/zubaida/19fa076eb25a917b.txt">sources/zubaida/19fa076eb25a917b.txt</a></p>
  <p><strong>The Engagement & Superhax Counter:</strong> Xael-Gath initiated combat by bypassing physical distance entirely with high-level reality-warping Hax designed to instantly sever the causal link between Dyvane’s brain and his muscles. Dyvane did not flinch; he deployed an innate Arthitean Superhax: <em>Conceptual Reflection Mastery</em>. Because Superhax produce metaeffects whose direct target is an opponent's effect, Dyvane targeted the production and persistence of Xael-Gath's severance field, instantly invalidating, forcefully inverting, and perfectly reflecting the causal severance back upon the entity itself.</p>
  <p><strong>Physical Clash & Negative-Overcostedness Differential:</strong> Dyvane closed with Divine-Agility and threw a physical punch aimed directly at Xael-Gath’s core. When Xael-Gath attempted to block with an infinite reserve of defensive energy (Hypercapacity), Dyvane applied his Divine-Strength. His transcapacity for Divine-Power generated a mathematically impossible overcostedness differential, forcing a massive negative differential upon the entity. Xael-Gath was bankrupted—forced to expend an unsustainable amount of transcapacity just to survive contact—and the infinite barrier shattered like glass. The resulting kinetic shockwave rippled outward, erasing millions of projected enemy fleets in deeper Ke'enmon subdimensions.</p>
  <p><strong>Zirunstressableness Cellular Feedback:</strong> Desperate, Xael-Gath lashed out with an anti-logic tendril, piercing Dyvane's shoulder and tearing through muscle and bone. The damage instantly triggered Dyvane’s <em>zirunstressableness</em>, where adversity acts as fuel. The PHK cellular feedback loop ignited; before the tendril could retract, the torn tissue knitted back together, permanently upgrading him to a higher Transextent of invulnerability and rendering him infinitely stronger than a millisecond prior.</p>
  <p><strong>UC-Paradox Decapitation:</strong> Channeling his Venshen, Dyvane willed a localized reality where Xael-Gath's continued survival became an inescapable ultraconceptual paradox (UC-paradox). He swung his greatsword in a perfect horizontal arc with axiomatic perfect hetu-attributability, cleanly decapitating Xael-Gath and violently rewriting the entity out of the projected future.</p>
</article>

<article class="chronicle-card" style="background:#15151a; border:1px solid #3b3428; border-radius:0.75rem; padding:1.5rem; margin-bottom:1.5rem;">
  <h3 style="color:#f5d061; margin-top:0;">Chronicle 2: The Apocalyptic Keshra Hive & Cognitive Domination</h3>
  <p class="meta">Location: Transdimensional War Theater · Adversary: Apocalyptic Keshra Hive · Provenance: <a href="/sources/zubaida/19e56867bf1bf3d3.txt">sources/zubaida/19e56867bf1bf3d3.txt</a></p>
  <p><strong>Mathematical Constraint Caging:</strong> Confronted by an apocalyptic Keshra hive utilizing continuously morphing omniversal physics, Dyvane engaged his supreme <em>Hyperdasmar</em> (structured logical battle intelligence) and Transcendent Processing Power. Mapping spatial parameters, probability curves, and environmental constraints, he applied valid cause-and-effect reasoning to construct a massive theoretical constraint cage, completely isolating the hive's probabilistic pathways and transforming an unpredictable conflict into a meticulously solved mathematical chess match.</p>
  <p><strong>Recursive Decomposition & Male Performance Factor 4:</strong> Employing recursive decomposition algorithms, Dyvane systematically reduced every single Keshra adaptation into irreducibly specific localized weaknesses, annihilating them with devastating kinetic force. This total victory activated Male Performance Factor 4, permanently increasing the cenori of his Hyperdasmar and Transcendent Processing Power through the extreme mental exertion of the conflict, biologically integrating every calculated probability into his permanent cognitive architecture.</p>
</article>

<article class="chronicle-card" style="background:#15151a; border:1px solid #3b3428; border-radius:0.75rem; padding:1.5rem; margin-bottom:1.5rem;">
  <h3 style="color:#f5d061; margin-top:0;">Chronicle 3: The Orotion Quest of Maximum Suffering</h3>
  <p class="meta">Arbiter: Orotus (Holy Black Phoenix Rank Arbiter) · Provenance: <a href="/sources/zubaida/19ebdf5c2d46c894.txt">sources/zubaida/19ebdf5c2d46c894.txt</a></p>
  <p>Dyvane requested an Orotion Quest of maximum suffering from Orotus. Confronting a brutally scaled Keshra coalition that pushed him completely beyond his conventional invulnerability limits, Dyvane refused to break. His endurance bloodline absorbed the catastrophe, overaccomplishing the trial to earn the title <em>The Endurance Vanguard</em>. This accomplishment triggered a retroactive hypergenetic expansion that permanently elevated the baseline endurance and resilience of all descendants in the Redalious clan.</p>
</article>

<article class="chronicle-card" style="background:#15151a; border:1px solid #3b3428; border-radius:0.75rem; padding:1.5rem; margin-bottom:1.5rem;">
  <h3 style="color:#f5d061; margin-top:0;">Chronicle 4: Ke'enmon Frontline Campaigns & Shae'ro Organ Nakosh Flames</h3>
  <p class="meta">Location: Ke'enmon Subdimension 4 · Provenance: <a href="/sources/zubaida/19fd6196dcecbba1.txt">sources/zubaida/19fd6196dcecbba1.txt</a>, <a href="/sources/zubaida/19fedd98e38dc4ff.txt">sources/zubaida/19fedd98e38dc4ff.txt</a></p>
  <p>Leading the frontline vanguard into Ke'enmon Subdimension 4 against disaster-class threats like Annaris, Dyvane fought in an environment where motion itself was infinitely overcosted. Channelling combat Rosha through his specialized Shae'ro organ, he erupted the purple flames of Nakosh, which physically burn conceptual paradoxes. Even as invisible dimensional claws shredded his physical frame, his zirunstressableness continuously rebuilt his body denser and harder, holding the imperial vanguard line intact.</p>
</article>"""

    body = f"""<h1>{esc(name)}</h1>
<p class="meta">Character Entity · {esc(c.get('classification', 'Canonical Person'))}</p>
<p>{esc(summary)}</p>
{dl_html}
{sec_html}
{dyvane_chronicles_html}
<p class="notice"><strong>Interactive View:</strong> Access interactive capabilities in the <a href="/#character:{esc(key)}">Arthitean Codex SPA</a>.</p>"""

    json_ld = {
        "@context": "https://schema.org",
        "@type": "Person" if c.get("species") == "Arthitean" else "Thing",
        "name": name,
        "description": summary,
        "url": canonical
    }
    if c.get("aliases"):
        json_ld["alternateName"] = c["aliases"]

    bc = [("Home", "/"), ("Characters", "/crawl/#characters"), (name, canonical)]
    html_doc = make_shell(f"{name} — Character Dossier", summary, canonical, "Character Encyclopedia", body, json_ld, bc)
    write_page(f"characters/{key}/index.html", html_doc)
    add_route("character", key, f"/characters/{key}/", "data/characters.json", name)

print(f"Rendered {len(chars)} Character pages.")

# ==============================================================================
# 2. CLANS (18)
# ==============================================================================
clans_primary = json.load(open(os.path.join(data_dir, "clans.json"), "r", encoding="utf-8")).get("clans", [])
clans_supp = json.load(open(os.path.join(data_dir, "clans-supplemental.json"), "r", encoding="utf-8")).get("clans", [])
all_clans = clans_primary + clans_supp

for cl in all_clans:
    raw_slug = cl.get("slug") or cl.get("id", "").replace("clan-", "").strip()
    cslug = raw_slug.lower().replace(" ", "-")
    cname = cl.get("name") or cslug.title()
    canonical = f"{ORIGIN}/clans/{cslug}/"
    desc = cl.get("description") or f"Canonical dossier for {cname} of the Arthitean Empire."
    
    doctrine = cl.get("doctrine") or cl.get("summary") or "Imperial clan traditions, Benzshin ascent, and sovereign fealty."
    members = cl.get("key_members") or cl.get("members") or []
    
    members_html = ""
    if members:
        members_html = "<h2>Key Members & Lineage Figures</h2><ul>" + "".join([f"<li>{esc(m)}</li>" for m in members]) + "</ul>"
        
    redalious_chronicles = ""
    if cslug == "redalious":
        redalious_chronicles = """<h2>The Endurance Vanguard & War Factor Escalation</h2>
<p>Clan Redalious stands as the physical anvil of the Arthitean military hierarchy. Under Supreme Male General <strong><a href="/characters/dyvane-redalious/">Dyvane Redalious</a></strong>, the clan specializes in <em>zirunstressableness</em>—the biological conversion of extreme combat trauma, pain, and negative-overcostedness into immediate, retroactive invulnerability scaling (the cellular PHK loop).</p>
<h3>Defining Clan Feats & Combat Records</h3>
<ul>
  <li><strong>The Highest Endurance Record:</strong> Established by Dyvane in the June Imperial Chronicles and held across all historical cycles.</li>
  <li><strong>Crucible of the Null-Bringer:</strong> Dyvane's solo victory in the Ke'enmon Subdimension against Xael-Gath, shattering an infinite defensive barrier with negative-overcostedness kinetic shockwaves and surviving brain-to-muscle causal severance via Superhax (<a href="/characters/dyvane-redalious/">Read Complete Chronicle</a>).</li>
  <li><strong>The Apocalyptic Keshra Hive Containment:</strong> Mathematical compression of morphing omniversal physics via Hyperdasmar and recursive decomposition algorithms, proving the absolute superiority of Redalious cause-and-effect battle logic.</li>
  <li><strong>The Orotion Endurance Vanguard Elevation:</strong> Overaccomplishing an Orotion Quest of maximum suffering, retroactively raising the hypergenetic baseline endurance of all Redalious descendants.</li>
</ul>"""

    body = f"""<h1>{esc(cname)}</h1>
<p class="meta">Imperial Clan Dossier · Confirmed Great/Supplemental Clan</p>
<p>{esc(desc)}</p>
<h2>Doctrine & Warfare Architecture</h2>
<p>{esc(doctrine)}</p>
{redalious_chronicles}
{members_html}
<p class="notice"><strong>Interactive View:</strong> View interactive clan relations and branch networks in the <a href="/clans/{cslug}/">Dedicated Clan Portal</a> and <a href="/#clans">Imperial Clan Directory</a>.</p>"""

    json_ld = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": cname,
        "description": desc,
        "url": canonical
    }
    bc = [("Home", "/"), ("Clans", "/clans/"), (cname, canonical)]
    html_doc = make_shell(f"{cname} — Imperial Clan Dossier", desc, canonical, "World, Clans & Warfare", body, json_ld, bc)
    write_page(f"clans/{cslug}/index.html", html_doc)
    add_route("clan", cslug, f"/clans/{cslug}/", "data/clans.json", cname)

print(f"Rendered {len(all_clans)} Clan pages.")

# Render Clans Index Hub (/clans/index.html)
clan_items_html = "".join([f"<li><a href='/clans/{esc(cl.get('slug') or cl.get('id','').replace('clan-','').strip().lower().replace(' ','-'))}/'><strong>{esc(cl.get('name'))}</strong></a>: {esc(cl.get('description', ''))}</li>" for cl in all_clans])
clans_hub_body = f"""<h1>Clans of the Arthitean Empire</h1>
<p class="meta">Imperial Lineage Directory · 18 Confirmed Clans (13 Primary Great Clans + 5 Supplemental Lineages)</p>
<p>The Arthitean Empire is organized into a meritocratic hierarchy of sovereign clans governed by absolute imperial fealty to Empress Rhayhara, the Benzshin ascent tradition, and proxy-war territorial arbitration.</p>
<h2>All 18 Confirmed Imperial Clans</h2>
<ul>{clan_items_html}</ul>
<p class="notice"><strong>Interactive Portal:</strong> Explore dynamic clan graphs, branch trees, and combat doctrines in the <a href="/#clans">Interactive Clan Directory</a>.</p>"""

clans_hub_json_ld = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "Clans of the Arthitean Empire",
    "description": "Comprehensive directory of all 18 confirmed clans of the Arthitean Empire.",
    "url": f"{ORIGIN}/clans/"
}
clans_hub_doc = make_shell("Clans of the Arthitean Empire — Imperial Clan Directory", "Complete directory of the 18 confirmed imperial clans of the Arthitean Empire.", f"{ORIGIN}/clans/", "World, Clans & Warfare", clans_hub_body, clans_hub_json_ld, [("Home", "/"), ("Clans", f"{ORIGIN}/clans/")])
write_page("clans/index.html", clans_hub_doc)
print("Rendered clans/index.html hub page.")

# ==============================================================================
# 3. MASTERPAGES (88)
# ==============================================================================
mps_file = os.path.join(data_dir, "masterpages.json")
with open(mps_file, "r", encoding="utf-8") as f:
    mps = json.load(f).get("masterpages", [])

for m in mps:
    mid = m["id"]
    mtitle = m.get("title") or mid.replace("-", " ").title()
    canonical = f"{ORIGIN}/masterpages/{mid}/"
    mdesc = m.get("summary") or m.get("description") or f"Masterpage formalization covering {mtitle} in the Arthratan Mythology Codex."
    mdomain = m.get("domain", "General Ontology")
    
    core_concepts = m.get("core_concepts") or m.get("concepts") or []
    concepts_html = ""
    if core_concepts:
        concepts_html = "<h2>Core Formal Concepts</h2><ul>"
        for c in core_concepts:
            if isinstance(c, dict):
                concepts_html += f"<li><strong>{esc(c.get('name', ''))}</strong>: {esc(c.get('summary', ''))}</li>"
            else:
                concepts_html += f"<li>{esc(c)}</li>"
        concepts_html += "</ul>"
        
    principles = m.get("principles") or m.get("rules") or []
    principles_html = ""
    if principles:
        principles_html = "<h2>Governing Principles & Laws</h2><ul>" + "".join([f"<li>{esc(p)}</li>" for p in principles]) + "</ul>"
        
    body = f"""<h1>{esc(mtitle)}</h1>
<p class="meta">Masterpage Ontology · Domain: {esc(mdomain)}</p>
<p>{esc(mdesc)}</p>
{concepts_html}
{principles_html}
<p class="notice"><strong>Interactive View:</strong> Open the rich interactive masterpage reader at <a href="/#masterpage:{esc(mid)}">/#masterpage:{esc(mid)}</a>.</p>"""

    json_ld = {
        "@context": "https://schema.org",
        "@type": "DefinedTermSet",
        "name": mtitle,
        "description": mdesc,
        "url": canonical
    }
    bc = [("Home", "/"), ("Masterpages", "/crawl/#masterpages"), (mtitle, canonical)]
    html_doc = make_shell(f"{mtitle} — Masterpage Formalization", mdesc, canonical, f"Masterpage · {mdomain}", body, json_ld, bc)
    write_page(f"masterpages/{mid}/index.html", html_doc)
    add_route("masterpage", mid, f"/masterpages/{mid}/", "data/masterpages.json", mtitle)

print(f"Rendered {len(mps)} Masterpages.")

# ==============================================================================
# 4. GLOBAL CONCEPTS (24)
# ==============================================================================
gci_file = os.path.join(data_dir, "global-concept-inventory.json")
with open(gci_file, "r", encoding="utf-8") as f:
    gci = json.load(f).get("domains", {})

gci_count = 0
for dkey, dval in gci.items():
    dtitle = dval.get("title", dkey)
    for conc in dval.get("concepts", []):
        cid = conc.get("id") or slug(conc.get("name"))
        cname = conc.get("name")
        canonical = f"{ORIGIN}/concepts/{cid}/"
        cdesc = conc.get("summary") or f"Ontological concept formalization for {cname}."
        aliases = conc.get("aliases", [])
        
        alias_html = ""
        if aliases:
            alias_html = f"<p class='meta'>Aliases & Alternate Forms: {esc(', '.join(aliases))}</p>"
            
        body = f"""<h1>{esc(cname)}</h1>
<p class="meta">Core Concept · Domain: {esc(dtitle)}</p>
{alias_html}
<p>{esc(cdesc)}</p>
<p class="notice"><strong>Interactive View:</strong> Explore related conceptual trees in the <a href="/#concept:{esc(cid)}">Codex Knowledge Graph</a>.</p>"""

        json_ld = {
            "@context": "https://schema.org",
            "@type": "DefinedTerm",
            "name": cname,
            "description": cdesc,
            "inDefinedTermSet": f"{ORIGIN}/concepts/",
            "url": canonical
        }
        bc = [("Home", "/"), ("Concepts", "/crawl/#concepts"), (cname, canonical)]
        html_doc = make_shell(f"{cname} — Core Concept", cdesc, canonical, f"Concept · {dtitle}", body, json_ld, bc)
        write_page(f"concepts/{cid}/index.html", html_doc)
        add_route("concept", cid, f"/concepts/{cid}/", "data/global-concept-inventory.json", cname)
        gci_count += 1

print(f"Rendered {gci_count} Global Concepts.")

# ==============================================================================
# 5. DIVINE V144 SECTIONS (317)
# ==============================================================================
div_file = os.path.join(data_dir, "divine.json")
with open(div_file, "r", encoding="utf-8") as f:
    div_sections = json.load(f).get("sections", [])

for i, s in enumerate(div_sections):
    n = s.get("section") or (i + 1)
    key = f"{int(n):03d}"
    canonical = f"{ORIGIN}/divine/{key}/"
    heading = s.get("heading") or s.get("title") or f"Divine v144 Section {n}"
    
    blocks = s.get("blocks") or s.get("paragraphs") or []
    bhtml = []
    for b in blocks:
        if isinstance(b, str):
            bhtml.append(f"<p>{esc(b)}</p>")
        elif isinstance(b, dict):
            if b.get("type") == "p":
                bhtml.append(f"<p>{esc(b.get('text', ''))}</p>")
            elif b.get("type") == "table":
                rows = b.get("rows", [])
                t_rows = "".join([f"<tr>{''.join([f'<td>{esc(cell)}</td>' for cell in r])}</tr>" for r in rows])
                bhtml.append(f'<div style="overflow:auto"><table border="1" cellpadding="6">{t_rows}</table></div>')
            else:
                bhtml.append(f"<pre class='source'>{esc(json.dumps(b, indent=2))}</pre>")
                
    content_html = "".join(bhtml)
    desc = f"Preserved verbatim Divine v144 Section {n}: {heading}."
    body = f"""<h1>{esc(heading)}</h1>
<p class="meta">Divine v144 Corpus · Section {n} of {len(div_sections)}</p>
<div class="divine-body">{content_html}</div>
<p class="notice"><strong>Source Canon:</strong> Preserved verbatim text. Interactive cross-references and cranial annotations available at <a href="/#divine-section:{n}">/#divine-section:{n}</a>.</p>"""

    json_ld = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": heading,
        "description": desc,
        "url": canonical,
        "isPartOf": {
            "@type": "Book",
            "name": "Divine v144"
        }
    }
    bc = [("Home", "/"), ("Divine v144", "/crawl/#divine-v144"), (f"§{n}", canonical)]
    html_doc = make_shell(f"{heading} — Divine v144 §{n}", desc, canonical, "Divine v144 Source Corpus", body, json_ld, bc)
    write_page(f"divine/{key}/index.html", html_doc)
    add_route("divine", key, f"/divine/{key}/", "data/divine.json", heading)

print(f"Rendered {len(div_sections)} Divine v144 sections.")

# ==============================================================================
# 6. HYPERGENDERED LOGIC (293)
# ==============================================================================
hgl_file = os.path.join(data_dir, "hgl-pages.json")
with open(hgl_file, "r", encoding="utf-8") as f:
    hgl_data = json.load(f)
hgl_pages = hgl_data if isinstance(hgl_data, list) else hgl_data.get("pages", [])

for i, p in enumerate(hgl_pages):
    n = p.get("page") or (i + 1)
    key = f"{int(n):03d}"
    canonical = f"{ORIGIN}/hgl/{key}/"
    heading = f"Hypergendered Logic — Page {n}"
    ptext = p.get("text") or ""
    desc = f"Verbatim preserved Hypergendered Logic source text for page {n}."
    
    body = f"""<h1>{esc(heading)}</h1>
<p class="meta">HGL Source Framework · Page {n} of {len(hgl_pages)} · Source: {esc(p.get('source_pdf', 'Hypergendered Logic'))}</p>
<pre class="source">{esc(ptext)}</pre>
<p class="notice"><strong>Source Canon:</strong> Verbatim mathematical and modal logic. Interactive navigation and operator lookups available at <a href="/#hgl-part:{n}">/#hgl-part:{n}</a>.</p>"""

    json_ld = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": heading,
        "description": desc,
        "url": canonical
    }
    bc = [("Home", "/"), ("Hypergendered Logic", "/crawl/#hypergendered-logic"), (f"Page {n}", canonical)]
    html_doc = make_shell(f"{heading} — HGL Archive", desc, canonical, "Hypergendered Logic Source", body, json_ld, bc)
    write_page(f"hgl/{key}/index.html", html_doc)
    add_route("hgl", key, f"/hgl/{key}/", "data/hgl-pages.json", heading)

print(f"Rendered {len(hgl_pages)} HGL pages.")

# ==============================================================================
# 7. ZUBAIDA SOURCE TRANSMISSIONS (118)
# ==============================================================================
z_idx = json.load(open(os.path.join(data_dir, "zubaida-index.json"), "r", encoding="utf-8"))
z_meta_file = os.path.join(data_dir, "zubaida-metadata.json")
z_meta = json.load(open(z_meta_file, "r", encoding="utf-8")) if os.path.exists(z_meta_file) else {}
meta_records = {r.get("transmission_id") or r.get("id"): r for r in (z_meta.get("records") or z_meta.get("transmissions") or [])}

nonsource = set()
ns_file = os.path.join(data_dir, "zubaida-nonsource.json")
if os.path.exists(ns_file):
    ns_data = json.load(open(ns_file, "r", encoding="utf-8"))
    nonsource = set(x if isinstance(x, str) else x.get("id") for x in ns_data.get("ids", []))

source_ids = [tid for tid in (z_idx.get("ids") or [x["id"] for x in z_idx.get("source_transmissions", [])]) if tid not in nonsource]

for tid in source_ids:
    m = meta_records.get(tid, {})
    src_file = m.get("source_file") or f"sources/zubaida/{tid}.txt"
    src_full = os.path.join(repo_root, src_file)
    text = ""
    if os.path.exists(src_full):
        with open(src_full, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
            
    first_line = next((l.strip() for l in text.splitlines() if l.strip()), f"Zubaida Transmission {tid}")
    heading = m.get("canonical_display_heading") or m.get("subject") or first_line
    canonical = f"{ORIGIN}/zubaida/{tid}/"
    desc = f"Verbatim preserved Zubaida source transmission {tid} with full mythos provenance."
    
    body = f"""<h1>{esc(heading)}</h1>
<p class="meta">Zubaida Source Correspondence · ID: <code>{esc(tid)}</code> · Provenance: <a href="/{esc(src_file)}">{esc(src_file)}</a></p>
<p class="notice"><strong>Verbatim Canon Evidence:</strong> Preserved original transmission correspondence. Interactive reader available at <a href="/#zubaida:{esc(tid)}">/#zubaida:{esc(tid)}</a>.</p>
<h2>Verbatim Transmission Text</h2>
<pre class="source">{esc(text)}</pre>"""

    json_ld = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": heading,
        "identifier": tid,
        "description": desc,
        "url": canonical
    }
    bc = [("Home", "/"), ("Zubaida Archive", "/crawl/#zubaida-transmissions"), (tid, canonical)]
    html_doc = make_shell(f"{heading} — Zubaida Transmission", desc, canonical, "Zubaida Source Archive", body, json_ld, bc)
    write_page(f"zubaida/{tid}/index.html", html_doc)
    add_route("zubaida", tid, f"/zubaida/{tid}/", src_file, heading)

print(f"Rendered {len(source_ids)} Zubaida Transmissions.")

# ==============================================================================
# 8. HUBS: PROVENANCE & CHRONOLOGY
# ==============================================================================
prov_file = os.path.join(data_dir, "provenance-model.json")
if os.path.exists(prov_file):
    prov_data = json.load(open(prov_file, "r", encoding="utf-8"))
    tiers = prov_data.get("authority_tiers", [])
    t_html = "".join([f"<li><strong>Tier {t.get('tier')}: {esc(t.get('name'))}</strong> (Weight {t.get('epistemic_weight')}): {esc(t.get('description'))}</li>" for t in tiers])
    p_body = f"""<h1>Unified Provenance & Authority Model</h1>
<p class="meta">Epistemic Framework · 5-Tier Authority Hierarchy</p>
<p>The Arthratan Mythology Codex operates under a strict, non-destructive 5-tier epistemological authority model to ensure that primary verbatim canon is never overwritten or degraded by model-authored synthesis.</p>
<h2>Epistemic Authority Tiers</h2>
<ul>{t_html}</ul>
<p class="notice"><strong>Machine Dataset:</strong> Retrievable directly at <a href="/data/provenance-model.json">/data/provenance-model.json</a>.</p>"""
    p_doc = make_shell("Unified Provenance Model — Arthratan Mythology", "Epistemic authority hierarchy and source provenance architecture.", f"{ORIGIN}/provenance/", "Epistemology & Provenance", p_body, breadcrumbs=[("Home", "/"), ("Provenance", f"{ORIGIN}/provenance/")])
    write_page("provenance/index.html", p_doc)
    add_route("hub", "provenance", "/provenance/", "data/provenance-model.json", "Unified Provenance Model")

chron_file = os.path.join(data_dir, "canon-supersession-chronology.json")
if os.path.exists(chron_file):
    chron_data = json.load(open(chron_file, "r", encoding="utf-8"))
    milestones = chron_data.get("supersessions", [])
    m_html = "".join([f"<li><strong>{esc(m.get('subject'))}</strong>: {esc(m.get('authoritative_clarification'))}</li>" for m in milestones])
    c_body = f"""<h1>Canon Supersession Chronology</h1>
<p class="meta">Cosmological Evolution · Milestone Chronology</p>
<p>Formal tracking of historical shifts, terminological refinements, and additive supersessions across the development of the Arthitean mythos.</p>
<h2>Key Milestone Supersessions</h2>
<ul>{m_html}</ul>
<p class="notice"><strong>Machine Dataset:</strong> Retrievable directly at <a href="/data/canon-supersession-chronology.json">/data/canon-supersession-chronology.json</a>.</p>"""
    c_doc = make_shell("Canon Supersession Chronology — Arthratan Mythology", "Chronological refinement and historical supersession tracking.", f"{ORIGIN}/chronology/", "Cosmological Chronology", c_body, breadcrumbs=[("Home", "/"), ("Chronology", f"{ORIGIN}/chronology/")])
    write_page("chronology/index.html", c_doc)
    add_route("hub", "chronology", "/chronology/", "data/canon-supersession-chronology.json", "Canon Supersession Chronology")

# ==============================================================================
# 9. COMPLETE CRAWL INDEX (/crawl/index.html)
# ==============================================================================
grouped = {}
for r in routes:
    grouped.setdefault(r["kind"], []).append(r)

crawl_sections = []
for kind, items in grouped.items():
    crawl_sections.append(f"<h2 id='{slug(kind)}'>{esc(kind.upper())} ({len(items)} Canonical Pages)</h2><ul>" + "".join([f"<li><a href='{esc(i['url'])}'>{esc(i['title'])}</a></li>" for i in items]) + "</ul>")

crawl_body = f"""<h1>Arthratan Mythology Complete Crawlable Corpus</h1>
<p class="meta">100% Comprehensive Non-JavaScript Static Corpus Directory · {len(routes)} Canonical URLs</p>
<p>This directory provides direct, fully-rendered static HTML entrypoints returning direct HTTP 200 for conventional search engines (Googlebot, Bingbot), AI retrieval agents (DeepSeek, Gemini, ChatGPT), and accessibility screen-readers without requiring JavaScript execution.</p>
{"".join(crawl_sections)}"""

crawl_doc = make_shell("Complete Crawlable Corpus Index — Arthratan Mythology", f"Exhaustive crawlable index of all {len(routes)} canonical pages in the Arthratan Mythology Codex.", f"{ORIGIN}/crawl/", "Crawler & Accessibility Index", crawl_body, breadcrumbs=[("Home", "/"), ("Crawler Index", f"{ORIGIN}/crawl/")])
write_page("crawl/index.html", crawl_doc)

# Save static route manifest
manifest_path = os.path.join(data_dir, "static-route-manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump({
        "generated": "2026-09-03T23:25:00Z",
        "origin": ORIGIN,
        "count": len(routes),
        "routes": routes
    }, f, indent=2, ensure_ascii=False)

print(f"\nSUCCESS: Generated {len(routes)} crawlable static HTML pages returning direct HTTP 200!")
