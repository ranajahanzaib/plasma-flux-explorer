#!/usr/bin/env python3
"""Build a small real-record catalog from official starter or challenge data.

Default mode downloads one official Parquet demo per machine. Pass
`--source challenge` to request rows from the challenge's Dataset Viewer API.
Only the selected records are fetched; this never downloads the full corpus.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pyarrow.parquet as parquet

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scientific.equilibrium import boundary_metrics, topology_candidates

DATASET = "Sophelio/fusion-equilibrium-challenge"
STARTER_REPO = "Sophelio/fusion-equilibrium-challenge-starter"
ENDPOINT = "https://datasets-server.huggingface.co/rows"
CONFIGS = {
    "diii_d_train": ("DIII-D", "train"),
    "diii_d_public_test": ("DIII-D", "public_test"),
    "mast_public_test": ("MAST", "public_test"),
}
DEMO_FILES = {
    "DIII-D": ["d3d_shot_203702.parquet", "d3d_shot_203703.parquet", "d3d_shot_203704.parquet"],
    "MAST": ["mast_shot_28348.parquet", "mast_shot_28350.parquet", "mast_shot_28351.parquet"],
}
GITHUB_RAW = f"https://media.githubusercontent.com/media/{STARTER_REPO}"
GITHUB_API = f"https://api.github.com/repos/{STARTER_REPO}/commits/main"


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "PlasmaFluxExplorer/0.1 data-bootstrap"})
    with urllib.request.urlopen(req, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError(f"upstream returned HTTP {response.status}")
        return json.load(response)


def finite_number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def json_safe(value):
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def frames_from(row: dict, config: str) -> list[dict]:
    times = row.get("efit_times") or []
    maps = row.get("efit_psirz") or []
    axes_r, axes_z = row.get("efit_r_axis") or [], row.get("efit_z_axis") or []
    psi_axis = row.get("efit_psi_axis") or []
    psi_boundary = row.get("efit_psi_boundary") or []
    lcfs_n, lcfs_r, lcfs_z = row.get("efit_lcfs_n") or [], row.get("efit_lcfs_r") or [], row.get("efit_lcfs_z") or []
    frames = []
    for i, timestamp in enumerate(times):
        psi = maps[i] if i < len(maps) else None
        # Withheld targets remain absent; time stamps alone are not an equilibrium.
        if not isinstance(psi, list):
            continue
        count = int(lcfs_n[i]) if i < len(lcfs_n) and lcfs_n[i] is not None else 0
        boundary = []
        if i < len(lcfs_r) and i < len(lcfs_z):
            rr, zz = lcfs_r[i], lcfs_z[i]
            if isinstance(rr, list) and isinstance(zz, list):
                for rv, zv in zip(rr[:count or None], zz[:count or None]):
                    rvalue, zvalue = finite_number(rv), finite_number(zv)
                    if rvalue is not None and zvalue is not None:
                        boundary.append([rvalue, zvalue])
        frames.append({
            "time_ms": finite_number(timestamp), "psi": json_safe(psi),
            "R": json_safe(row.get("efit_grid_R")), "Z": json_safe(row.get("efit_grid_Z")),
            "boundary": boundary or None,
            "axis": {"R": finite_number(axes_r[i]) if i < len(axes_r) else None,
                     "Z": finite_number(axes_z[i]) if i < len(axes_z) else None},
            "psi_axis": finite_number(psi_axis[i]) if i < len(psi_axis) else None,
            "psi_boundary": finite_number(psi_boundary[i]) if i < len(psi_boundary) else None,
        })
    return frames


def stable_id(row: dict, machine: str, config: str, revision: str) -> str:
    released = row.get("record_id") or row.get("id") or row.get("shot_id")
    if not released:
        index = row.get("record_index", row.get("index"))
        released = f"{machine}_{index}" if index is not None else f"row-{hashlib.sha256(json.dumps(row, sort_keys=True, default=str).encode()).hexdigest()[:12]}"
    return f"{machine}:{config}:{revision}:{released}"


def decimate_minmax(times, values, maximum_points=1400):
    """Preserve per-bucket extrema and their time order for display-only signals."""
    pairs = [(finite_number(t), finite_number(v), i) for i, (t, v) in enumerate(zip(times or [], values or []))]
    pairs = [pair for pair in pairs if pair[0] is not None and pair[1] is not None]
    if len(pairs) <= maximum_points:
        return [[t, v] for t, v, _ in pairs]
    buckets = max(1, maximum_points // 2)
    result = []
    for bucket in range(buckets):
        start = bucket * len(pairs) // buckets
        end = (bucket + 1) * len(pairs) // buckets
        segment = pairs[start:end]
        if not segment:
            continue
        low, high = min(segment, key=lambda p: p[1]), max(segment, key=lambda p: p[1])
        result.extend(sorted((low, high), key=lambda p: p[2]) if low[2] != high[2] else (low,))
    return [[t, v] for t, v, _ in result]


def thomson_system(row: dict, machine: str, system: str) -> dict | None:
    times = row.get(f"thomson_{system}_times")
    te = row.get(f"thomson_{system}_Te")
    ne = row.get(f"thomson_{system}_ne")
    coordinate = row.get("thomson_core_R" if system == "core" else "thomson_edge_spatial")
    if not isinstance(times, list) or not isinstance(te, list) or not isinstance(ne, list) or not isinstance(coordinate, list):
        return None
    # Both inspected starter Parquets use (time, channel). MAST core R is one
    # channel shorter because its uncalibrated first data channel is NaN.
    aligned = machine == "MAST" and system == "core" and te and len(coordinate) + 1 == len(te[0])
    if aligned:
        te = [row_values[1:] for row_values in te]
        ne = [row_values[1:] for row_values in ne]
    n = min(len(coordinate), len(te[0]) if te else 0, len(ne[0]) if ne else 0)
    if n == 0:
        return None
    return {
        "time_ms": [finite_number(t) for t in times],
        "coordinate_m": [finite_number(x) for x in coordinate[:n]],
        "coordinate_axis": "R" if system == "core" or machine == "MAST" else "Z",
        "Te_eV": [[finite_number(x) for x in values[:n]] for values in te],
        "ne_m3": [[finite_number(x) for x in values[:n]] for values in ne],
        "alignment_note": "Dropped uncalibrated channel 0 to align MAST core Thomson R with Te/ne." if aligned else None,
    }


def diagnostics_from(row: dict, machine: str) -> dict:
    shared_times = row.get("magnetics_time") or []
    coils = []
    for name, values in row.items():
        if not name.startswith("magnetics_") or name in {
            "magnetics_time", "magnetics_plasma_current", "magnetics_plasma_current_times", "magnetics_dsep", "magnetics_dsep_times",
        } or not isinstance(values, list):
            continue
        if len(values) == len(shared_times):
            coils.append({"name": name.removeprefix("magnetics_"), "provenance": "Supplied actuator signal",
                          "native_units": "As released by the challenge", "points": decimate_minmax(shared_times, values)})
    plasma_current = row.get("magnetics_plasma_current")
    ip_times = row.get("magnetics_plasma_current_times") or shared_times
    if isinstance(plasma_current, list) and isinstance(ip_times, list):
        coils.append({"name": "plasma_current", "provenance": "Measured diagnostic",
                      "native_units": "As released by the challenge", "points": decimate_minmax(ip_times, plasma_current)})
    return {
        "coil_signals": coils,
        "thomson": {system: thomson_system(row, machine, system) for system in ("core", "edge")},
        "coil_geometry": {key: json_safe(row.get(key)) for key in ("coil_name", "coil_input_column", "coil_R", "coil_Z", "coil_width", "coil_height") if key in row},
        "thomson_chords": {key: json_safe(row.get(key)) for key in ("thomson_chord_name", "thomson_chord_R", "thomson_chord_Z") if key in row},
    }


def make_record(row: dict, machine: str, config: str, revision: str, source_url: str, raw_path: Path, digest: str) -> dict:
    rid = row.get("record_id") or row.get("id") or row.get("shot_id") or row.get("record_index")
    frames = frames_from(row, config)
    parameter_fields = {
        "beta_n": "efit_beta_n", "beta_p": "efit_beta_p", "internal_inductance": "efit_li",
        "q95": "efit_q95", "efit_elongation": "efit_elongation",
        "geometric_axis_R_m": "efit_geom_axis_r", "geometric_axis_Z_m": "efit_geom_axis_z",
    }
    for idx, frame in enumerate(frames):
        frame["topology"] = topology_candidates(frame)
        frame["geometry"] = boundary_metrics(frame.get("boundary") or [], frame.get("axis")) if frame.get("boundary") else None
        frame["parameters"] = {name: finite_number(row[column][idx]) for name, column in parameter_fields.items()
                                if isinstance(row.get(column), list) and idx < len(row[column])}
        frame["parameters_provenance"] = "EFIT reference reconstruction"
    schema_columns = sorted(row.keys())
    schema_fingerprint = hashlib.sha256(json.dumps(schema_columns, separators=(",", ":")).encode()).hexdigest()
    return {
        "id": stable_id(row, machine, config, revision), "record_id": rid,
        "machine": machine, "configuration": config, "dataset": DATASET if config != "starter_demo" else f"{STARTER_REPO}/parquet_data",
        "revision": revision, "source_url": source_url,
        "raw_path": raw_path.relative_to(ROOT).as_posix(), "sha256": digest,
        "reference_available": bool(frames), "prediction_available": False, "frames": frames,
        "frame_count": len(row.get("efit_times") or []), "times": json_safe(row.get("efit_times") or []),
        "source_columns": schema_columns, "schema_fingerprint": schema_fingerprint,
        "diagnostics": diagnostics_from(row, machine),
    }


def download_file(url: str, destination: Path):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        return
    partial = destination.with_suffix(destination.suffix + ".part")
    existing = partial.stat().st_size if partial.exists() else 0
    headers = {"User-Agent": "PlasmaFluxExplorer/0.1 data-bootstrap"}
    if existing:
        headers["Range"] = f"bytes={existing}-"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=180) as response:
        if response.status not in (200, 206):
            raise RuntimeError(f"download returned HTTP {response.status}: {url}")
        if response.status == 200 and existing:
            existing = 0
        mode = "ab" if response.status == 206 and existing else "wb"
        with partial.open(mode) as output:
            shutil.copyfileobj(response, output, length=1024 * 1024)
    partial.replace(destination)


def starter_revision() -> str:
    try:
        return get_json(GITHUB_API).get("sha") or "main"
    except Exception as exc:
        print(f"Warning: starter-kit revision lookup failed ({exc}); recording 'main' and file hashes.", file=sys.stderr)
        return "main"


def starter_demo_records(args) -> tuple[list[dict], str]:
    revision = starter_revision()
    machines = args.machine or ["DIII-D", "MAST"]
    records = []
    for machine in machines:
        files = DEMO_FILES[machine][args.offset:args.offset + args.max_shots]
        if not files:
            print(f"{machine}: requested offset has no demo records", file=sys.stderr)
            continue
        for filename in files:
            upstream = f"parquet_data/{filename}"
            url = f"{GITHUB_RAW}/{revision}/{upstream}"
            path = ROOT / "data/raw/starter-demo" / revision / filename
            legacy_path = ROOT / "data/raw/starter-demo" / filename
            if not path.exists() and legacy_path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(legacy_path, path)
            try:
                download_file(url, path)
                table = parquet.read_table(path)
                if table.num_rows != 1:
                    raise ValueError(f"expected one shot row, found {table.num_rows}")
                row = table.to_pylist()[0]
            except Exception as exc:
                raise SystemExit(f"{machine} {filename}: unable to read official starter record: {exc}")
            if row.get("source") != machine:
                raise SystemExit(f"{filename}: expected source {machine!r}, found {row.get('source')!r}")
            # The official filename includes the demo shot identifier.
            shot = filename.split("shot_", 1)[1].removesuffix(".parquet")
            row["record_id"] = f"{machine}_{shot}"
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            record = make_record(row, machine, "starter_demo", revision, url, path, digest)
            record["source_file"] = upstream
            records.append(record)
            print(f"{machine} {record['record_id']}: {len(record['frames'])} EFIT reference frames · sha256 {digest[:12]}")
    return records, revision


def challenge_records(args) -> tuple[list[dict], str]:
    configs = args.config or ["diii_d_train", "mast_public_test"]
    try:
        revision = get_json("https://huggingface.co/api/datasets/" + DATASET).get("sha") or "main"
    except Exception as exc:
        print(f"Warning: dataset revision lookup failed ({exc}); pin recorded as 'main'.", file=sys.stderr)
        revision = "main"
    raw_root = ROOT / "data/raw" / revision
    raw_root.mkdir(parents=True, exist_ok=True)
    records = []
    for config in configs:
        machine, split = CONFIGS[config]
        rows = []
        for page_start in range(args.offset, args.offset + args.max_shots, 100):
            length = min(100, args.offset + args.max_shots - page_start)
            params = urllib.parse.urlencode({"dataset": DATASET, "config": config, "split": split, "offset": page_start, "length": length})
            url = f"{ENDPOINT}?{params}"
            try:
                result = get_json(url)
            except urllib.error.HTTPError as exc:
                raise SystemExit(f"{config}: Hugging Face returned HTTP {exc.code}; existing catalog was not changed. Try again later.")
            except Exception as exc:
                raise SystemExit(f"{config}: unable to fetch official rows: {exc}")
            if result.get("error"):
                raise SystemExit(f"{config}: official service error: {result['error']}")
            page = result.get("rows", [])
            if not page:
                break
            rows.extend(page[:length])
        if not rows:
            print(f"{config}: no rows returned at offset {args.offset}", file=sys.stderr)
            continue
        params = urllib.parse.urlencode({"dataset": DATASET, "config": config, "split": split, "offset": args.offset, "length": len(rows)})
        url = f"{ENDPOINT}?{params}"
        for entry in rows[:args.max_shots]:
            row = entry.get("row", entry)
            serialized = json.dumps(row, separators=(",", ":"), ensure_ascii=False, default=str)
            digest = hashlib.sha256(serialized.encode()).hexdigest()
            raw_path = raw_root / f"{config}-{digest[:16]}.json"
            raw_path.write_text(json.dumps({"dataset": DATASET, "revision": revision, "config": config,
                                            "source_url": url, "sha256": digest, "row": json_safe(row)},
                                           separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n")
            record = make_record(row, machine, config, revision, url, raw_path, digest)
            records.append(record)
            print(f"{config}: {record['record_id']} · {len(record['frames'])} reference frames · sha256 {digest[:12]}")
        time.sleep(.2)
    return records, revision


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--":
        sys.argv.pop(1)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("starter-demo", "challenge"), default="starter-demo",
                        help="Default uses real official demo Parquet; challenge uses the Hugging Face row API")
    parser.add_argument("--machine", choices=("DIII-D", "MAST"), action="append",
                        help="Starter-demo mode only; may be repeated. Default selects both machines.")
    parser.add_argument("--config", choices=CONFIGS.keys(), action="append",
                        help="Challenge mode only; may be repeated.")
    parser.add_argument("--max-shots", type=int, default=1, help="Maximum rows/files per selected config or machine (default 1)")
    parser.add_argument("--offset", type=int, default=0, help="Starting row/file index for deterministic selection")
    args = parser.parse_args()
    if args.max_shots < 1 or args.offset < 0:
        parser.error("--max-shots must be >= 1 and --offset >= 0")
    if args.source == "starter-demo" and args.config:
        parser.error("--config requires --source challenge")
    if args.source == "challenge" and args.machine:
        parser.error("--machine is for --source starter-demo")
    records, revision = starter_demo_records(args) if args.source == "starter-demo" else challenge_records(args)
    if not records:
        raise SystemExit("No records were ingested; the existing catalog was not changed.")
    catalog_path = ROOT / "data/processed/catalog.json"
    old = []
    if catalog_path.exists():
        try:
            old = json.loads(catalog_path.read_text()).get("records", [])
        except (OSError, json.JSONDecodeError):
            pass
    merged = {record["id"]: record for record in old}
    merged.update({record["id"]: record for record in records})
    revisions = sorted({record.get("revision", revision) for record in merged.values()})
    catalog = {
        "schema_version": "1.0.0", "dataset": "Fusion Equilibrium Challenge and official starter-kit demo Parquet",
        "revision": revisions[0] if len(revisions) == 1 else "MULTIPLE", "records": list(merged.values()),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = catalog_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(catalog, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n")
    temporary.replace(catalog_path)
    print(f"Catalog updated: {catalog_path.relative_to(ROOT)} ({len(merged)} records; "
          f"{sum(len(record['frames']) for record in records)} available reference frames)")


if __name__ == "__main__":
    main()
