import os
import glob
import git
import time
import json
import github

def read_json_response(path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    return data

def clone_repo(clone_dir, clone_url):
    git.Repo.clone_from(clone_url, clone_dir)

def process_json(path_to_json_response):
    data = read_json_response(path_to_json_response)
    if data['id'] != 159175746 and data['id'] != 82329862 and data['id'] != 31302456 and data['id'] != 68827685 and data['id'] != 121175320 and data['id'] != 136026789:
        clone_dir = '/Users/akshatbajaj/Desktop/esolutions/mining-nlp-repos/cloned-repos/boa5/' + str(data['id'])
        clone_repo( clone_dir, data['html_url'])
        time.sleep(1)

def main():
    # Analyse json responses
    path_to_json_dir = 'data/boa/json/*.json'
    json_responses = glob.glob(path_to_json_dir)
    for path_to_json_response in json_responses:
        process_json(path_to_json_response)

if __name__ == "__main__":
    main()
