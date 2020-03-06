import os
import requests
import json
import csv
import glob
import github

BIG_QUERY_CSV = 'data/non-data-science/big_query.csv'
PATH_TO_CSV = 'data/non-data-science/github_api.csv'

def send_get_request(url):
    headers = {'Authorization': 'token ' + github.ACCESS_TOKEN}
    response = requests.get(url, headers=headers)
    return response.json()

def get_repo_details(url):
    return send_get_request(url)

def read_json_response(path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    return data

def write_json_response(object_to_write, path_to_file):
    directory = os.path.dirname(path_to_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path_to_file, 'w', encoding='utf-8') as f:
        json.dump(object_to_write, f, ensure_ascii=False, indent=4)

def read_csv(path_to_file):
    with open(path_to_file, 'r', newline='', encoding='utf8') as result:
        data = list(csv.reader(result, delimiter=','))
        result.close()

    return data

def write_csv(object_to_write, path_to_file):
    directory = os.path.dirname(path_to_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path_to_file, 'a+', newline='', encoding='utf8') as result:
        writer = csv.writer(result, delimiter=',')
        writer.writerow(object_to_write)

def get_file_path(file_name):
    path = os.path.join('data/non-data-science/json', str(file_name) + '.json')
    return path

def process_json(path_to_json):
    data = read_json_response(path_to_json)
    object_to_write = [data['id'], data['name'], data['full_name'], data['url'], data['html_url'], data['stargazers_count'], data['created_at'], data['updated_at'], data['pushed_at'], data['size'], data['language'], data['forks_count'], data['open_issues_count'], data['subscribers_count'], data['description']]
    write_csv(object_to_write, PATH_TO_CSV)

def generate_csv():
    csv_header = ['id', 'name', 'full_name', 'url', 'html_url', 'stars', 'created_at', 'updated_at', 'pushed_at', 'size', 'language', 'forks_count', 'open_issues_count', 'watch', 'description']
    write_csv(csv_header, PATH_TO_CSV)

    # Analyse json responses
    path_to_json_dir = 'data/non-data-science/json/*.json'
    json_responses = glob.glob(path_to_json_dir)
    for path_to_json_response in json_responses:
        process_json(path_to_json_response)


def main():
    repos_from_big_query = read_csv(BIG_QUERY_CSV)
    repos_from_big_query.pop(0)
    for repo in repos_from_big_query:
        url = repo[2]
        repo_details = get_repo_details(url)
        if 'name' in repo_details:
            path = get_file_path(repo_details['id'])
            write_json_response(repo_details, path)

    # Generate csv from the json responses
    generate_csv()

if __name__ == "__main__":
    main()
