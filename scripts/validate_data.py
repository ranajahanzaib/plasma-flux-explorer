#!/usr/bin/env python3
"""Validate local catalog structure and scientific frame coordinate metadata."""
import json, math, sys
from pathlib import Path

path=Path(__file__).resolve().parents[1]/"data/processed/catalog.json"
if not path.exists(): raise SystemExit("No local catalog. Run `pnpm data:bootstrap` first.")
catalog=json.loads(path.read_text()); errors=[]; warnings=[]
if catalog.get("schema_version")!="1.0.0": errors.append("Unsupported catalog schema version")
seen=set()
for r in catalog.get("records",[]):
    if not r.get("id") or r["id"] in seen: errors.append(f"Missing or duplicate stable record id: {r.get('id')}")
    seen.add(r.get("id"))
    if r.get("reference_available") and not r.get("frames"): errors.append(f"{r['id']}: reference flag set without frames")
    if r.get("configuration") in ("diii_d_public_test","mast_public_test") and r.get("reference_available"): errors.append(f"{r['id']}: public test labels must remain withheld")
    for i,f in enumerate(r.get("frames",[])):
        grid=f.get("psi"); R=f.get("R"); Z=f.get("Z")
        if not grid or not R or not Z: errors.append(f"{r['id']} frame {i}: missing flux grid or coordinate vectors"); continue
        if len(grid)!=len(Z) or any(len(row)!=len(R) for row in grid): errors.append(f"{r['id']} frame {i}: array/grid shape mismatch")
        if any(not math.isfinite(float(x)) for x in R+Z): errors.append(f"{r['id']} frame {i}: non-finite coordinate")
        if any(R[j]>=R[j+1] for j in range(len(R)-1)) or any(Z[j]>=Z[j+1] for j in range(len(Z)-1)): errors.append(f"{r['id']} frame {i}: coordinates not strictly increasing")
        if not f.get("axis") or f["axis"].get("R") is None: warnings.append(f"{r['id']} frame {i}: EFIT magnetic axis unavailable")
    if not r.get("source_url") or not r.get("revision") or not r.get("sha256"): errors.append(f"{r.get('id')}: provenance metadata incomplete")
print(f"Records: {len(seen)} · Errors: {len(errors)} · Warnings: {len(warnings)}")
for m in errors+warnings: print(("ERROR: " if m in errors else "WARNING: ")+m)
if errors: raise SystemExit(1)
