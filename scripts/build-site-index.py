# -*- coding: utf-8 -*-
"""
Canonical Site Index Generator for Arthratan Mythology / Arthitean Codex
Builds data/site-index.json across all 7 canonical knowledge domains with A–Z,
hierarchical domain ontology, and alias resolution hash map.
"""
import os
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_dir = os.path.join(repo_root, "data")
output_path = os.path.join(data_dir, "site-index.json")

print(f"Building Canonical Site Index in {repo_root}...")

# 1. Load source datasets
with open(os.path.join(data_dir, "characters.json"), "r", encoding="utf-8") as f:
    chars_data = json.load(f)["characters"]

with open(os.path.join(data_dir, "masterpages.json"), "r", encoding="utf-8") as f:
    mp_data = json.load(f)["masterpages"]

with open(os.path.join(data_dir, "global-concept-inventory.json"), "r", encoding="utf-8") as f:
    gci_data = json.load(f)["domains"]

with open(os.path.join(data_dir, "divine.json"), "r", encoding="utf-8") as f:
    div_sections = json.load(f)["sections"]

with open(os.path.join(data_dir, "hgl-toc.json"), "r", encoding="utf-8") as f:
    hgl_parts = json.load(f)["parts"]

# Load clan datasets
clans_primary = []
clans_primary_file = os.path.join(data_dir, "clans.json")
if os.path.exists(clans_primary_file):
    with open(clans_primary_file, "r", encoding="utf-8") as f:
        clans_primary = json.load(f).get("clans", [])

clans_supp = []
clans_supp_file = os.path.join(data_dir, "clans-supplemental.json")
if os.path.exists(clans_supp_file):
    with open(clans_supp_file, "r", encoding="utf-8") as f:
        clans_supp = json.load(f).get("clans", [])

culture_ontology = {}
cult_file = os.path.join(data_dir, "culture-clans-ontology.json")
if os.path.exists(cult_file):
    with open(cult_file, "r", encoding="utf-8") as f:
        culture_ontology = json.load(f)

chronology_data = {}
chron_file = os.path.join(data_dir, "canon-supersession-chronology.json")
if os.path.exists(chron_file):
    with open(chron_file, "r", encoding="utf-8") as f:
        chronology_data = json.load(f)

canonical_entries = {}
alias_map = {}

def add_entry(entry_id, label, domain, category, aliases, provenance, target_url, description, status="CANONICAL"):
    # Normalize clean label
    clean_label = label.strip()
    clean_url = target_url.strip()
    assert " " not in clean_url, f"Malformed URL with spaces: {clean_url}"
    assert "Clan Clan" not in clean_label, f"Malformed duplicate Clan label: {clean_label}"
    
    if entry_id in canonical_entries:
        existing = canonical_entries[entry_id]
        existing_aliases = set(existing["aliases"])
        for a in aliases:
            if a and a.strip() and a.lower() != clean_label.lower() and a not in existing_aliases:
                existing["aliases"].append(a.strip())
                existing_aliases.add(a.strip())
        return
    
    clean_aliases = []
    seen = set()
    for a in aliases:
        if a and a.strip() and a.lower() != clean_label.lower() and a.lower() not in seen:
            clean_aliases.append(a.strip())
            seen.add(a.lower())
            
    entry = {
        "id": entry_id,
        "label": clean_label,
        "domain": domain,
        "category": category,
        "aliases": clean_aliases,
        "provenance": provenance,
        "target_url": clean_url,
        "description": description.strip() if isinstance(description, str) else str(description),
        "status": status
    }
    canonical_entries[entry_id] = entry
    
    # Register aliases in alias map
    for a in clean_aliases:
        norm_a = a.lower()
        if norm_a not in alias_map:
            alias_map[norm_a] = {
                "canonical_id": entry_id,
                "canonical_label": clean_label,
                "domain": domain,
                "target_url": clean_url
            }

# A. Ingest Characters
for c in chars_data:
    cid = c.get("slug") or c.get("id") or c["name"].lower().replace(" ", "-")
    name = c["name"]
    aliases = list(c.get("aliases", [])) + list(c.get("titles", []))
    role = c.get("role", "Character")
    species = c.get("species", "Arthitean")
    clan = c.get("clan")
    cat = f"{species} ({clan})" if clan else species
    prov = "data/characters.json"
    if c.get("source_threads"):
        prov += f" | Threads: {', '.join(c['source_threads'][:3])}"
        
    url = f"/characters/{cid}/"
    desc = c.get("summary", f"{name} — {role}.")
    
    # Invariant Orotus Rule
    if "orotus" in cid.lower():
        aliases.extend(["Sunborn Phoenix", "Divine Beast of the Arthiatan Empire", "Holy Black Phoenix"])
        desc = "Orotus is the Divine Beast of the Arthiatan Empire, the Sunborn Phoenix. Governed exclusively by Sheet 04 canon model; Sheet 03 humanoid depiction is strictly quarantined."
        
    add_entry(
        entry_id=f"char-{cid}",
        label=name,
        domain="Characters & Entities",
        category=cat,
        aliases=aliases,
        provenance=prov,
        target_url=url,
        description=desc,
        status="CANONICAL"
    )

# B. Ingest Masterpages
for m in mp_data:
    mid = m["id"]
    title = m.get("title") or mid.replace("-", " ").title()
    dom = m.get("domain") or "General Ontology"
    aliases = list(m.get("aliases", []))
    summary = m.get("summary") or m.get("description") or f"Masterpage covering {title} concepts and formalization."
    url = f"/#masterpage:{mid}"
    prov = "data/masterpages.json"
    
    add_entry(
        entry_id=f"mp-{mid}",
        label=title,
        domain="Core Concepts & Masterpages",
        category=dom,
        aliases=aliases,
        provenance=prov,
        target_url=url,
        description=summary,
        status="CANONICAL"
    )

# C. Ingest Global Concept Inventory (GCI)
for dom_key, dom_val in gci_data.items():
    dom_title = dom_val.get("title", dom_key)
    for concept in dom_val.get("concepts", []):
        cid = concept.get("id") or concept["name"].lower().replace(" ", "-")
        cname = concept["name"]
        aliases = list(concept.get("aliases", []))
        summary = concept.get("summary", "")
        url = f"/#masterpage:{cid}"
        prov = f"data/global-concept-inventory.json [{dom_key}]"
        
        add_entry(
            entry_id=f"concept-{cid}",
            label=cname,
            domain="Core Concepts & Masterpages",
            category=dom_title,
            aliases=aliases,
            provenance=prov,
            target_url=url,
            description=summary,
            status="CANONICAL"
        )

# D. Ingest Divine v144 Key Sections
for sec in div_sections:
    s_num = sec.get("section") or sec.get("id")
    s_title = sec.get("title") or f"Divine Section {s_num}"
    s_id = f"divine-sec-{s_num}"
    url = f"/#divine-section:{s_num}"
    summary = sec.get("summary") or sec.get("text", "")[:180] + "..."
    aliases = [f"Section {s_num}", f"Divine v144 Sec {s_num}"]
    if sec.get("thematic_tag"):
        aliases.append(sec["thematic_tag"])
    
    add_entry(
        entry_id=s_id,
        label=f"Divine v144 §{s_num}: {s_title}",
        domain="Divine v144 Corpus",
        category="Theological & Cranial Doctrine",
        aliases=aliases,
        provenance=f"data/divine.json [Section {s_num}]",
        target_url=url,
        description=summary,
        status="CANONICAL"
    )

# E. Ingest Hypergendered Logic (HGL) Parts & Operators
for p in hgl_parts:
    p_num = p.get("part") or p.get("id")
    p_title = p.get("title") or f"HGL Part {p_num}"
    p_id = f"hgl-part-{p_num}"
    url = f"/#hgl-part:{p_num}"
    summary = p.get("summary") or f"Hypergendered Logic Part {p_num}: {p_title}."
    aliases = [f"Part {p_num}", f"HGL Part {p_num}"]
    if p.get("operators"):
        aliases.extend(p["operators"])
        
    add_entry(
        entry_id=p_id,
        label=f"HGL Part {p_num}: {p_title}",
        domain="Hypergendered Logic (HGL)",
        category="Formal Logical Framework",
        aliases=aliases,
        provenance=f"data/hgl-toc.json [Part {p_num}]",
        target_url=url,
        description=summary,
        status="CANONICAL"
    )

# F. Ingest World, Clans & Warfare Institutions (Corrected Generator)
# Ingest all confirmed clans from clans.json and clans-supplemental.json
for clan in clans_primary:
    raw_name = clan.get("name", "")
    clean_base = re.sub(r'^(Clan\s+)+', '', raw_name, flags=re.IGNORECASE).strip()
    clean_base = re.sub(r'(\s+Clan)+$', '', clean_base, flags=re.IGNORECASE).strip()
    label = f"Clan {clean_base}"
    raw_slug = clan.get("slug") or clan.get("id", "").replace("clan-", "").strip()
    clean_slug = raw_slug.lower().replace(" ", "-")
    c_id = f"clan-{clean_slug}"
    url = f"/clans/{clean_slug}/"
    desc = clan.get("description") or f"Confirmed Great Clan {clean_base} of the Arthitean Empire."
    aliases = clan.get("aliases", [])
    
    add_entry(
        entry_id=c_id,
        label=label,
        domain="World, Clans & Warfare Institutions",
        category="Great Clans of the Empire",
        aliases=aliases,
        provenance="data/clans.json",
        target_url=url,
        description=desc,
        status="CANONICAL"
    )

for clan in clans_supp:
    raw_name = clan.get("name", "")
    clean_base = re.sub(r'^(Clan\s+)+', '', raw_name, flags=re.IGNORECASE).strip()
    clean_base = re.sub(r'(\s+Clan)+$', '', clean_base, flags=re.IGNORECASE).strip()
    label = f"Clan {clean_base}"
    raw_slug = clan.get("slug") or clan.get("id", "").replace("clan-", "").strip()
    clean_slug = raw_slug.lower().replace(" ", "-")
    c_id = f"clan-{clean_slug}"
    url = f"/clans/{clean_slug}/"
    desc = clan.get("description") or f"Supplemental confirmed clan {clean_base} of the Arthitean Empire."
    aliases = clan.get("aliases", [])
    
    add_entry(
        entry_id=c_id,
        label=label,
        domain="World, Clans & Warfare Institutions",
        category="Supplemental Clans of the Empire",
        aliases=aliases,
        provenance="data/clans-supplemental.json",
        target_url=url,
        description=desc,
        status="CANONICAL"
    )

# Institutions from culture-clans-ontology.json
for inst in culture_ontology.get("institutions", []):
    i_id = f"inst-{inst['name'].lower().replace(' ', '-')}"
    url = f"/concepts/culture/#{inst.get('id', inst['name'].lower().replace(' ', '-'))}"
    add_entry(
        entry_id=i_id,
        label=inst["name"],
        domain="World, Clans & Warfare Institutions",
        category="Imperial Institutions & Warfare",
        aliases=inst.get("aliases", []),
        provenance="data/culture-clans-ontology.json",
        target_url=url,
        description=inst.get("description", f"Imperial institution: {inst['name']}."),
        status="CANONICAL"
    )

# G. Ingest Zubaida Transmissions (1 to 118)
for t_idx in range(1, 119):
    t_id = f"zub-trans-{t_idx:03d}"
    add_entry(
        entry_id=t_id,
        label=f"Zubaida Transmission {t_idx}",
        domain="Zubaida Transmissions",
        category="Verbatim Email Transmissions",
        aliases=[f"Transmission {t_idx}", f"Zub {t_idx}", f"ZUB-{t_idx:03d}"],
        provenance=f"sources/zubaida/transmission_{t_idx:03d}.txt",
        target_url=f"/#zubaida:{t_idx}",
        description=f"Verbatim preserved transmission {t_idx} from Zubaida correspondence, containing primary mythos evidence.",
        status="CANONICAL"
    )

# H. Ingest Living Canon & Supersession Chronology
for rec in chronology_data.get("supersessions", []):
    s_id = f"chron-{rec['id']}"
    add_entry(
        entry_id=s_id,
        label=rec.get("subject") or rec.get("title") or rec["id"],
        domain="Living Canon & Cosmological Chronology",
        category="Supersession & Chronology Records",
        aliases=rec.get("aliases", []),
        provenance="data/canon-supersession-chronology.json",
        target_url=f"/#chronology:{rec['id']}",
        description=rec.get("authoritative_clarification") or rec.get("summary") or "Chronological refinement and historical clarification of canonical terminology.",
        status="CANONICAL"
    )

# 2. Structure A to Z Partitioning
a_to_z = {}
for char_code in range(ord('A'), ord('Z') + 1):
    a_to_z[chr(char_code)] = []
a_to_z["0-9"] = []

for eid, entry in canonical_entries.items():
    label = entry["label"]
    sort_key = label
    for prefix in ["Divine v144 §", "HGL Part ", "Clan "]:
        if sort_key.startswith(prefix):
            sort_key = sort_key[len(prefix):]
            break
            
    first_char = sort_key[0].upper()
    if first_char.isalpha():
        a_to_z.setdefault(first_char, []).append(entry)
    elif first_char.isdigit():
        a_to_z["0-9"].append(entry)
    else:
        a_to_z.setdefault("A", []).append(entry)

for k in a_to_z:
    a_to_z[k].sort(key=lambda x: x["label"].lower())

# 3. Structure Hierarchical Domain Tree
hierarchical_tree = {}
for eid, entry in canonical_entries.items():
    dom = entry["domain"]
    cat = entry["category"]
    if dom not in hierarchical_tree:
        hierarchical_tree[dom] = {}
    if cat not in hierarchical_tree[dom]:
        hierarchical_tree[dom][cat] = []
    hierarchical_tree[dom][cat].append({
        "id": entry["id"],
        "label": entry["label"],
        "target_url": entry["target_url"],
        "aliases_count": len(entry["aliases"])
    })

for dom in hierarchical_tree:
    for cat in hierarchical_tree[dom]:
        hierarchical_tree[dom][cat].sort(key=lambda x: x["label"].lower())

total_canonical = len(canonical_entries)
total_aliases = len(alias_map)
total_indexable = total_canonical + total_aliases

site_index = {
    "metadata": {
        "schema_version": "1.0.0",
        "bounty_id": "INDEX-001",
        "worker_id": "AG-20260903-1647-N3K8",
        "title": "Arthratan Mythology / Arthitean Codex Canonical Site Index",
        "description": "Comprehensive human-oriented A–Z and hierarchical directory across all 7 knowledge domains, with full alias resolution and route mapping.",
        "generated_at": "2026-09-03T23:05:00Z",
        "metrics": {
            "total_canonical_entries": total_canonical,
            "total_alias_mappings": total_aliases,
            "total_indexable_terms": total_indexable,
            "domains_count": len(hierarchical_tree),
            "alphabetical_partitions": len([k for k, v in a_to_z.items() if len(v) > 0])
        }
    },
    "domains_summary": {dom: sum(len(items) for items in cats.values()) for dom, cats in hierarchical_tree.items()},
    "a_to_z": a_to_z,
    "hierarchical_tree": hierarchical_tree,
    "alias_map": alias_map
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(site_index, f, indent=2, ensure_ascii=False)

print(f"SUCCESS: Generated clean canonical site-index.json ({total_canonical} entries, {total_aliases} aliases) at {output_path} ({os.path.getsize(output_path)} bytes)")
