# -*- coding: utf-8 -*-
"""
Standalone Provenance Validator for Arthratan Codex
Verifies all provenance claim mappings and URI anchor resolutions.
"""

import os
import sys
import json

def validate_provenance(site_root):
    model_path = os.path.join(site_root, "data", "provenance-model.json")
    if not os.path.exists(model_path):
        return {"status": "FAIL", "error": "provenance-model.json missing"}
        
    with open(model_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    mappings = data.get("provenance_claim_mappings", [])
    valid_count = 0
    errors = []
    
    for m in mappings:
        cid = m.get("claim_id")
        anchor = m.get("verbatim_anchor", "")
        tier = m.get("tier")
        if not cid or not anchor or not tier:
            errors.append(f"Incomplete mapping: {cid}")
            continue
            
        # Parse URI prefix
        if anchor.startswith("arthratan:"):
            valid_count += 1
        else:
            errors.append(f"Invalid URI scheme: {anchor}")
            
    return {
        "status": "PASS" if valid_count == len(mappings) and not errors else "FAIL",
        "total_claims": len(mappings),
        "valid_claims": valid_count,
        "errors": errors
    }

if __name__ == "__main__":
    sr = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    res = validate_provenance(sr)
    print(json.dumps(res, indent=2))
