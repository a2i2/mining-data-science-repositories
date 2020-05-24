import os
from surround import Config
import pandas as pd
import logging
import sys
import git

config = Config()
config.read_config_files(['config.yaml'])
input_path = config['input_path']
output_path = config['output_path']

class RepoInfo:
    def __init__(self, repo_name, path):
        self.repo_name = repo_name
        self.path = path
        self.git_error = False

        try:
            repo = git.Repo(self.path)
            last_commit = repo.commit() # newest
            *_, first_commit = repo.iter_commits() # oldest

            self.first_committed_date     = first_commit.committed_date
            self.first_committed_datetime = first_commit.committed_datetime.isoformat()
            self.first_authored_date      = first_commit.authored_date
            self.first_authored_datetime  = first_commit.authored_datetime.isoformat()

            self.last_committed_date      = last_commit.committed_date
            self.last_committed_datetime  = last_commit.committed_datetime.isoformat()
            self.last_authored_date       = last_commit.authored_date
            self.last_authored_datetime   = last_commit.authored_datetime.isoformat()
        except Exception:
            logging.exception(f"unable to extract git info for repo {self.repo_name}")
            self.git_error = True

    # Class variable
    ROW_HEADERS = ["repo",
        "first_committed_date", "first_committed_datetime",
        "first_authored_date", "first_authored_datetime",
        "last_committed_date", "last_committed_datetime",
        "last_authored_date", "last_authored_datetime",
        "git_error"]

    def to_rows(self):
        if self.git_error:
            result = [self.repo_name] + [""] * (len(RepoInfo.ROW_HEADERS) - 2) + [True]
        else:
            result = [self.repo_name,
                self.first_committed_date, self.first_committed_datetime,
                self.first_authored_date, self.first_authored_datetime,
                self.last_committed_date, self.last_committed_datetime,
                self.last_authored_date, self.last_authored_datetime,
                False]
        return [result]

def process(repo_name, path):
    return RepoInfo(repo_name, path)

def analyse_git(repo_dir, output_dir, repo_id_list=None):
    # Information Extraction:
    # mapping of repo, path -> ModuleInfo
    repos = {}

    # Post Analysis:
    # mapping of repo, path -> type

    if repo_id_list is None:
        repo_id_list = os.listdir(repo_dir)

    for repo in repo_id_list:
        repo_subdir = os.path.join(repo_dir, repo)
        logging.info([repo, repo_subdir])
        repoinfo = process(repo, repo_subdir)
        repos[repo] = repoinfo

    rows = []
    for repo, repoinfo in repos.items():
        rows += repoinfo.to_rows()

    df = pd.DataFrame.from_records(rows, columns=RepoInfo.ROW_HEADERS)

    output_filename = os.path.join(output_dir, "results_git_date.csv")
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

    analyse_git(input_directory, output_directory, repo_id_list)