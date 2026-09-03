#!/usr/bin/env python3
"""
IndexNow Search Engine Indexation Submitter
Submits core canonical URLs of arthratanmythology.com to the IndexNow protocol
(supported by Microsoft Bing, Yandex, Seznam, and Naver) to accelerate
crawling, discovery, and SERP indexing.
"""

import urllib.request
import json
import sys

KEY = "8d4b3f1e7a2c4e9f8a1b2c3d4e5f6a7b"
HOST = "arthratanmythology.com"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"

# Core high-priority canonical routes
URL_LIST = [
    f"https://{HOST}/",
    f"https://{HOST}/characters/dyvane-redalious/",
    f"https://{HOST}/characters/rhayhara/",
    f"https://{HOST}/characters/qintara-unmatara/",
    f"https://{HOST}/characters/xael-gath/",
    f"https://{HOST}/characters/halatayo/",
    f"https://{HOST}/clans/",
    f"https://{HOST}/clans/redalious/",
    f"https://{HOST}/clans/unmatara/",
    f"https://{HOST}/clans/varvadeil/",
    f"https://{HOST}/masterpages/supramajor/",
    f"https://{HOST}/masterpages/hypernegative-rewrite/",
    f"https://{HOST}/masterpages/negative-rewrite/",
    f"https://{HOST}/zubaida/19fa076eb25a917b/",
    f"https://{HOST}/zubaida/19e56867bf1bf3d3/",
    f"https://{HOST}/crawl/",
    f"https://{HOST}/ai/",
    f"https://{HOST}/sitemap.xml",
    f"https://{HOST}/robots.txt"
]

def submit_indexnow():
    endpoint = "https://api.indexnow.org/indexnow"
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": URL_LIST
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[SUCCESS] IndexNow API returned HTTP {r.status} {r.reason}")
            print(f"Submitted {len(URL_LIST)} canonical URLs to IndexNow network.")
            return True
    except urllib.error.HTTPError as e:
        print(f"[HTTP ERROR] {e.code} {e.reason}")
        print(e.read().decode("utf-8", errors="replace"))
        return False
    except Exception as e:
        print(f"[ERROR] Failed to submit to IndexNow: {e}")
        return False

if __name__ == "__main__":
    submit_indexnow()
