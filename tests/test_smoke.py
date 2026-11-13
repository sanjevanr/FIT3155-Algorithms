"""Small, dependency-free smoke tests for the provided implementations."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "algorithms"

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class TestSmoke(unittest.TestCase):
    def test_boyer_moore(self):
        mod = load("boyer_moore")
        positions, _ = mod.modified_boyer_moore("banana", "ana")
        self.assertEqual(sorted(positions), [2, 4])

    def test_bwt_exact(self):
        mod = load("bwt_approximate_matching")
        text, _, suffixes = mod.compute_suffix_array("banana")
        bwt = mod.extract_BWT(text, suffixes)
        positions = mod.backward_search_exact_match_case("ana", suffixes, mod.compute_rank(bwt), mod.compute_nOccurences(bwt))
        self.assertEqual(sorted(positions), [1, 3])

    def test_ukkonen_lcp(self):
        mod = load("ukkonen_suffix_tree")
        root = mod.UkkonensAlgorithm("banana$", [])
        suffixes, lcp = [], []
        mod.DFS_suffix_tree_to_construct_suffix_and_LCP_array(root, suffixes, lcp, 0, 0)
        self.assertEqual(suffixes, [6, 5, 3, 1, 0, 4, 2])
        self.assertEqual(lcp, [0, 0, 1, 3, 0, 0, 2])

    def test_rolling_hash(self):
        mod = load("rolling_hash_matching")
        self.assertEqual(mod.semi_numerical_pattern_matching("banana", "ana"), [2, 4])

if __name__ == "__main__":
    unittest.main()
