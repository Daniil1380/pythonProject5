import time

import requests

gitlab_url = ''
private_token = ' '


headers = {'PRIVATE-TOKEN': private_token}

user_projects = {}

with open("otus.txt", "w") as file:
    for i in range(1000):
        time.sleep(0.1)
        users_response = requests.get(f'{gitlab_url}/users?active=true&page=' + str(i), headers=headers)
        if users_response.status_code == 200:
            users = users_response.json()
            if len(users) == 0:
                break
            for user in users:
                user_id = user['id']
                print(user_id)
                print(user_projects)
                for j in range(1000):
                    time.sleep(0.1)
                    mrs_response = requests.get(f'{gitlab_url}/merge_requests?scope=all&author_id=' + str(user_id) + "&page=" + str(j),
                                                headers=headers)
                    if mrs_response.status_code == 404:
                        print("skip")
                        break
                    mrs = mrs_response.json()
                    if len(mrs) == 0:
                        break
                    for mr in mrs:
                        project_id = mr['project_id']
                        if user_id not in user_projects:
                            user_projects[user_id] = set()
                        user_projects[user_id].add(project_id)
    file.close()

# Сортируем пользователей по количеству проектов
sorted_users = sorted(user_projects.items(), key=lambda item: len(item[1]), reverse=True)

# Выводим результат
for user_id, projects in sorted_users:
    print(f'User ID: {user_id}, Projects: {len(projects)}')


