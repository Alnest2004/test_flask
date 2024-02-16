from locust import HttpUser, TaskSet, task, between
import random
import string

'''
Данный файл создан для тестирования,  чтобы запустить тестирование с помощью Locust,
выполните следующую команду в терминале:
locust -f locustfile.py
После этого вы сможете перейти по адресу http://localhost:8089 в
своем браузере и настроить параметры тестирования,
'''

class UserBehavior(TaskSet):
    cities = ['London', 'Paris', 'New York', 'Tokyo', 'Moscow']

    @task(1)
    def update_balance(self):
        city = random.choice(self.cities)
        username = ''.join(random.choices(string.ascii_lowercase, k=10))  # Генерируем случайное имя пользователя
        self.client.get(f"/update_balance?username={username}&city={city}")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(0.1, 3)  # Время ожидания между запросами
