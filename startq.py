import time

import requests

# Константы
GITLAB_TOKEN = ''
GITLAB_API_URL = ''
PER_PAGE = 100  # Количество результатов на страницу (максимум 100)
JAVA_THRESHOLD = 5

headers = {
    'Private-Token': GITLAB_TOKEN
}

user_projects = {}
reviewer_counts = {}


def get_projects():
    projects = []
    page = 1
    while True:
        response = requests.get(f"{GITLAB_API_URL}/projects?per_page={PER_PAGE}&page={page}", headers=headers)
        data = response.json()
        if not data:
            break
        for project in data:
            # Получаем информацию о языках в проекте
            languages = requests.get(f"{GITLAB_API_URL}/projects/{project['id']}/languages", headers=headers).json()
            # Проверяем, достаточно ли Java в проекте
            if JAVA_THRESHOLD <= languages.get('Java', 0) <= 100 - JAVA_THRESHOLD:
                projects.append(project)
                print(project['id'])
        page += 1
    return projects

def get_merge_requests(project_id):
    mrs = []
    page = 1
    print(project_id)
    while True:
        response = requests.get(f"{GITLAB_API_URL}/projects/{project_id}/merge_requests?state=all&per_page={PER_PAGE}&page={page}&created_after=2024-01-01T00:00:00Z", headers=headers)
        data = response.json()
        if not data or data == "{'message': '403 Forbidden'}":
            break
        if response.status_code == 403:
            break
        mrs.extend(data)
        page += 1
    return mrs

# Функция для получения количества комментариев в merge request
def get_comments_count(project_id, merge_request_iid):
    page = 1
    mrs = []
    while True:
        url = f'{GITLAB_API_URL}/projects/{project_id}/merge_requests/{merge_request_iid}/commits?page={page}'
        headers = {'PRIVATE-TOKEN': GITLAB_TOKEN}
        response = requests.get(url, headers=headers)
        data = response.json()
        if not data or data == "{'message': '403 Forbidden'}":
            break
        if response.status_code == 403:
            break
        mrs.extend(data)
        page += 1
    return len(mrs)

def get_reviewers(project_id, merge_request_iid, mr):
    """Извлекает список reviewers из MR."""
    data = mr['reviewers']
    if not data or data == "{'message': '403 Forbidden'}":
        return []
    reviewers = []
    for approval in data:
        reviewer = approval['id']
        print("---------")
        print(mr['author']['id'])
        print("---------")
        if reviewer and reviewer != mr['author']['id']:
            reviewers.append(reviewer)
    return reviewers

def find_largest_mr():
    largest_mr = None
    for project in get_projects():
        print(project['id'])
        for mr in get_merge_requests(project['id']):
            reviewers = get_reviewers(project['id'], mr['iid'], mr)
            for reviewer in reviewers:
                if reviewer in reviewer_counts:
                    reviewer_counts[reviewer] += 1
                else:
                    reviewer_counts[reviewer] = 1
    print(reviewer_counts)
    print(max(reviewer_counts, key=reviewer_counts.get))
    return largest_mr

if __name__ == "__main__":
    largest_mr = find_largest_mr()



