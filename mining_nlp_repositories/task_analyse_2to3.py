import os
import subprocess
import collections
from surround import Config
import pandas as pd
import logging

logging.basicConfig(filename='../output/debug.log',level=logging.DEBUG)

config = Config()
config.read_config_files(['config.yaml'])
input_path = config['input_path']
output_path = config['output_path']

class ModuleInfo:
    def __init__(self, repo, path, diffcount=0, parse_error=False):
        self.repo = repo
        self.path = path
        # mapping of repo, path -> diffcount
        self.diffcount = diffcount
        self.parse_error = parse_error

    @staticmethod
    def from_diff(repo, path, stdout_capture, stderr_capture):
        parse_error = False
        diffcount = 0
        headers = 0

        lines = stdout_capture.split('\n')
        for line in lines:
            if line.startswith("---"):
                # Diff header
                # TODO: Deal with edge case where line itself begins with --
                headers += 1
                continue
            if line.startswith("-"):
                diffcount += 1
                continue

        # Raise assertion error if it diff header not as expected.
        if diffcount == 0:
            assert headers == 0
        else:
            assert headers == 1

        if "Can't parse" in stderr_capture:
            parse_error = True

        logging.info([repo, path, diffcount, headers, parse_error])
        
        return ModuleInfo(repo, path, diffcount, parse_error)

    # Class variable
    ROW_HEADERS = ["repo", "path", "diffcount", "parse_error"]

    def to_rows(self):
        result = [self.repo, self.path, self.diffcount, self.parse_error]
        return [result]

def process(repo, path, filepath):
    result = subprocess.run(["2to3", filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_stdout = result.stdout.decode('utf-8')
    result_stderr = result.stderr.decode('utf-8')
    modinfo = ModuleInfo.from_diff(repo, path, result_stdout, result_stderr)
    return modinfo

def analyse_diffs(repo_dir, output_dir):
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
                modinfo = process(repo, path, filepath)
                modules[(repo, path)] = modinfo

    rows = []
    for (repo, path), module in modules.items():
        rows += module.to_rows()

    df = pd.DataFrame.from_records(rows, columns=ModuleInfo.ROW_HEADERS)

    output_filename = os.path.join(output_dir, "results_2to3.csv")
    df.to_csv(output_filename, index=False)

if __name__ == "__main__":
    input_directory = os.path.join("../", input_path)
    output_directory = os.path.join("../", output_path)
    analyse_diffs(input_directory, output_directory)