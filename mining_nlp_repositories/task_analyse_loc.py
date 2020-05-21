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


class ModuleInfo:
    def __init__(self, repo, path, result, internal_error=False):
        self.repo = repo
        self.path = path
        self.result = result
        self.internal_error = internal_error

    WC_FIELDS = ["nonblank_loc"]

    @staticmethod
    def from_count(repo, path, filepath_rel, stdout_capture, stderr_capture):
        module_name = None
        internal_error = False
        parse_error = False

        errlines = stderr_capture.strip()

        if errlines:
            logging.error(errlines)
            internal_error = True

        try:
            res = int(stdout_capture)
        except (ValueError) as e:
            logging.exception(e)
            internal_error = True
            res = 0
        
        return ModuleInfo(repo, path, res, internal_error)

    # Class variable
    ROW_HEADERS = ["repo", "path"] + WC_FIELDS + ["internal_error"]

    def to_row(self):
        if self.internal_error:
            # No results
            return [self.repo, self.path] + [""] * len(ModuleInfo.WC_FIELDS) + [self.internal_error]
        
        return [self.repo, self.path] + [self.result] + [self.internal_error]

    def to_rows(self):
        return [self.to_row()]

def process(repo, repo_subdir, path, filepath, filepath_rel):
    # https://stackoverflow.com/questions/114814/count-non-blank-lines-of-code-in-bash/114861#114861
    result = subprocess.run(['grep', '-cve', '^\s*$', filepath_rel],
        cwd=repo_subdir,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_stdout = result.stdout.decode('utf-8')
    result_stderr = result.stderr.decode('utf-8')
    modinfo = ModuleInfo.from_count(repo, path, filepath_rel, result_stdout, result_stderr)
    return modinfo

def analyse_loc(repo_dir, output_dir, repo_id_list=None):
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
                    filepath_rel = os.path.normpath(os.path.relpath(filepath, repo_subdir))
                    modinfo = process(repo, repo_subdir, path, filepath, filepath_rel)
                    modules[(repo, path)] = modinfo

    rows = []
    for (repo, path), module in modules.items():
        rows += module.to_rows()

    df = pd.DataFrame.from_records(rows, columns=ModuleInfo.ROW_HEADERS)

    output_filename = os.path.join(output_dir, "results_loc.csv")
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
    
    analyse_loc(input_directory, output_directory, repo_id_list)
