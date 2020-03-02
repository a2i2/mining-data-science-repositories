import requests
import github

URL_PREFIX = 'https://api.github.com/repos/'

def send_get_request(url):
    headers = {'Authorization': 'token ' + github.ACCESS_TOKEN}
    response = requests.get(url, headers=headers)
    return response.json()

def build_url(repo_name):
    return URL_PREFIX + repo_name

def main():
    repo_name = '13o-bbr-bbq/machine_learning_security'
    url = build_url(repo_name)
    print(send_get_request(url))

if __name__ == "__main__":
    main()
