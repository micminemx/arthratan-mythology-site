# -*- coding: utf-8 -*-
"""
Exhaustive XML Sitemap Generator
Generates a valid XML sitemap indexing all 907 canonical URLs in the Codex.
"""
import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys

sys.stdout.reconfigure(encoding='utf-8')

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
manifest_file = os.path.join(repo_root, "data", "static-route-manifest.json")
sitemap_file = os.path.join(repo_root, "sitemap.xml")
ORIGIN = "https://arthratanmythology.com"

print("Building Comprehensive Production XML Sitemap...")

with open(manifest_file, "r", encoding="utf-8") as f:
    data = json.load(f)

routes = data.get("routes", [])

# Collect all canonical URLs
urls = [
    {"loc": f"{ORIGIN}/", "changefreq": "daily", "priority": "1.0"},
    {"loc": f"{ORIGIN}/crawl/", "changefreq": "daily", "priority": "0.9"},
    {"loc": f"{ORIGIN}/search/", "changefreq": "daily", "priority": "0.9"},
    {"loc": f"{ORIGIN}/clans/", "changefreq": "weekly", "priority": "0.9"},
    {"loc": f"{ORIGIN}/provenance/", "changefreq": "monthly", "priority": "0.8"},
    {"loc": f"{ORIGIN}/chronology/", "changefreq": "monthly", "priority": "0.8"}
]

for r in routes:
    u = r["url"]
    full_loc = f"{ORIGIN}{u}"
    kind = r.get("kind", "")
    
    if full_loc in [x["loc"] for x in urls]:
        continue
        
    prio = "0.7"
    freq = "monthly"
    if kind in ["character", "clan", "masterpage"]:
        prio = "0.8"
        freq = "weekly"
    elif kind in ["divine", "hgl", "zubaida"]:
        prio = "0.7"
        freq = "monthly"
        
    urls.append({"loc": full_loc, "changefreq": freq, "priority": prio})

# Build XML
urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

for item in urls:
    url_tag = ET.SubElement(urlset, "url")
    loc_tag = ET.SubElement(url_tag, "loc")
    loc_tag.text = item["loc"]
    
    lastmod_tag = ET.SubElement(url_tag, "lastmod")
    lastmod_tag.text = "2026-09-03"
    
    cf_tag = ET.SubElement(url_tag, "changefreq")
    cf_tag.text = item["changefreq"]
    
    prio_tag = ET.SubElement(url_tag, "priority")
    prio_tag.text = item["priority"]

rough_string = ET.tostring(urlset, 'utf-8')
reparsed = minidom.parseString(rough_string)
pretty_xml = reparsed.toprettyxml(indent="  ")

# Clean blank lines from minidom
cleaned_xml = "\n".join([line for line in pretty_xml.splitlines() if line.strip()]) + "\n"

with open(sitemap_file, "w", encoding="utf-8") as f:
    f.write(cleaned_xml)

print(f"SUCCESS: Generated sitemap.xml with {len(urls)} canonical URLs at {sitemap_file} ({os.path.getsize(sitemap_file)} bytes)!")
