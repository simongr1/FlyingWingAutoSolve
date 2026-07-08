# Diagnose broken sketch geometry in the active FreeCAD document.
#
# HOW TO RUN:
#   1. Open FlyingWingAutoSolve_newParamater.FCStd in FreeCAD.
#   2. Open the Python console (View > Panels > Python console).
#   3. Paste this whole file, or run:
#        exec(open("/home/simon/projects/uni/FlyingWingRevision/FlyingWingAutoSolve/Tools/find_broken_geometry.py").read())
#
# It finds which sketch owns a "Both points are equal" / "Edge too small"
# error by scanning every sketch for zero-length edges, lists objects in an
# error state, and lets you inspect/select a specific geometry index.

import FreeCAD as App
import FreeCADGui as Gui

TOL = 1e-6  # length below this counts as "collapsed"

doc = App.ActiveDocument
if doc is None:
    print("No active document. Open the .FCStd first.")
else:
    # ------------------------------------------------------------------
    # 1. Scan every sketch for zero-length (degenerate) edges.
    #    This is the authoritative way to locate "Both points are equal".
    # ------------------------------------------------------------------
    print("=== Zero-length edges (candidates for 'Both points are equal') ===")
    found_any = False
    for sk in doc.Objects:
        if sk.TypeId != "Sketcher::SketchObject":
            continue
        for i, g in enumerate(sk.Geometry):
            try:
                # actual arc length, not endpoint distance -- a closed/periodic
                # B-spline (e.g. an airfoil contour) has coincident endpoints
                # by design but real length, so endpoint distance would lie.
                if g.length() < TOL:
                    found_any = True
                    print(f"  {sk.Name} ({sk.Label!r})  geo[{i}] -> Edge{i+1}"
                          f"  ZERO-LENGTH  {g.TypeId}")
            except Exception:
                pass
    if not found_any:
        print("  (none found)")

    # ------------------------------------------------------------------
    # 2. List every object currently in an Error / Invalid state.
    # ------------------------------------------------------------------
    print("\n=== Objects in an error/touched state ===")
    any_err = False
    for o in doc.Objects:
        st = o.State
        if st and ("Error" in st or "Invalid" in st or "Touched" in st):
            any_err = True
            print(f"  {o.Name:14s} {o.Label!r:30s} {o.TypeId:35s} {st}")
    if not any_err:
        print("  (none)")


def inspect(sketch_name, idx):
    """Inspect and select geometry element `idx` in a given sketch.

    Example:  inspect("Sketch011", 16)
    """
    sk = doc.getObject(sketch_name)
    if sk is None:
        print(f"No object named {sketch_name!r}")
        return
    g = sk.Geometry[idx]
    print(f"{sketch_name} geo[{idx}] -> {g.TypeId}")
    try:
        d = g.StartPoint.distanceToPoint(g.EndPoint)
        print(f"  start: {g.StartPoint}\n  end:   {g.EndPoint}\n  length: {d}")
    except Exception as e:
        print(f"  (no endpoints): {e}")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, sk.Name, f"Edge{idx+1}")
    print(f"  selected Edge{idx+1} (geo index is 0-based; subelement is 1-based)")


def edit(sketch_name, *indices):
    """Open a sketch in edit mode and select the given geometry indices.

    Use this to actually see/fix a collapsed edge inside the Sketcher.
    A zero-length edge is invisible, but this highlights it (and its
    endpoints) so you can find where it lives among the constraints.

    Example:  edit("Sketch003", 15, 16)
    """
    sk = doc.getObject(sketch_name)
    if sk is None:
        print(f"No object named {sketch_name!r}")
        return
    Gui.activeDocument().setEdit(sk)          # enter Sketcher edit mode
    Gui.Selection.clearSelection()
    for idx in indices:
        g = sk.Geometry[idx]
        Gui.Selection.addSelection(doc.Name, sk.Name, f"Edge{idx+1}")
        # also select the two endpoints (Vertex numbering is separate)
        try:
            d = g.StartPoint.distanceToPoint(g.EndPoint)
            print(f"  {sketch_name} geo[{idx}] Edge{idx+1}: length={d}  {g.TypeId}")
        except Exception as e:
            print(f"  {sketch_name} geo[{idx}] Edge{idx+1}: {e}")
    print("  -> selected in the Sketcher. Close edit mode with:  "
          "Gui.activeDocument().resetEdit()")


def explain(sketch_name, idx):
    """Explain what a geometry element is: its points, neighbours, and every
    constraint that references it. This is how you understand an invisible
    (zero-length) edge -- its constraints reveal its intent and what
    collapsed it.

    Example:  explain("Sketch003", 15)
    """
    sk = doc.getObject(sketch_name)
    if sk is None:
        print(f"No object named {sketch_name!r}")
        return
    geo = sk.Geometry
    g = geo[idx]
    print(f"=== {sketch_name} geo[{idx}] (Edge{idx+1}) ===")
    print(f"  type: {g.TypeId}   construction: {getattr(g,'Construction',None)}")
    try:
        print(f"  start: {g.StartPoint}")
        print(f"  end:   {g.EndPoint}")
        print(f"  length: {g.StartPoint.distanceToPoint(g.EndPoint)}")
    except Exception as e:
        print(f"  (no endpoints): {e}")

    # neighbours: which other edges share an endpoint with this one?
    print("  -- neighbours sharing an endpoint --")
    try:
        pa, pb = g.StartPoint, g.EndPoint
        for j, o in enumerate(geo):
            if j == idx or not hasattr(o, "StartPoint"):
                continue
            for label, p in (("start", o.StartPoint), ("end", o.EndPoint)):
                if p.distanceToPoint(pa) < 1e-6 or p.distanceToPoint(pb) < 1e-6:
                    print(f"     geo[{j}] Edge{j+1} {o.TypeId} ({label})")
                    break
    except Exception:
        pass

    # constraints that reference this geometry (GeoId == idx)
    print("  -- constraints referencing this element --")
    hit = False
    for c in sk.Constraints:
        if idx in (c.First, c.Second, c.Third):
            hit = True
            parts = []
            for gid, pos in ((c.First, c.FirstPos),
                             (c.Second, c.SecondPos),
                             (c.Third, c.ThirdPos)):
                if gid != -2000:  # -2000 = "not used"
                    parts.append(f"geo{gid}:pos{pos}")
            val = ""
            try:
                if c.Value:
                    val = f"  value={c.Value}"
            except Exception:
                pass
            name = f" '{c.Name}'" if c.Name else ""
            print(f"     {c.Type}{name}: {', '.join(parts)}{val}")
    if not hit:
        print("     (no constraints reference it -- it is free/unconstrained)")


def whereis(*internal_names):
    """Print Label/Type for internal names from the log and select them.

    Example:  whereis("Sketch011", "Part014", "Compound006")
    """
    Gui.Selection.clearSelection()
    for n in internal_names:
        o = doc.getObject(n)
        if o is None:
            print(f"  {n:14s} -> (not found)")
            continue
        print(f"  {n:14s} -> Label={o.Label!r:30s} Type={o.TypeId}")
        Gui.Selection.addSelection(o)


print("\nHelpers loaded:")
print("  inspect('Sketch003', 16)   # examine + select geometry index 16")
print("  edit('Sketch003', 15, 16)  # OPEN sketch in edit mode + select edges to fix")
print("  whereis('Part014','Box')   # map internal names -> Label/Type")
