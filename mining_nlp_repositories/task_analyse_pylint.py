import os
import subprocess
import collections
from surround import Config
import pandas as pd
import logging
import json
import sys

config = Config()
config.read_config_files(['config.yaml'])
input_path = config['input_path']
output_path = config['output_path']

# Note: As pylint configuration may differ between Python2 and Python3, they have been postfixed with the python version. 
# Path to pylintrc file to prevent "No config file found, using default configuration" in stderr
PYLINT_RC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylintrc_")

# Run Pylint within Python venv to ensure control over which libraries are present when Pylint does its checks.
PY2_ENV = "/app/clean_env_py2/bin/"
PY3_ENV = "/app/clean_env_py3/bin/"
PY_ENV = {
    "python2": PY2_ENV,
    "python3": PY3_ENV
}

class ModuleInfo:
    def __init__(self, repo, path, pylint_results=[], parse_error=False, internal_error=False):
        self.repo = repo
        self.path = path
        # mapping of repo, path -> [{pylint_field: val}]
        self.pylint_results = pylint_results
        self.parse_error = parse_error
        self.internal_error = internal_error # internal errors from pylint or in parsing pylint output

    # Field names that occur in pylint JSON
    PYLINT_FIELDS = ["type", "module", "obj", "line", "column", "path", "symbol", "message", "message-id"]

    @staticmethod
    def from_pylint(repo, path, stdout_capture, stderr_capture):
        module_name = None
        internal_error = False
        parse_error = False
        

        # Pylint2 will output warning about config file to stderr, even if present.
        # https://stackoverflow.com/questions/48447900/how-to-disable-using-config-file-in-pylint
        errlines = stderr_capture.split('\n')
        errlines = [e for e in errlines if not e.startswith("Using config file")] # ignore warnings about config file
        errlines = [e for e in errlines if e.strip()] # ignore blank lines

        if errlines:
            logging.error(errlines)
            internal_error = True

        try:
            if stdout_capture == "":
                # If Pylint2 detects no errors, it will have an empty output rather than an empty list []
                res = []
            else:
                res = json.loads(stdout_capture)
        except ValueError as e:
            logging.error(e)
            internal_error = True
            res = []

        # list of dict
        results = []

        for err in res:
            result_dict = {}
            for field in ModuleInfo.PYLINT_FIELDS:
                result_dict[field] = err[field]
            results.append(result_dict)

        for err in res:
            # TODO: Remove this check (as it also flags parse errors related to imports)
            if err["message-id"] == "E0001":
                 parse_error = True

        return ModuleInfo(repo, path, results, parse_error, internal_error)

    # Class variable
    ROW_HEADERS = ["repo", "path"] + PYLINT_FIELDS + ["parse_error", "internal_error"]

    def to_rows(self):
        result = []
        if not self.pylint_results:
            # No pylint errors/warnings
            result.append([self.repo, self.path] + [""] * len(ModuleInfo.PYLINT_FIELDS) + [self.parse_error, self.internal_error])
        for pylint_result in self.pylint_results:
            result.append([self.repo, self.path] + [pylint_result[field] for field in ModuleInfo.PYLINT_FIELDS] + [self.parse_error, self.internal_error])
        return result

def process(repo, repo_subdir, path, filepath, filepath_rel, py_version="python3", py_env=""):
    logging.info(repo_subdir)
    # set working dir to root of project so that imports resolve correctly
    # (doesn't make any difference unless run for whole project at the module level)
    result = subprocess.run([os.path.join(py_env, "pylint"),
                             "--output-format", "json",
                             "--rcfile", PYLINT_RC_FILE + py_version,
                             filepath_rel],
        cwd=repo_subdir,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_stdout = result.stdout.decode('utf-8')
    result_stderr = result.stderr.decode('utf-8')
    modinfo = ModuleInfo.from_pylint(repo, path, result_stdout, result_stderr)
    return modinfo

def analyse_pylint(repo_dir, output_dir, py_version, repo_id_list=None):
    # Information Extraction:
    # mapping of repo, path -> ModuleInfo
    modules = {}

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
                    filepath_rel = os.path.normpath(os.path.relpath(filepath, repo_subdir))
                    modinfo = process(repo, repo_subdir, path, filepath, filepath_rel, py_version, PY_ENV[py_version])
                    modules[(repo, path)] = modinfo

    rows = []
    for (repo, path), module in modules.items():
        rows += module.to_rows()

    df = pd.DataFrame.from_records(rows, columns=ModuleInfo.ROW_HEADERS)

    output_filename = os.path.join(output_dir, "results_pylint_" + py_version + ".csv")
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

    analyse_pylint(input_directory, output_directory, "python3", repo_id_list)
    analyse_pylint(input_directory, output_directory, "python2", repo_id_list)
