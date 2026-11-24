# Architecture

## Runtime

- `app/` contains the Next.js App Router shell, static research routes served through the root workspace, and catalog-backed research API handlers.
- `public/app.js` owns high-frequency canvas interaction and compact workspace state. `app/workspace.css` contains the dark instrument theme; Tailwind CSS is available for route-level utility styling.
- `scientific/` contains pure Python calculations, independent of browser rendering.
- `scripts/` contains bounded upstream selection and catalog validation.
- `data/raw/<revision>/` retains fetched source rows; `data/processed/catalog.json` is the compact browser index. Local artifacts are ignored by Git.

`lib/catalog.ts` resolves the catalog from the OpenNext `PFE_DATA` R2 binding and falls back to the local generated file during plain Next.js development. Local development needs no credentials. Frame arrays are stored inline in the curated catalog, which is intended for the starter selection rather than full-corpus delivery.

## Data flow

1. The bootstrap resolves the source revision and requests only the configured row limit from the official Dataset Viewer.
2. It preserves the response as a raw JSON record with source URL, configuration, revision, and checksum.
3. The processed index retains EFIT flux only when the row supplies it. Test configurations with withheld targets produce no reference frames.
4. The browser reads the index, draws the supplied grid, and labels supplied EFIT geometry separately from calculations.
5. Exports include record identity, revision, source provenance, timestamp, and physical units.

The viewer does not synthesize a missing equilibrium frame, bridge time gaps, or substitute an analytical field for a selected source record. The unselected teaching field is explicitly synthetic.

## Routes

`/`, `/explorer`, `/flux-lab`, `/magnetic-geometry`, `/plasma-geometry`, `/diagnostics`, `/compare`, `/predictions`, `/catalog`, `/sources`, `/methodology`, and `/settings` are reloadable workspace routes.

The API includes `/api/health`, bounded `/api/catalog` pagination and filters, `/api/datasets`, `/api/machines`, record metadata, bounded frames, per-frame equilibrium and topology, geometry, coils, diagnostics, predictions, model registry, and provenance routes under `/api/discharges/:id` and `/api/provenance/:artifact`. Unavailable predictions return an explicit empty state; no model results are fabricated.
