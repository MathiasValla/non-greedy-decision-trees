"""Build the existing Cython split scorer without treeple's unrelated modules."""

from pathlib import Path
import os

import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, setup

REPO = Path(__file__).resolve().parents[2]
BUILD = REPO / "paper" / "array_revision" / ".cache" / "runtime"

if __name__ == "__main__":
    BUILD.mkdir(parents=True, exist_ok=True)
    os.chdir(BUILD)
    setup(
        name="array-revision-scorer",
        ext_modules=cythonize(
            [Extension("revision_tree._lookahead_fast",
                       [str(REPO / "treeple/tree/_lookahead_fast.pyx")],
                       include_dirs=[np.get_include()])],
            build_dir=str(BUILD / "cython"),
            compiler_directives={"language_level": 3},
        ),
        script_args=["build_ext", "--build-lib", str(BUILD),
                     "--build-temp", str(BUILD / "temp")],
    )
