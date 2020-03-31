import os
import subprocess
import collections
from surround import Config
import pandas as pd
import logging
import sys
from py2or3_wrapper import to_py_str, test_py

logging.basicConfig(filename='../output/debug.log',level=logging.DEBUG)

config = Config()
config.read_config_files(['config.yaml'])
input_path = config['input_path']
output_path = config['output_path']

class VerInfo:
    def __init__(self, repo, path, ver=""):
        self.repo = repo
        self.path = path
        self.ver = ver
    
    # Class variable
    ROW_HEADERS = ["repo", "path", "ver"]

    def to_rows(self):
        row = [self.repo, self.path, self.ver]
        return [row]

def process(repo, path, filepath):
    result = to_py_str(*test_py(filepath))
    verinfo = VerInfo(repo, path, result)
    return verinfo

def analyse_version(repo_dir, output_dir, repo_id_list=None):
    # Information Extraction:
    # mapping of repo, path -> VerInfo
    modules = {}

    # Post Analysis:
    # mapping of repo, path -> type

    for dirpath, dirnames, filenames in os.walk(repo_dir):
        if dirpath == repo_dir:
            if repo_id_list is not None:
                dirnames2 = [d for d in dirnames if d in set(repo_id_list)]
                # os.walk allows *in-place* modification of dirnames
                del dirnames[:] # clear the existing directory list
                dirnames += dirnames2 # update with only the desired directories

        for filename in filenames:
            if filename.endswith(".py"):
                logging.info([dirpath, filename])
                filepath = os.path.join(dirpath, filename)
                path = os.path.normpath(os.path.relpath(filepath, repo_dir))
                repo = path.split(os.path.sep)[0]
                verinfo = process(repo, path, filepath)
                modules[(repo, path)] = verinfo

    rows = []
    for (repo, path), module in modules.items():
        rows += module.to_rows()

    df = pd.DataFrame.from_records(rows, columns=VerInfo.ROW_HEADERS)

    output_filename = os.path.join(output_dir, "results_version.csv")
    df.to_csv(output_filename, index=False)

if __name__ == "__main__":
    input_directory = os.path.join("../", input_path)
    output_directory = os.path.join("../", output_path)

    try:
        repo_list_path = sys.argv[1]
    except IndexError:
        repo_list_path = None

    if repo_list_path:
        repo_list_path = os.path.join("../", repo_list_path)
        repo_id_list = list(pd.read_csv(repo_list_path)["id"].astype(str))
    else:
        repo_id_list = None

    analyse_version(input_directory, output_directory, repo_id_list)
