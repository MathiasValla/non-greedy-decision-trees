"""Load the repository's unchanged estimator and its separately built scorer."""

import importlib.util
from pathlib import Path
import sys
import types

REPO = Path(__file__).resolve().parents[2]
RUNTIME = REPO / "paper/array_revision/.cache/runtime/revision_tree"


def load_classifier():
    package = types.ModuleType("revision_tree")
    package.__path__ = [str(RUNTIME)]
    sys.modules.setdefault("revision_tree", package)
    spec = importlib.util.spec_from_file_location(
        "revision_tree._lookahead", REPO / "treeple/tree/_lookahead.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if module._lookahead_fast is None:
        raise RuntimeError("Build the Cython scorer using build_revision_runtime.py first")
    return module.LookaheadDecisionTreeClassifier
