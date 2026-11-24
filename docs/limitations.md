# Current limitations

Plasma Flux Explorer focuses on transparent exploration of the released challenge data and its official starter examples. The following limits define the current scope.

- Ingestion supports the official starter-kit Parquet demos and bounded Dataset Viewer rows. Full-corpus streaming, schema migration tooling, and a signed artifact store are not included.
- The 2D grid viewer, interpolated contours, pan/zoom, layers, URL routes, and frame controls are available. Grid-resolution stationary candidates and an axisymmetric Canvas surface from the selected LCFS are also available. Sub-grid stationary refinement, robust X-point/LCFS extraction, field-aligned topology, and measured machine-wall geometry are outside scope.
- Coil/plasma-current traces and nearest-sample Thomson profiles use their source time bases. The optional DIII-D plasma-current timing correction is not applied. The documented MAST core channel 0 alignment is handled and recorded; calibration and broader diagnostic validation are not provided.
- Cross-machine boundary/shape comparison and session-only prediction JSON import are available. Imported predictions are checked for schema and grid alignment, but not model accuracy, calibration, or physical correctness. Predictions are not persisted.
- Geometry measurements are calculated from supplied LCFS contours. They describe the source geometry and do not constitute independent experimental validation.
- JSON frame export is available. CSV, Parquet, Arrow, NPZ, image, and glTF exports are not included.
- Cloudflare Worker configuration, local R2 preview, catalog publishing, and validation CI are included. Rate limiting, external error monitoring, large-catalog artifact sharding, and hosted production verification are not part of this release.
- The interface supports responsive layouts. Accessibility testing across a full viewport matrix and assistive technologies is not documented as complete.

Unavailable measurements, withheld labels, and unsupported scientific conclusions must remain unavailable until the corresponding source data and validated algorithms are added.
