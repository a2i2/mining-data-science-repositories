import os
import subprocess
from surround import Config
import logging
import sys

logging.basicConfig(filename='../output/debug.log',level=logging.DEBUG)

config = Config()
config.read_config_files(['config.yaml'])
input_drive_path = config['input_drive_path']
symplink_path = config['input_path']

def process(repo, repo_subdir, path, filepath, filepath_rel, py_version="python3", py_env=""):
    logging.info(repo_subdir)
    # set working dir to root of project so that imports resolve correctly
    # (doesn't make any difference unless run for whole project at the module level)
    result = subprocess.run([os.path.join(py_env, py_version),
                             "-m", "pylint",
                             "--output-format", "json",
                             "--rcfile", PYLINT_RC_FILE + py_version,
                             filepath_rel],
        cwd=repo_subdir,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_stdout = result.stdout.decode('utf-8')
    result_stderr = result.stderr.decode('utf-8')
    modinfo = ModuleInfo.from_pylint(repo, path, result_stdout, result_stderr)
    return modinfo

def create_symlinks(repo_dir, subdir, symlink_dir):
    subdir_path = os.path.join(repo_dir, subdir)
    for dir in os.listdir(subdir_path):
        repo_path = os.path.join(subdir_path, dir)
        if os.path.isdir(repo_path):
            symlink_name = os.path.join(symlink_dir, dir)
            os.symlink(repo_path, symlink_name)

if __name__ == "__main__":
    input_drive_directory = os.path.join("../", input_drive_path)
    symlink_directory = os.path.join("../", symplink_path)

    create_symlinks(input_drive_directory, "cloned-repos/boa",                           symlink_directory)
    create_symlinks(input_drive_directory, "cloned-repos/boa-zip-download",              symlink_directory)
    create_symlinks(input_drive_directory, "cloned-repos/non-data-science",              symlink_directory)
    create_symlinks(input_drive_directory, "cloned-repos/non-data-science-zip-download", symlink_directory)
