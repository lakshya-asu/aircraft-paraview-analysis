"""
Aircraft STL Analysis using ParaView 6
Analyzes ATR_x and Fighter Jet Concept models:
  - Geometric measurements (bounding box, surface area, volume)
  - Mesh statistics (triangles, vertices, quality)
  - Visual screenshots (7 camera angles + curvature + wireframe)
  - JSON results export
"""

import os
import sys
import json
import math

# Offscreen rendering before any paraview import
import paraview
paraview.options.offscreen = True

from paraview.simple import (
    STLReader, Curvature, MeshQuality,
    Show, Hide, ResetSession, GetActiveViewOrCreate,
    ColorBy, GetColorTransferFunction, GetScalarBar,
    SaveScreenshot, Render,
)
# ParaView 6 renamed GenerateSurfaceNormals -> SurfaceNormals
try:
    from paraview.simple import SurfaceNormals as _SurfaceNormals
    def GenerateSurfaceNormals(**kwargs):
        return _SurfaceNormals(**kwargs)
except ImportError:
    from paraview.simple import GenerateSurfaceNormals
from paraview import servermanager

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
REPO_DIR     = os.path.dirname(SCRIPT_DIR)
RESULTS_DIR  = os.path.join(REPO_DIR, "results")
SHOTS_DIR    = os.path.join(RESULTS_DIR, "screenshots")

MODELS = {
    "ATR_x": {
        "stl":    os.path.join(REPO_DIR, "models", "ATR_x.stl"),
        "prefix": "atr_x",
        "color":  [0.55, 0.75, 0.92],   # steel blue
        "desc":   "ATR turboprop regional aircraft concept",
    },
    "Fighter_Jet": {
        "stl":    os.path.join(REPO_DIR, "models", "Fighter_jet_concept.stl"),
        "prefix": "fighter_jet",
        "color":  [0.92, 0.72, 0.40],   # warm sand
        "desc":   "Fighter jet concept",
    },
}

# ── Camera helpers ────────────────────────────────────────────────────────────
def camera_views(bounds):
    """Return 9 named camera (position, focal_point, view_up) tuples."""
    cx = (bounds[0] + bounds[1]) / 2
    cy = (bounds[2] + bounds[3]) / 2
    cz = (bounds[4] + bounds[5]) / 2
    diag = math.sqrt(
        (bounds[1] - bounds[0]) ** 2 +
        (bounds[3] - bounds[2]) ** 2 +
        (bounds[5] - bounds[4]) ** 2
    )
    d = diag * 1.9
    return {
        "front":        ([cx,       cy - d,       cz],         [cx, cy, cz], [0, 0, 1]),
        "rear":         ([cx,       cy + d,       cz],         [cx, cy, cz], [0, 0, 1]),
        "left":         ([cx - d,   cy,           cz],         [cx, cy, cz], [0, 0, 1]),
        "right":        ([cx + d,   cy,           cz],         [cx, cy, cz], [0, 0, 1]),
        "top":          ([cx,       cy,           cz + d],     [cx, cy, cz], [0, 1, 0]),
        "bottom":       ([cx,       cy,           cz - d],     [cx, cy, cz], [0, 1, 0]),
        "perspective":  ([cx + d*0.7, cy - d*0.7, cz + d*0.5],[cx, cy, cz], [0, 0, 1]),
    }


# ── VTK geometry (surface area + volume) ─────────────────────────────────────
def vtk_mass_properties(stl_path):
    """Compute surface area and volume via raw VTK pipeline."""
    try:
        from vtkmodules.vtkIOGeometry    import vtkSTLReader
        from vtkmodules.vtkFiltersCore   import vtkTriangleFilter, vtkMassProperties
    except ImportError:
        try:
            from paraview.vtk.vtkIOGeometry  import vtkSTLReader    # noqa
            from paraview.vtk.vtkFiltersCore import vtkTriangleFilter, vtkMassProperties  # noqa
        except ImportError:
            from vtk import vtkSTLReader, vtkTriangleFilter, vtkMassProperties  # noqa

    r = vtkSTLReader()
    r.SetFileName(stl_path)
    r.Update()

    tri = vtkTriangleFilter()
    tri.SetInputConnection(r.GetOutputPort())
    tri.Update()

    mp = vtkMassProperties()
    mp.SetInputConnection(tri.GetOutputPort())
    mp.Update()

    return {
        "surface_area": round(mp.GetSurfaceArea(), 4),
        "volume":       round(mp.GetVolume(),       4),
    }


# ── Per-model analysis ────────────────────────────────────────────────────────
def analyze(name, cfg):
    print(f"\n{'='*60}\nAnalyzing: {name}\n{'='*60}")
    stl_path = cfg["stl"]
    prefix   = cfg["prefix"]
    color    = cfg["color"]

    ResetSession()

    # Load STL
    reader = STLReader(FileNames=[stl_path])
    reader.UpdatePipeline()
    info     = reader.GetDataInformation()
    bounds   = info.GetBounds()            # xmin xmax ymin ymax zmin zmax
    n_cells  = info.GetNumberOfCells()
    n_points = info.GetNumberOfPoints()

    lx = bounds[1] - bounds[0]
    ly = bounds[3] - bounds[2]
    lz = bounds[5] - bounds[4]
    center = [
        round((bounds[0] + bounds[1]) / 2, 4),
        round((bounds[2] + bounds[3]) / 2, 4),
        round((bounds[4] + bounds[5]) / 2, 4),
    ]

    print(f"  Triangles : {n_cells:,}")
    print(f"  Vertices  : {n_points:,}")
    print(f"  Length X  : {lx:.4f}")
    print(f"  Length Y  : {ly:.4f}")
    print(f"  Length Z  : {lz:.4f}")
    print(f"  Center    : {center}")

    # Mass properties
    geo = vtk_mass_properties(stl_path)
    print(f"  Surface Area : {geo['surface_area']:.4f}")
    print(f"  Volume (est) : {geo['volume']:.4f}")

    # ParaView filters
    normals   = GenerateSurfaceNormals(Input=reader)
    normals.UpdatePipeline()

    curvature = Curvature(Input=normals)
    curvature.CurvatureType = "Mean"
    curvature.UpdatePipeline()

    # ── Render setup ──────────────────────────────────────────────────────────
    view = GetActiveViewOrCreate("RenderView")
    view.ViewSize               = [1920, 1080]
    view.Background             = [0.10, 0.11, 0.16]
    view.Background2            = [0.03, 0.03, 0.08]
    view.BackgroundColorMode    = "Gradient"

    views = camera_views(bounds)
    shots = []

    # ── 1. Surface-with-edges (7 angles) ─────────────────────────────────────
    disp = Show(normals, view)
    disp.Representation = "Surface With Edges"
    disp.AmbientColor   = color
    disp.DiffuseColor   = color
    disp.EdgeColor      = [0.08, 0.08, 0.08]
    disp.LineWidth      = 0.5
    disp.ColorArrayName = ["POINTS", ""]   # solid color, no scalar mapping
    view.ResetCamera()

    for vname, (pos, fpt, vup) in views.items():
        view.CameraPosition  = pos
        view.CameraFocalPoint = fpt
        view.CameraViewUp    = vup
        path = os.path.join(SHOTS_DIR, f"{prefix}_{vname}.png")
        SaveScreenshot(path, view, ImageResolution=[1920, 1080])
        shots.append(os.path.relpath(path, REPO_DIR))
        print(f"  Shot: {vname}")

    Hide(normals, view)

    # ── 2. Curvature heat-map ─────────────────────────────────────────────────
    cd = Show(curvature, view)
    cd.Representation = "Surface"
    ColorBy(cd, ("POINTS", "Mean_Curvature"))
    cd.RescaleTransferFunctionToDataRange(True)

    lut = GetColorTransferFunction("Mean_Curvature")
    lut.ApplyPreset("Cool to Warm", True)

    bar = GetScalarBar(lut, view)
    bar.Title           = "Mean Curvature"
    bar.ComponentTitle  = ""
    bar.Visibility      = 1
    bar.ScalarBarLength = 0.6

    pos, fpt, vup = views["perspective"]
    view.CameraPosition  = pos
    view.CameraFocalPoint = fpt
    view.CameraViewUp    = vup

    path = os.path.join(SHOTS_DIR, f"{prefix}_curvature.png")
    SaveScreenshot(path, view, ImageResolution=[1920, 1080])
    shots.append(os.path.relpath(path, REPO_DIR))
    print("  Shot: curvature")

    bar.Visibility = 0
    Hide(curvature, view)

    # ── 3. Wireframe ─────────────────────────────────────────────────────────
    wd = Show(reader, view)
    wd.Representation = "Wireframe"
    wd.AmbientColor   = [0.25, 0.85, 0.45]
    wd.DiffuseColor   = [0.25, 0.85, 0.45]
    wd.ColorArrayName = ["POINTS", ""]     # solid color

    view.CameraPosition  = pos
    view.CameraFocalPoint = fpt
    view.CameraViewUp    = vup

    path = os.path.join(SHOTS_DIR, f"{prefix}_wireframe.png")
    SaveScreenshot(path, view, ImageResolution=[1920, 1080])
    shots.append(os.path.relpath(path, REPO_DIR))
    print("  Shot: wireframe")
    Hide(reader, view)

    return {
        "name":        name,
        "description": cfg["desc"],
        "file":        os.path.basename(stl_path),
        "mesh": {
            "triangles": n_cells,
            "vertices":  n_points,
            "tri_to_vert_ratio": round(n_cells / n_points, 3) if n_points else None,
        },
        "geometry": geo,
        "bounding_box": {
            "x":        {"min": round(bounds[0], 4), "max": round(bounds[1], 4), "length": round(lx, 4)},
            "y":        {"min": round(bounds[2], 4), "max": round(bounds[3], 4), "length": round(ly, 4)},
            "z":        {"min": round(bounds[4], 4), "max": round(bounds[5], 4), "length": round(lz, 4)},
            "center":   center,
            "diagonal": round(math.sqrt(lx**2 + ly**2 + lz**2), 4),
        },
        "screenshots": shots,
    }


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(SHOTS_DIR, exist_ok=True)

    all_results = {}
    for name, cfg in MODELS.items():
        all_results[name] = analyze(name, cfg)

    out_path = os.path.join(RESULTS_DIR, "analysis_results.json")
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved → {out_path}")

    return all_results


if __name__ == "__main__":
    main()
