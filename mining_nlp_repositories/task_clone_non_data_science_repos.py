import os
import glob
import git
import time
import json
import github
from pprint import pprint

not_cloned = []

def read_json_response(path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    return data

def clone_repo(clone_dir, clone_url):
    git.Repo.clone_from(clone_url, clone_dir)

def process_json(path_to_json_response):
    data = read_json_response(path_to_json_response)
    clone_dir = 'data/non-data-science/cloned-repos/' + str(data['id'])
    if not os.path.isdir(clone_dir):
        try:
            clone_repo( clone_dir, data['html_url'])
            time.sleep(1)
        except:
            not_cloned.append(data['id'])

def main():
    # Analyse json responses
    path_to_json_dir = 'data/non-data-science/json/*.json'
    json_responses = glob.glob(path_to_json_dir)
    for path_to_json_response in json_responses:
        process_json(path_to_json_response)

    print('Id of repos that are not cloned')
    # Zip download ids:  33350195, 10075405
    pprint(not_cloned)

if __name__ == "__main__":
    main()
