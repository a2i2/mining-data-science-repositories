import os
import subprocess
import collections
from surround import Config
import pandas as pd
import logging
import sys

config = Config()
config.read_config_files(['config.yaml'])
input_path = config['input_path']
output_path = config['output_path']

PY2_ENV = "/app/clean_env_py2/bin/"
PY3_ENV = "/app/clean_env_py3/bin/"
PY_ENV = {
    "python2": PY2_ENV,
    "python3": PY3_ENV
}

class ModuleInfo:
    def __init__(self, repo, path, module_name, imports=[], parse_error=False):
        self.repo = repo
        self.path = path
        # mapping of repo, path -> module_name
        self.module_name = module_name
        # mapping of repo, path -> [import]
        self.imports = imports
        self.parse_error = parse_error
        self.errors = []
    
    def log(self, err):
        self.errors.append(err)

    @staticmethod
    def from_findimports(repo, path, txt):
        module_name = None
        parse_error = False
        imports = []

        lines = txt.split('\n')
        for line in lines:
            if line == "":
                # ignore blank lines
                continue
            if line.endswith(":"):
                # module name
                assert not module_name # should only be set once
                module_name = line[:-1] # drop trailing ':'
                module_name = module_name.strip() # drop any whitespace
            else:
                import_str = line.strip()
                imports.append(import_str)

        logging.info(lines)
        logging.info([repo, path, module_name, imports])
        
        if not module_name:
            parse_error = True
            module_name = ""
            
        return ModuleInfo(repo, path, module_name, imports, parse_error)

    # Class variable
    ROW_HEADERS = ["repo", "path", "module_name", "import_name", "parse_error"]

    def to_rows(self):
        result = []
        if not self.imports:
            result.append([self.repo, self.path, self.module_name, "", self.parse_error]) # No imports
        for import_name in self.imports:
            result.append([self.repo, self.path, self.module_name, import_name, self.parse_error])
        return result

def process(repo, path, filepath, py_version="python3", py_env=""):
    result = subprocess.run([os.path.join(py_env, py_version),
                             "-m", "findimports",
                             filepath],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_stdout = result.stdout.decode('utf-8')
    modinfo = ModuleInfo.from_findimports(repo, path, result_stdout)
    result_stderr = result.stderr.decode('utf-8')
    modinfo.log(result_stderr)
    return modinfo

def analyse_imports(repo_dir, output_dir, py_version, repo_id_list=None):
    # Information Extraction:
    # mapping of repo, path -> ModuleInfo
    modules = {}

    # Post Analysis:
    # mapping of repo, path -> type

    if repo_id_list is None:
        repo_id_list = os.listdir(repo_dir)

    for repo in repo_id_list:
        repo_subdir = os.path.join(repo_dir, repo)
        for dirpath, dirnames, filenames in os.walk(repo_subdir):
            for filename in filenames:
                if filename.endswith(".py"):
                    logging.info([dirpath, filename])
                    filepath = os.path.join(dirpath, filename)
                    path = os.path.normpath(os.path.relpath(filepath, repo_dir))
                    modinfo = process(repo, path, filepath, py_version, PY_ENV[py_version])
                    modules[(repo, path)] = modinfo

    rows = []
    for (repo, path), module in modules.items():
        rows += module.to_rows()

    df = pd.DataFrame.from_records(rows, columns=ModuleInfo.ROW_HEADERS)

    output_filename = os.path.join(output_dir, "results_imports_" + py_version + ".csv")
    df.to_csv(output_filename, index=False)

if __name__ == "__main__":
    input_directory = os.path.join("../", input_path)

    try:
        # limit to list of repositories
        repo_list_path = sys.argv[1]
    except IndexError:
        repo_list_path = None

    if repo_list_path:
        repo_list_path = os.path.join("../", repo_list_path)
        repo_id_list = list(pd.read_csv(repo_list_path)["id"].astype(str))
    else:
        repo_id_list = None

    try:
        # custom output_path
        output_path = sys.argv[2]
    except IndexError:
        pass # leave output_path as is

    output_directory = os.path.join("../", output_path)
    logging.basicConfig(filename=os.path.join(output_directory, 'debug.log'),level=logging.DEBUG)

    analyse_imports(input_directory, output_directory, "python3", repo_id_list)
    analyse_imports(input_directory, output_directory, "python2", repo_id_list)
