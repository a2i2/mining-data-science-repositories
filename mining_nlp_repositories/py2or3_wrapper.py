#!/usr/bin/env python3

import sys
import ast
import subprocess

# Adapted from
# https://stackoverflow.com/questions/40886456/how-to-detect-if-code-is-python-3-compatible/40886697#40886697


def test_py(fname):
    py2result = subprocess.run(["python2", "py2or3.py", fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    py2stdout = py2result.stdout.decode('utf-8')
    validPy2 = py2stdout == "valid\n"
    
    py3result = subprocess.run(["python3", "py2or3.py", fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    py3stdout = py3result.stdout.decode('utf-8')
    validPy3 = py3stdout == "valid\n"
    
    return validPy2, validPy3

def to_py_str(validPy2, validPy3):
    names = {
      (False, False): "neither",
      (True, False): "python2",
      (False, True): "python3",
      (True, True): "either"
    }
    return names[(validPy2, validPy3)]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: py2or3_wrapper file.py")
    fname = sys.argv[1]
    result = to_py_str(*test_py(fname))

    print (result)