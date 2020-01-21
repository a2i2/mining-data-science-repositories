import os
import subprocess
import collections
from surround import Config
import pandas as pd
import logging
import json

logging.basicConfig(filename='../debug.log',level=logging.DEBUG)

config = Config()
config.read_config_files(['config.yaml'])
input_path = config['input_path']
output_path = config['output_path']

# Note: As pylint configuration may differ between Python2 and Python3, they have been postfixed with the python version. 
# Path to pylintrc file to prevent "No config file found, using default configuration" in stderr
PYLINT_RC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylintrc_")

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

def process(repo, repo_subdir, path, filepath, filepath_rel, py_version="python3"):
    logging.info(repo_subdir)
    # set working dir to root of project so that imports resolve correctly
    # (doesn't make any difference unless run for whole project at the module level)
    result = subprocess.run([py_version, "-m", "pylint", "--output-format", "json", "--rcfile", PYLINT_RC_FILE + py_version, filepath_rel],
        cwd=repo_subdir,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_stdout = result.stdout.decode('utf-8')
    result_stderr = result.stderr.decode('utf-8')
    modinfo = ModuleInfo.from_pylint(repo, path, result_stdout, result_stderr)
    return modinfo

def analyse_pylint(repo_dir, output_dir, py_version):
    # Information Extraction:
    # mapping of repo, path -> ModuleInfo
    modules = {}

    for dirpath, dirnames, filenames in os.walk(repo_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                logging.info([dirpath, filename])
                filepath = os.path.join(dirpath, filename)
                path = os.path.normpath(os.path.relpath(filepath, repo_dir))
                repo = path.split(os.path.sep)[0]
                repo_subdir = os.path.join(repo_dir, repo)
                filepath_rel = os.path.normpath(os.path.relpath(filepath, repo_subdir))
                modinfo = process(repo, repo_subdir, path, filepath, filepath_rel, py_version)
                modules[(repo, path)] = modinfo

    rows = []
    for (repo, path), module in modules.items():
        rows += module.to_rows()

    df = pd.DataFrame.from_records(rows, columns=ModuleInfo.ROW_HEADERS)

    output_filename = os.path.join(output_dir, "results_pylint_" + py_version + ".csv")
    df.to_csv(output_filename, index=False)

if __name__ == "__main__":
    input_directory = os.path.join("../", input_path)
    output_directory = os.path.join("../", output_path)
    analyse_pylint(input_directory, output_directory, "python3")
    analyse_pylint(input_directory, output_directory, "python2")
