# Prediction integration

The browser accepts numeric JSON prediction artifacts only. It never evaluates code or deserializes pickle files. Imports stay in browser memory for the current session and are not uploaded.

## Schema 1.0.0

Each artifact identifies one exact local catalog record and dataset revision. It contains a model ID/name and version, the psi unit, strictly increasing R and Z coordinates in metres, timestamps in milliseconds matching the record in order, and one finite Z-by-R psi grid per timestamp. Optional per-frame `axis` and `boundary` values are predictions and must not be treated as EFIT reference labels.

```json
{
  "schema_version": "1.0.0",
  "record_id": "DIII-D:starter_demo:main:DIII-D_203702",
  "dataset_revision": "main",
  "model": { "id": "example-baseline", "version": "1.0.0" },
  "units": { "psi": "Wb/rad" },
  "R": [0.8, 0.9],
  "Z": [-1.0, 0.0],
  "timestamps_ms": [100.0],
  "frames": [
    {
      "time_ms": 100.0,
      "psi": [
        [0.1, 0.2],
        [0.3, 0.4]
      ]
    }
  ]
}
```

The short arrays above illustrate the contract only; a real import must match every timestamp and the source grid coordinates when reference grids exist. For labeled records, the explorer can show the reference, model prediction, or absolute residual. Residual mode is disabled in meaning when the reference is withheld and reports that requirement. Model outputs retain model-predicted provenance, and no confidence values are inferred.

This importer validates shape, finite values, coordinate monotonicity, timestamp correspondence, record identity, revision, and required model/unit metadata. It does not assess model accuracy, calibration, topology validity, or physical correctness. Those require separate reference validation.
