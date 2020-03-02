import requests
import github
import boa_repos

URL_PREFIX = 'https://api.github.com/repos/'

def send_get_request(url):
    headers = {'Authorization': 'token ' + github.ACCESS_TOKEN}
    response = requests.get(url, headers=headers)
    return response.json()

def build_url(repo_name):
    return URL_PREFIX + repo_name

def main():
    for repo in boa_repos.BOA_REPOS:
        url = build_url(repo)
        print(send_get_request(url))

if __name__ == "__main__":
    main()
