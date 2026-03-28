# Aircraft ParaView Analysis

Geometric and visual analysis of two aircraft STL models using [ParaView 6](https://www.paraview.org/).
Each model is analyzed for mesh statistics, bounding-box geometry, surface area, estimated volume, and rendered from 9 viewpoints (7 orthographic + curvature heat-map + wireframe).

---

## Models

| # | Model | File | Source |
|---|-------|------|--------|
| 1 | **ATR_x** | `ATR_x.stl` | [Thingiverse #7049570](https://www.thingiverse.com/thing:7049570) |
| 2 | **Fighter Jet Concept** | `Fighter_jet_concept.stl` | [Thingiverse #6930754](https://www.thingiverse.com/thing:6930754) |

---

## Comparison Summary

| Metric | ATR_x | Fighter Jet |
|--------|-------|-------------|
| **Triangles** | 143,270 | 172,676 |
| **Vertices** | 71,651 | 86,062 |
| **Tri/Vert ratio** | 2.000 | 2.006 |
| **Surface Area (units²)** | 76,235.70 | 209,992.46 |
| **Volume est. (units³)** | 295,310.39 | 638,026.24 |
| **Length X** | 335.15 | 520.00 |
| **Length Y (wingspan)** | 340.00 | 260.00 |
| **Height Z** | 84.74 | 59.89 |
| **Bounding diagonal** | 484.88 | 584.45 |

> Units are in the STL file's native coordinate system (millimeters for these models).
> Volume is estimated from the closed surface via `vtkMassProperties` — valid only for watertight meshes.

---

## ATR_x — ATR Turboprop Regional Aircraft Concept

### Perspective View
![ATR_x Perspective](results/screenshots/atr_x_perspective.png)

### Front
![ATR_x Front](results/screenshots/atr_x_front.png)

### Rear
![ATR_x Rear](results/screenshots/atr_x_rear.png)

### Left Side
![ATR_x Left](results/screenshots/atr_x_left.png)

### Right Side
![ATR_x Right](results/screenshots/atr_x_right.png)

### Top
![ATR_x Top](results/screenshots/atr_x_top.png)

### Bottom
![ATR_x Bottom](results/screenshots/atr_x_bottom.png)

### Mean Curvature Heat-Map
![ATR_x Curvature](results/screenshots/atr_x_curvature.png)

> Cool-to-Warm color map: **blue** = concave regions, **red** = convex regions.

### Wireframe
![ATR_x Wireframe](results/screenshots/atr_x_wireframe.png)

---

## Fighter Jet Concept

### Perspective View
![Fighter Jet Perspective](results/screenshots/fighter_jet_perspective.png)

### Front
![Fighter Jet Front](results/screenshots/fighter_jet_front.png)

### Rear
![Fighter Jet Rear](results/screenshots/fighter_jet_rear.png)

### Left Side
![Fighter Jet Left](results/screenshots/fighter_jet_left.png)

### Right Side
![Fighter Jet Right](results/screenshots/fighter_jet_right.png)

### Top
![Fighter Jet Top](results/screenshots/fighter_jet_top.png)

### Bottom
![Fighter Jet Bottom](results/screenshots/fighter_jet_bottom.png)

### Mean Curvature Heat-Map
![Fighter Jet Curvature](results/screenshots/fighter_jet_curvature.png)

> Cool-to-Warm color map: **blue** = concave regions, **red** = convex regions.

### Wireframe
![Fighter Jet Wireframe](results/screenshots/fighter_jet_wireframe.png)

---

## Repository Structure

```
aircraft-paraview-analysis/
├── models/
│   ├── ATR_x.stl
│   └── Fighter_jet_concept.stl
├── scripts/
│   └── analyze.py          # ParaView 6 analysis script
├── results/
│   ├── analysis_results.json
│   └── screenshots/        # 18 PNG renders (1920×1080)
└── README.md
```

## Reproducing the Analysis

Requirements: ParaView 6 with Python bindings (`pvpython`).

```bash
pvpython --force-offscreen-rendering scripts/analyze.py
```

Full JSON results are in [`results/analysis_results.json`](results/analysis_results.json).

---

*Generated with [ParaView](https://www.paraview.org/) 6.0.1 and [Claude Code](https://claude.ai/claude-code).*
