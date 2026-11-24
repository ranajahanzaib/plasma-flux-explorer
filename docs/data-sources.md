# Data sources

## Primary dataset

Plasma Flux Explorer uses the [Fusion Equilibrium Challenge dataset](https://huggingface.co/datasets/Sophelio/fusion-equilibrium-challenge) from the Hugging Face dataset repository. The [official starter kit](https://github.com/Sophelio/fusion-equilibrium-challenge-starter) documents the configurations, nested Parquet row structure, timing conventions, and known v1.1.0 input errata.

Supported configurations are `diii_d_train`, `diii_d_public_test`, and `mast_public_test`. A shot is one row; timeseries and 65×65 flux grids are nested arrays. Times are milliseconds. The bootstrap stores the dataset revision, configuration, source URL, record identity, and SHA-256 digest alongside every raw row.

The browser application never labels public test targets as references. DIII-D training rows can include EFIT reference reconstructions. DIII-D and MAST public test equilibrium targets are withheld. MAST's released challenge data has no training configuration. Therefore a MAST public test record has diagnostics but no reference flux frame unless an independently sourced artifact is explicitly imported and provenance-tagged.

## Local starter selection

`pnpm data:bootstrap` downloads one official starter-kit Parquet demo for each machine by default: DIII-D shot 203702 and MAST shot 28348. The starter-kit demos include EFIT frames for visualizing the released equilibrium reference; the MAST demo must not be described as a MAST challenge training split. Files are kept beneath `data/raw/starter-demo/<starter-revision>/`, and the curated records go to `data/processed/catalog.json`. The catalog records the upstream URL, revision, SHA-256 digest, and demo configuration.

Use `pnpm data:bootstrap -- --source challenge` to request bounded rows from the Hugging Face Dataset Viewer. It defaults to `diii_d_train` and `mast_public_test`; use repeated `--config` flags to choose configs. Challenge public-test targets remain withheld. The bootstrap never silently advances after a failed request or fabricates measurements.

The Dataset Viewer can temporarily stop row jobs during load. In that case the command reports the upstream error and leaves the existing catalog unchanged. Full dataset ingestion is deliberately not part of local setup.

## Limitations and attribution

The dataset is a challenge release and its own license/terms apply; the repository's MIT license does not relicense source data. Cite the dataset and challenge authors when publishing results. Source shot numbers are not derived from challenge row order. Stable local IDs combine machine, configuration, dataset revision, and released record identity.

The official starter kit documents two v1.1.0 input errata: DIII-D plasma-current time-axis correction and MAST Thomson core channel alignment. The UI preserves DIII-D's released plasma-current timebase as-is and does not apply the optional correction. For the MAST demo, it drops the documented uncalibrated core Thomson channel 0 so the 130 coordinate positions align with the 131 Te/ne values; this is recorded in the catalog. Signal plots retain independent diagnostic time bases, and Thomson display chooses the nearest released sample without temporal interpolation. Actuator coil inputs and measured plasma current are labeled separately.
