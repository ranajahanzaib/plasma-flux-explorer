# Equilibrium processing methods

## Grid semantics

The released EFIT grid consists of `efit_grid_R`, `efit_grid_Z`, and per-frame `efit_psirz`. Rows are retained in the source nested-array ordering; coordinate vectors are stored with each frame. The catalog validator checks shape agreement, finite coordinates, and strict monotonicity. It does not transpose a grid based on shape. The viewer indexes the first array dimension against Z and the second against R, as required by this contract. A schema or orientation mismatch is reported instead of silently repaired.

## Flux normalization

When axis and boundary flux values are available, normalized poloidal flux is ψN=(ψ−ψaxis)/(ψboundary−ψaxis). Both signs of the denominator are valid. A near-zero denominator or nonfinite input yields an unavailable result; missing pixels remain missing. ψN is not normalized toroidal flux. The current viewer displays a field color scale and only uses ψN labels where its metadata says the normalization is established.

## Contours and geometry

The browser view uses linearly interpolated marching-squares segments on the original grid. Segments are drawn for display; no smoothing adds measurement resolution. A source-provided LCFS can be overlaid separately and retains its EFIT provenance. The helper functions in `scientific/equilibrium.py` document polygon area (shoelace), axisymmetric volume (Pappus centroid theorem), elongation, and sampled top/bottom triangularity. They require a valid simple boundary and do not repair self-intersections.

## Failure states

Unavailable axes, ambiguous contours, incomplete coordinates, and withheld targets remain unavailable. The product does not bridge gaps between EFIT frame times. Coil and Thomson signals retain their own timestamps; any future resampling must name its method and preserve the original samples.

# Derived geometry and topology candidates

For frames with a source LCFS contour, geometry processing records the bounding-box geometric center, minor/major radius, aspect ratios, elongation, sampled upper/lower triangularity, shoelace area, polygon perimeter, Pappus axisymmetric volume from the area centroid, and vertical displacement from the geometric center. The magnetic axis remains a separate EFIT-provided coordinate. The catalog records the formula summary and marks these values as derived from EFIT reference reconstruction.

Topology processing is a conservative grid-resolution investigation, not complete topology extraction. Eight-neighbour local extrema are listed as O-point candidates. Each bilinear cell is checked for an interior stationary point; for a nonzero mixed term its interpolant has a saddle. Candidate coordinates and the quality string are retained. The method does not refine candidates below grid spacing, prove contour connectivity, or identify a primary/secondary separatrix. Edge extrema can be artifacts and require review.
