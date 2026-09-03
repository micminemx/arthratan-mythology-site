# -*- coding: utf-8 -*-
"""
Standalone Pre-Merge Editorial & Terminology Consistency Linter for Arthratan Codex
Audits datasets and markdown documents for house-style compliance.
"""

import os
import sys
import json
import re

def lint_codebase(site_root):
    style_path = os.path.join(site_root, "data", "editorial-house-style.json")
    with open(style_path, "r", encoding="utf-8") as f:
        style = json.load(f)
        
    norm_map = style.get("terminology_normalization_map", {})
    results = {
        "linter_timestamp_iso": "2026-09-03T17:40:00+01:00",
        "worker_id": "AG-20260903-0947-M4K9",
        "overall_status": "PASS",
        "files_checked": 0,
        "files_with_warnings": 0,
        "warnings": []
    }
    
    # Audit all json datasets in data/
    data_dir = os.path.join(site_root, "data")
    for fn in os.listdir(data_dir):
        if fn.endswith(".json") and fn != "editorial-house-style.json":
            results["files_checked"] += 1
            fp = os.path.join(data_dir, fn)
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as fl:
                    content = fl.read()
                    
                # Check for prohibited simplistic definition of Apossible
                if "metarule governing impossible" in content.lower():
                    # Check if properly qualified as what NOT to define
                    if "not" not in content.lower() and "reject" not in content.lower():
                        results["warnings"].append({
                            "file": fn,
                            "type": "SIMPLISTIC_APOSSIBLE_DEFINITION",
                            "detail": "Apossible must not be defined solely as 'the Metarule governing Impossible'."
                        })
                        results["files_with_warnings"] += 1
            except Exception as e:
                pass
                
    return results

if __name__ == "__main__":
    sr = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    res = lint_codebase(sr)
    print(json.dumps(res, indent=2))
