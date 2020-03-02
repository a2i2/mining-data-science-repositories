import os
import subprocess
import collections
from surround import Config
import pandas as pd
import logging
import json

logging.basicConfig(filename='../output/debug.log',level=logging.DEBUG)

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
    def __init__(self, repo, path, radon_results=[], parse_error=False, internal_error=False):
        self.repo = repo
        self.path = path
        self.radon_results = radon_results
        self.parse_error = parse_error
        self.internal_error = internal_error # internal errors from radon or in parsing radon output

    # Field names that occur in Radon JSON
    RADON_CORE_FIELDS = ["type", "rank", "lineno", "name", "col_offset", "complexity", "endline"]
    RADON_EXTRA_FIELDS = ["methods_count", "closures_count"]
    RADON_FIELDS = RADON_CORE_FIELDS + RADON_EXTRA_FIELDS

    @staticmethod
    def from_radon(repo, path, filepath_rel, stdout_capture, stderr_capture):
        module_name = None
        internal_error = False
        parse_error = False

        errlines = stderr_capture.strip()

        if errlines:
            logging.error(errlines)
            internal_error = True

        try:
            res = json.loads(stdout_capture)
            res = res[filepath_rel]
        except (ValueError, KeyError) as e:
            logging.exception(e)
            internal_error = True
            res = []
        
        results = []

        if "error" in res:
            parse_error = True
            logging.error(res["error"])

        if not (internal_error or parse_error):
            for r in res:
                result_dict = {}

                for field in ModuleInfo.RADON_CORE_FIELDS:
                    result_dict[field] = r[field]

                result_dict["methods_count"] = len(r["methods"]) if "methods" in r else 0
                result_dict["closures_count"] = len(r["closures"]) if "closures" in r else 0
                
                results.append(result_dict)

        return ModuleInfo(repo, path, results, parse_error, internal_error)

    # Class variable
    ROW_HEADERS = ["repo", "path"] + RADON_FIELDS + ["parse_error", "internal_error"]

    def to_rows(self):
        result = []
        if not self.radon_results:
            # No pylint errors/warnings
            result.append([self.repo, self.path] + [""] * len(ModuleInfo.RADON_FIELDS) + [self.parse_error, self.internal_error])
        for radon_result in self.radon_results:
            result.append([self.repo, self.path] + [radon_result[field] for field in ModuleInfo.RADON_FIELDS] + [self.parse_error, self.internal_error])
        return result


def process(repo, repo_subdir, path, filepath, filepath_rel, py_version="python3", py_env=""):
    result = subprocess.run([os.path.join(py_env, py_version),
                             "-m", "radon", "cc", "-j",
                             filepath_rel],
        cwd=repo_subdir,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_stdout = result.stdout.decode('utf-8')
    result_stderr = result.stderr.decode('utf-8')
    modinfo = ModuleInfo.from_radon(repo, path, filepath_rel, result_stdout, result_stderr)
    return modinfo

def analyse_radon(repo_dir, output_dir, py_version):
    # Information Extraction:
    # mapping of repo, path -> ModuleInfo
    modules = {}

    # Post Analysis:
    # mapping of repo, path -> type

    for dirpath, dirnames, filenames in os.walk(repo_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                logging.info([dirpath, filename])
                filepath = os.path.join(dirpath, filename)
                path = os.path.normpath(os.path.relpath(filepath, repo_dir))
                repo = path.split(os.path.sep)[0]
                repo_subdir = os.path.join(repo_dir, repo)
                filepath_rel = os.path.normpath(os.path.relpath(filepath, repo_subdir))
                modinfo = process(repo, repo_subdir, path, filepath, filepath_rel, py_version, PY_ENV[py_version])
                modules[(repo, path)] = modinfo

    rows = []
    for (repo, path), module in modules.items():
        rows += module.to_rows()

    df = pd.DataFrame.from_records(rows, columns=ModuleInfo.ROW_HEADERS)

    output_filename = os.path.join(output_dir, "results_radon_cc_" + py_version + ".csv")
    df.to_csv(output_filename, index=False)

if __name__ == "__main__":
    input_directory = os.path.join("../", input_path)
    output_directory = os.path.join("../", output_path)
    analyse_radon(input_directory, output_directory, "python2")
    analyse_radon(input_directory, output_directory, "python3")
