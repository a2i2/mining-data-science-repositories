import os
import subprocess
import collections
from surround import Config
import pandas as pd
import logging
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

def analyse_version(repo_dir, output_dir):
    # Information Extraction:
    # mapping of repo, path -> VerInfo
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
    analyse_version(input_directory, output_directory)
