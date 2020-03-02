import os
import requests
import json
import github
import boa_repos

URL_PREFIX = 'https://api.github.com/repos/'

def send_get_request(url):
    headers = {'Authorization': 'token ' + github.ACCESS_TOKEN}
    response = requests.get(url, headers=headers)
    return response.json()

def build_url(repo_name):
    return URL_PREFIX + repo_name

def get_repo_details(url):
    return send_get_request(url)

def write_json_response(object_to_write, path_to_file):
    directory = os.path.dirname(path_to_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path_to_file, 'w', encoding='utf-8') as f:
        json.dump(object_to_write, f, ensure_ascii=False, indent=4)

def get_file_path(file_name):
    path = os.path.join('data/boa/json', str(file_name) + '.json')
    return path

def main():
    for repo in boa_repos.BOA_REPOS:
        url = build_url(repo)
        repo_details = get_repo_details(url)
        path = get_file_path(repo_details['id'])
        write_json_response(repo_details, path)


if __name__ == "__main__":
    main()
