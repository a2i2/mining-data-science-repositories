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

class ModuleInfo:
    def __init__(self, repo, path, radon_result={}, parse_error=False, internal_error=False):
        self.repo = repo
        self.path = path
        self.radon_result = radon_result
        self.parse_error = parse_error
        self.internal_error = internal_error # internal errors from radon or in parsing radon output

    # Field names that occur in Radon JSON
    RADON_FIELDS = ["loc", "lloc", "sloc", "comments", "multi", "blank", "single_comments"]

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
            logging.info(res)
            res = res[filepath_rel]
        except (ValueError, KeyError) as e:
            logging.exception(e)
            internal_error = True
            res = {}
        
        if "error" in res:
            parse_error = True
            logging.error(res["error"])
        
        result_dict = {}
        if not (internal_error or parse_error):
            for field in ModuleInfo.RADON_FIELDS:
                result_dict[field] = res[field]
            
        return ModuleInfo(repo, path, result_dict, parse_error, internal_error)

    # Class variable
    ROW_HEADERS = ["repo", "path"] + RADON_FIELDS + ["parse_error", "internal_error"]

    def to_row(self):
        if not self.radon_result:
            # No radon errors/warnings
            return [self.repo, self.path] + [""] * len(ModuleInfo.RADON_FIELDS) + [self.parse_error, self.internal_error]
        
        return [self.repo, self.path] + [self.radon_result[field] for field in ModuleInfo.RADON_FIELDS] + [self.parse_error, self.internal_error]

    def to_rows(self):
        return [self.to_row()]

def process(repo, repo_subdir, path, filepath, filepath_rel, py_version="python3"):
    result = subprocess.run([py_version, "-m", "radon", "raw", "-j", filepath_rel],
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
                modinfo = process(repo, repo_subdir, path, filepath, filepath_rel, py_version)
                modules[(repo, path)] = modinfo

    rows = []
    for (repo, path), module in modules.items():
        rows += module.to_rows()

    df = pd.DataFrame.from_records(rows, columns=ModuleInfo.ROW_HEADERS)

    output_filename = os.path.join(output_dir, "results_radon_raw_" + py_version + ".csv")
    df.to_csv(output_filename, index=False)

if __name__ == "__main__":
    input_directory = os.path.join("../", input_path)
    output_directory = os.path.join("../", output_path)
    analyse_radon(input_directory, output_directory, "python2")
    analyse_radon(input_directory, output_directory, "python3")
