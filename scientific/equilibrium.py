"""Small, documented axisymmetric geometry calculations.

These functions operate on source-provided EFIT values and/or explicitly
supplied boundary contours. They do not infer missing experimental labels.
Flux normalization follows the challenge's EFIT convention and rejects
ill-conditioned axis-to-boundary intervals.
"""
from __future__ import annotations
import math

def normalize_flux(psi, psi_axis: float, psi_boundary: float, *, rtol: float = 1e-12):
    """Return ψN=(ψ−ψaxis)/(ψboundary−ψaxis), or None if invalid.

    Supports either orientation (positive or negative denominator). Nonfinite
    pixels stay None so the renderer cannot mistake missing values for zero.
    """
    try: den=float(psi_boundary)-float(psi_axis)
    except (TypeError,ValueError): return None
    scale=max(abs(float(psi_axis)),abs(float(psi_boundary)),1.0)
    if not math.isfinite(den) or abs(den)<=rtol*scale: return None
    def one(v):
        try:
            x=float(v)
            return (x-float(psi_axis))/den if math.isfinite(x) else None
        except (TypeError,ValueError): return None
    if isinstance(psi,(list,tuple)):
        return [normalize_flux(row,psi_axis,psi_boundary,rtol=rtol) if isinstance(row,(list,tuple)) else one(row) for row in psi]
    return one(psi)

def polygon_area(points) -> float | None:
    """Absolute shoelace area in m² for an ordered, closed or open R-Z contour."""
    pts=[(float(p[0]),float(p[1])) for p in points if len(p)>=2 and all(math.isfinite(float(x)) for x in p[:2])]
    if len(pts)<3:return None
    if pts[0]!=pts[-1]:pts.append(pts[0])
    return abs(sum(pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1] for i in range(len(pts)-1)))/2

def axisymmetric_volume(points) -> float | None:
    """Pappus volume V=2π R̄ A for a simple poloidal cross-section.

    Assumes an axisymmetric torus, a simple non-self-intersecting contour,
    and rotation about R=0. It is invalid for an open boundary or clipped wall.
    """
    area=polygon_area(points)
    pts=[(float(p[0]),float(p[1])) for p in points if len(p)>=2]
    if area is None or len(pts)<3:return None
    if pts[0]==pts[-1]:pts=pts[:-1]
    # Polygon centroid R coordinate, area-weighted shoelace centroid.
    if len(pts)<3:return None
    cross=[pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts))]
    signed=sum(cross)
    if abs(signed)<1e-15:return None
    rbar=sum((pts[i][0]+pts[(i+1)%len(pts)][0])*cross[i] for i in range(len(pts)))/(3*signed)
    return 2*math.pi*rbar*area if rbar>0 else None

def elongation(points) -> float | None:
    """κ=vertical full extent / horizontal full extent of supplied contour."""
    try:rs=[float(p[0]) for p in points];zs=[float(p[1]) for p in points]
    except (TypeError,ValueError,IndexError):return None
    if not rs or not zs:return None
    width=max(rs)-min(rs);height=max(zs)-min(zs)
    return height/width if width>0 and height>0 else None

def triangularity(points, magnetic_axis_r: float) -> dict[str,float] | None:
    """Top/bottom triangularity from extremal Z points and horizontal half-width.

    δ=(Raxis−Redge)/a, where Raxis is EFIT Raxis, Redge is the R location at
    top/bottom Z extremum, and a is half the total R extent. This simple sampled
    boundary functional is grid-dependent; it does not interpolate the contour.
    """
    try:pts=[(float(p[0]),float(p[1])) for p in points]
    except (TypeError,ValueError,IndexError):return None
    if len(pts)<3:return None
    a=(max(p[0] for p in pts)-min(p[0] for p in pts))/2
    if a<=0:return None
    top=max(pts,key=lambda p:p[1]);bottom=min(pts,key=lambda p:p[1])
    axis=float(magnetic_axis_r)
    return {"top":(axis-top[0])/a,"bottom":(axis-bottom[0])/a}

def boundary_metrics(points, axis=None) -> dict | None:
    """Calculate auditable shape metrics from an ordered, supplied LCFS polygon.

    The geometric center uses the bounding-box midpoints. R0 follows the
    challenge plan's (Rmax+Rmin)/2 definition; volume uses the area centroid
    through Pappus' theorem. This assumes a simple closed contour about R=0.
    """
    try:
        pts=[(float(p[0]),float(p[1])) for p in points]
        if any(not math.isfinite(r) or not math.isfinite(z) for r,z in pts): return None
    except (TypeError,ValueError,IndexError): return None
    if len(pts)>1 and pts[0]==pts[-1]: pts=pts[:-1]
    if len(pts)<3:return None
    rs=[p[0] for p in pts];zs=[p[1] for p in pts]
    rmin,rmax,zmin,zmax=min(rs),max(rs),min(zs),max(zs)
    r0=(rmax+rmin)/2;a=(rmax-rmin)/2;height=zmax-zmin
    area=polygon_area(pts);volume=axisymmetric_volume(pts)
    if a<=0 or height<=0 or area is None:return None
    perimeter=sum(math.hypot(pts[(i+1)%len(pts)][0]-pts[i][0],pts[(i+1)%len(pts)][1]-pts[i][1]) for i in range(len(pts)))
    top=max(pts,key=lambda p:p[1]);bottom=min(pts,key=lambda p:p[1])
    triangularity_top=(r0-top[0])/a;triangularity_bottom=(r0-bottom[0])/a
    axis_r=axis.get("R") if isinstance(axis,dict) else None
    axis_z=axis.get("Z") if isinstance(axis,dict) else None
    return {
        "geometric_center":{"R_m":r0,"Z_m":(zmax+zmin)/2},
        "magnetic_axis":{"R_m":axis_r,"Z_m":axis_z},
        "extents":{"R_min_m":rmin,"R_max_m":rmax,"Z_min_m":zmin,"Z_max_m":zmax},
        "minor_radius_m":a,"major_radius_m":r0,
        "aspect_ratio":r0/a if r0>0 else None,"inverse_aspect_ratio":a/r0 if r0>0 else None,
        "elongation":height/(2*a),"triangularity":{"upper":triangularity_top,"lower":triangularity_bottom,"mean":(triangularity_top+triangularity_bottom)/2},
        "cross_sectional_area_m2":area,"boundary_perimeter_m":perimeter,"axisymmetric_volume_m3":volume,
        "vertical_displacement_m":axis_z-(zmax+zmin)/2 if axis_z is not None else None,
        "provenance":"Derived from EFIT reference reconstruction",
        "method":"Shoelace area; Pappus volume from polygon area centroid; bounding-box R0/a/elongation; upper/lower triangularity at sampled Z extrema.",
    }

def topology_candidates(frame: dict, *, gradient_rtol: float = 2e-3) -> dict:
    """Inspect the source grid for discrete extrema and bilinear saddle points.

    This conservative grid-level search returns candidate locations only. It
    does not infer divertor regions or claim a complete separatrix topology.
    Coordinates are interpolated within source cells and carry an explicit
    sampling-resolution quality flag.
    """
    grid=frame.get("psi");rs=frame.get("R");zs=frame.get("Z")
    result={"o_points":[],"x_points":[],"quality":"unavailable","method":"grid-local extrema and bilinear-cell stationary points"}
    if not isinstance(grid,list) or len(grid)<2 or not isinstance(rs,list) or not isinstance(zs,list):return result
    if len(grid)!=len(zs) or any(not isinstance(row,list) or len(row)!=len(rs) for row in grid):return result
    try:
        values=[[float(v) for v in row] for row in grid]
        if any(not math.isfinite(v) for row in values for v in row):return result
    except (TypeError,ValueError):return result
    scale=max(max(row) for row in values)-min(min(row) for row in values)
    tol=max(scale*gradient_rtol,1e-14)
    # Local 8-neighbour extrema are deliberately candidates, not refined axes.
    for j in range(1,len(zs)-1):
        for i in range(1,len(rs)-1):
            value=values[j][i];neighbours=[values[y][x] for y in range(j-1,j+2) for x in range(i-1,i+2) if (x,y)!=(i,j)]
            if value<=min(neighbours) and max(neighbours)-value>tol:result["o_points"].append({"R_m":rs[i],"Z_m":zs[j],"psi":value,"classification":"minimum","quality":"grid candidate; not sub-grid refined"})
            elif value>=max(neighbours) and value-min(neighbours)>tol:result["o_points"].append({"R_m":rs[i],"Z_m":zs[j],"psi":value,"classification":"maximum","quality":"grid candidate; not sub-grid refined"})
    # A bilinear interpolant has an analytic stationary point in a cell when
    # its mixed term is nonzero; its Hessian determinant is negative (saddle).
    seen=[]
    for j in range(len(zs)-1):
        for i in range(len(rs)-1):
            q00,q10=values[j][i],values[j][i+1];q01,q11=values[j+1][i],values[j+1][i+1]
            mixed=q11-q10-q01+q00
            if abs(mixed)<=tol:continue
            u=-(q01-q00)/mixed;v=-(q10-q00)/mixed
            if not (0<u<1 and 0<v<1):continue
            point={"R_m":rs[i]+u*(rs[i+1]-rs[i]),"Z_m":zs[j]+v*(zs[j+1]-zs[j]),
                   "psi":q00+(q10-q00)*u+(q01-q00)*v+mixed*u*v,
                   "classification":"saddle","gradient_residual":"zero for bilinear cell interpolant",
                   "quality":"candidate; bilinear interpolation at source-grid resolution"}
            if not any(math.hypot(point["R_m"]-p["R_m"],point["Z_m"]-p["Z_m"])<1e-8 for p in seen):
                result["x_points"].append(point);seen.append(point)
    result["quality"]="candidate topology; source grid not sub-grid refined" if result["o_points"] or result["x_points"] else "no stationary candidate resolved at source-grid resolution"
    return result
