import sys
import ast

# Adapted from
# https://stackoverflow.com/questions/40886456/how-to-detect-if-code-is-python-3-compatible/40886697#40886697

def test(fname):
    # Open in binary mode (else UTF-8 BOM will cause parse error if read as text)
    with open(fname, 'rb') as f:
        src_code = f.read()
    try:
        ast.parse(src_code)
    except SyntaxError as e:
        return "invalid"
    
    return "valid"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: py2or3 file.py")
    fname = sys.argv[1]
    result = test(fname)
    print (result)