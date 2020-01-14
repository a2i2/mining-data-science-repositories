import unittest
from import_graph import *
import pandas as pd
import numpy as np

class TestGraph(unittest.TestCase):
    
    def setUp(self):
        self.simple_paths2imports = pd.DataFrame({
            "path":        ["a.py", "a.py", "b/x.py", "b/x.py", "c/__init__.py", "d.py", "e.py", "f.py", "a.py", "f.py"],
            "module_name": ["a",    "a",    "b.x",    "b.x",    "c.__init__",    "d",    "e",    "f",    "a",    "f"],
            "import_name": ["b.x",  "x.y",  "d.x",    "ml.alg", "ml",            "c",    "",     "z",    "x.y",  ""]
        })
        self.simple_tier0modules = ["ml"]
        self.simple_module2imports = pd.DataFrame({
            "module_name": ["a",    "a",    "b.x",    "b.x",    "c.__init__",    "d",    "e",    "f"],
            "import_name": ["b.x",  "x.y",  "d.x",    "ml.alg", "ml",            "c",    "",     "z"]
        })
        self.simple_module2hops_init = pd.DataFrame({
            "module_name": ["a",    "b.x", "c.__init__", "d",    "e",    "f"],
            "hops":        [np.inf, 0,     0,            np.inf, np.inf, np.inf]
        })
        self.simple_module2hops = pd.DataFrame({
            "module_name": ["a",    "b.x", "c.__init__", "d",    "e",    "f"],
            "hops":        [1,      0,     0,            1,      np.inf, np.inf]
        })
        self.simple_path2hops = pd.DataFrame({
            "path":        ["a.py", "b/x.py", "c/__init__.py", "d.py", "e.py", "f.py"],
            "module_name": ["a",    "b.x",    "c.__init__",    "d",    "e",    "f"],
            "hops":        [1,      0,        0,               1,      np.inf, np.inf]
        })
        
        # Construct repo dataframe example
        repo1_paths2imports = self.simple_paths2imports.copy()
        repo1_paths2imports["repo"] = "rep1"
        repo2_paths2imports = self.simple_paths2imports.copy()
        repo2_paths2imports["repo"] = "rep2"
        self.simple_repos = pd.concat([repo1_paths2imports, repo2_paths2imports])
        
    def test_strip_init(self):
        self.assertEqual(strip_init("a.__init__"), "a")
        self.assertEqual(strip_init("a.b.__init__"), "a.b")
        self.assertEqual(strip_init("a"), "a")
        self.assertEqual(strip_init("a.b"), "a.b")
    
    def test_analyse_project(self):
        result = analyse_project(self.simple_module2imports, self.simple_module2hops_init)
        cmp = result == self.simple_module2hops
        self.assertTrue(cmp.all().all()) # all values of all columns should match expectations
    
    def test_seedhops(self):
        result = seedhops(self.simple_module2imports, self.simple_tier0modules)
        cmp = result == self.simple_module2hops_init
        self.assertTrue(cmp.all().all()) # all values of all columns should match expectations
    
    def test_paths2modules(self):
        result = paths2modules(self.simple_paths2imports)        
        cmp = result == self.simple_module2imports
        self.assertTrue(cmp.all().all()) # all values of all columns should match expectations
    
    def test_matches(self):
        self.assertTrue(matches("a", "a"))
        self.assertTrue(matches("a.b", "a.b"))
        self.assertTrue(matches("a.b", "a"))
        self.assertFalse(matches("a", "a.b"))
        self.assertFalse(matches("a", "b"))
        self.assertFalse(matches("a.b", "b"))
        self.assertFalse(matches("pylab", "py"))
        self.assertFalse(matches("pylab.b", "py"))

    def test_modules2paths(self):
        result = modules2paths(self.simple_module2hops, self.simple_paths2imports)
        cmp = result == self.simple_path2hops
        self.assertTrue(cmp.all().all()) # all values of all columns should match expectations

    def _validate_repo1_result(self, result):
        cmp = result == self.simple_path2hops
        self.assertTrue(cmp.all().all()) # all values of all columns should match expectations

    def test_process_repo(self):
        result = process_repo(self.simple_paths2imports, self.simple_tier0modules)
        self._validate_repo1_result(result)

    def test_process_repos(self):
        result = process_repos(self.simple_repos, self.simple_tier0modules)
        repo1_result = result[result["repo"] == "rep1"].drop("repo", axis=1)
        self._validate_repo1_result(repo1_result)

if __name__ == '__main__':
    unittest.main()

    