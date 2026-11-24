# Ingestion

Run `pnpm data:bootstrap` to download the official starter-kit demo Parquet file for DIII-D shot 203702 and MAST shot 28348. These labeled visualization examples are separate from the challenge splits. To request challenge rows, add `--source challenge`; this mode defaults to one DIII-D training row and one MAST public-test row. A small bounded selection keeps development independent of the full corpus. Use repeated `--config` flags, `--max-shots N`, and `--offset N` to select another reproducible range.

In starter-demo mode, the script downloads the selected files from the official starter kit, records the resolved source revision, hashes the raw rows, writes them beneath `data/raw/starter-demo/<revision>/`, and updates the processed index after successful processing. In challenge mode, it requests the official Hugging Face Dataset Viewer row endpoint in pages of at most 100 and records the resolved dataset commit SHA where available. Re-running an identical selection is safe because row artifacts are content-addressed by digest and records merge by stable ID.

If an upstream request fails, the command exits with an actionable message and does not replace the prior processed catalog. Interrupted challenge requests can be retried with the same offset. Challenge mode uses the Dataset Viewer JSON row API; direct challenge Parquet shard ingestion, Hugging Face streaming client integration, and full-corpus job orchestration are outside the current implementation.

Validate the local index with `pnpm data:validate`. The validator checks schema version, unique identifiers, source provenance, frame/grid dimensions, finite strictly increasing coordinates, and the rule that public test records cannot claim reference labels.
