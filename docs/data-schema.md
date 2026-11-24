# Data schema

The local index uses schema version `1.0.0` and identifies the upstream dataset as `Sophelio/fusion-equilibrium-challenge`.

Each catalog record includes:

| Field                                          | Meaning                                                                                                 |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `id`                                           | Stable key: machine, config, revision, and source released record ID/index                              |
| `record_id`                                    | Released source identifier when supplied; never an inferred experimental shot number                    |
| `machine`                                      | Machine identifier, currently `DIII-D` or `MAST`                                                        |
| `configuration`                                | Challenge configuration or the explicitly labeled `starter_demo` configuration                          |
| `revision`, `source_url`, `sha256`, `raw_path` | Traceable upstream provenance and immutable raw-row reference                                           |
| `reference_available`                          | True only when at least one EFIT flux frame is present in the source row                                |
| `prediction_available`                         | False until a model output is explicitly imported and validated                                         |
| `frame_count`, `times`                         | Released EFIT timebase; timestamps may exist even when test targets are withheld                        |
| `frames`                                       | Available target frames only; each contains `time_ms`, `psi`, `R`, `Z`, optional supplied axis and LCFS |
| `diagnostics`                                  | Source signal arrays retained with their own timebases                                                  |

Grid semantics follow the official challenge card: `efit_grid_R` labels columns and `efit_grid_Z` labels rows. Each frame preserves this order and the original coordinate vectors. Flux units are V·s/rad; R and Z are metres; all supplied time arrays are milliseconds. The application does not reinterpret an unavailable target as a zero-valued grid.

EFIT-derived axis and LCFS fields are present only when supplied by the source record. Challenge public-test rows withhold these targets; the separate official starter demo files include reference frames for visualization. A prediction must be a separate artifact with a model identifier and cannot set `reference_available`.
