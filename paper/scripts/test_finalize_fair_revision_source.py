"""Exercise manuscript assembly in an isolated copy; never fit or edit originals."""

from pathlib import Path
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import finalize_fair_revision_source as finalizer


class FairSourceAssemblyTest(unittest.TestCase):
    def test_figure_environment_is_scoped_to_its_marker(self):
        first = "\\begin{figure*}\n% BEGIN GENERATED figure1\nfirst\n\\end{figure*}"
        second = "\\begin{figure*}\n% BEGIN GENERATED figure2\nsecond\n\\end{figure*}"
        self.assertEqual(finalizer.figure_environment(first + "\n" + second, "figure2"), second)

    def test_caption_replacement_requires_a_marker(self):
        with self.assertRaises(ValueError):
            finalizer.replace_caption("Unmarked document", "figure1", "New caption")

    def test_complete_native_assembly_is_idempotent(self):
        original = Path(__file__).resolve().parents[1]
        evidence = Path(os.environ.get("FAIR_ANALYSIS_ROOT", original / "array_revision_fair"))
        if not (evidence / "analysis/full/validation.json").is_file():
            self.skipTest("Restore the full bundle and set FAIR_ANALYSIS_ROOT to its new root")
        with tempfile.TemporaryDirectory(prefix="fair_source_assembly_") as directory:
            paper = Path(directory) / "paper"
            article = paper / "array_revision"
            article.mkdir(parents=True)
            for name in ("main.tex", "response_to_reviewers.tex"):
                shutil.copyfile(original / "array_revision" / name, article / name)
            fair = paper / "array_revision_fair"
            shutil.copytree(original / "array_revision_fair/manuscript", fair / "manuscript")
            shutil.copytree(evidence / "analysis/full", fair / "analysis/full")
            with patch.object(finalizer, "PAPER", paper), \
                    patch.object(finalizer, "FAIR", fair), \
                    patch.object(finalizer, "MANUSCRIPT", article / "main.tex"), \
                    patch.object(sys, "argv", ["finalize_fair_revision_source.py"]):
                finalizer.main()
                first = {name: (article / name).read_bytes()
                         for name in ("main.tex", "response_to_reviewers.tex")}
                finalizer.main()
                self.assertEqual(first, {name: (article / name).read_bytes() for name in first})
            text = first["main.tex"].decode()
            self.assertEqual(text.count(r"\begin{table*}"), 2)
            self.assertEqual(text.count(r"\end{table*}"), 2)
            self.assertEqual(text.count(r"\begin{figure*}"), 3)
            self.assertEqual(text.count(r"\end{figure*}"), 3)
            labels = re.findall(r"\\label\{([^}]+)\}", text)
            self.assertEqual(len(labels), len(set(labels)))
            self.assertTrue({"fig:depth", "fig:tradeoff", "fig:tuned",
                             "tab:performance", "tab:comparisons"}.issubset(labels))
            self.assertNotIn(r"\includegraphics", text)
            self.assertNotIn("still running", text)
            self.assertNotIn("ydir=reverse", text)
            self.assertIn("y dir=reverse", text)
            tradeoff = text.index(r"\label{fig:tradeoff}")
            following = text.index("% BEGIN FIGURE2_POSTPLOT_TEXT")
            self.assertLess(tradeoff, following)
            self.assertLess(following - tradeoff, 200)


if __name__ == "__main__":
    unittest.main()
