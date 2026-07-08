# Sample random design vectors from the parameter space, apply each to the
# CAD model, recompute, and report whether the geometry rebuilds cleanly.
#
# Use this to check that the sketch fixes hold across the whole parameter
# space, not just the current config.
#
# HOW TO RUN (inside FreeCAD, with the model open):
#   exec(open("/home/simon/projects/uni/FlyingWingRevision/FlyingWingAutoSolve/Tools/verify_random_configs.py").read())
#   verify(n=10)              # test 10 random configs
#   verify(n=10, seed=42)     # reproducible
#
# It restores the original CurrentParameter values when done.

import math
import random

import FreeCAD as App

doc = App.ActiveDocument

desc = doc.getObjectsByLabel("ParameterDescription")[0]
current = doc.getObjectsByLabel("CurrentParameter")[0]
geometry = doc.getObjectsByLabel("WingGeometry")[0]

# parameter table (same indirection the solver uses: a cell holds the name
# of the column that actually stores the values)
paramnames = desc.cells[desc.cells["ParameterNames"]]
parammins = desc.cells[desc.cells["MinValue"]]
parammaxs = desc.cells[desc.cells["MaxValue"]]
paramdefaults = desc.cells[desc.cells["DefaultValues"]]


def _apply(values):
    """Set CurrentParameter to `values` (name->float) and recompute the model.
    Mirrors _set_params in WingSolver_CalcGradient.FCMacro."""
    for name, v in values.items():
        current.set(name, "%E" % v)
    current.recompute()
    geometry.recompute()
    for obj in doc.Objects:
        obj.touch()
    doc.recompute()


def _problems():
    """Return a list of (name, why) for anything wrong after a recompute:
    objects in an error state, plus any zero-length sketch edges."""
    probs = []
    for o in doc.Objects:
        st = o.State
        if st and ("Error" in st or "Invalid" in st):
            probs.append((o.Name, f"state={st}"))
        if o.TypeId == "Sketcher::SketchObject":
            for i, g in enumerate(o.Geometry):
                try:
                    # use actual arc length, not endpoint distance: a closed
                    # (periodic) B-spline has coincident endpoints by design
                    # but non-zero length, so endpoint distance false-positives.
                    if g.length() < 1e-6:
                        probs.append((o.Name, f"zero-length Edge{i+1} "
                                              f"({g.TypeId.split('::')[-1]})"))
                except Exception:
                    pass
    return probs


def _sample():
    """One random design vector within [min, max]. NaN bound -> default."""
    vals = {}
    for i, name in enumerate(paramnames):
        lo, hi, dv = parammins[i], parammaxs[i], paramdefaults[i]
        if lo is None or hi is None or (isinstance(lo, float) and math.isnan(lo)) \
                or (isinstance(hi, float) and math.isnan(hi)):
            vals[name] = dv
        else:
            vals[name] = random.uniform(lo, hi)
    return vals


def verify(n=10, seed=None):
    if seed is not None:
        random.seed(seed)

    # remember the current design vector so we can restore it
    original = {name: current.cells[name] for name in paramnames}

    passed = failed = 0
    try:
        for k in range(n):
            v = _sample()
            try:
                _apply(v)
                probs = _problems()
            except Exception as e:
                probs = [("<exception>", repr(e))]

            if probs:
                failed += 1
                print(f"[{k+1}/{n}] FAIL")
                for name, why in probs[:12]:
                    print(f"        {name}: {why}")
                print("        config: " +
                      ", ".join(f"{p}={v[p]:.4g}" for p in paramnames))
            else:
                passed += 1
                print(f"[{k+1}/{n}] ok")
    finally:
        _apply(original)  # restore
        print(f"\nRestored original config. {passed} passed, {failed} failed.")


def apply_case(seed, index):
    """Reproduce and APPLY the `index`-th config (1-based) from a verify(seed)
    run, and LEAVE it applied so you can inspect the broken geometry in the
    3D view. Draws samples in the same order verify() does, so the config
    matches exactly.

    Example:  apply_case(42, 2)   # reproduce test [2/10] and keep it
    """
    random.seed(seed)
    v = None
    for _ in range(index):
        v = _sample()          # advance the RNG exactly like verify()
    _apply(v)
    print(f"Applied config #{index} (seed={seed}) -- NOT restored.")
    print("  " + ", ".join(f"{p}={v[p]:.4g}" for p in paramnames))
    probs = _problems()
    if probs:
        print("  problems:")
        for name, why in probs:
            print(f"    {name}: {why}")
    print("  Now inspect in the tree/3D view. To go back to defaults, "
          "re-run WingSolver_ResetDefaults or restore manually.")
    return v


print("Loaded. Run:  verify(n=10)   or   verify(n=10, seed=42)")
print("             apply_case(42, 2)   # keep test #2 applied for inspection")
