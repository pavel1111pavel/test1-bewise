import requests

url = "http://localhost:8000/quiz/"
questions_num = int(input("Введите количество вопросов: "))
data = {"questions_num": questions_num}
response = requests.post(url, json=data)
print(response.status_code)
if response.status_code == 200:
    print(response.json())
else:
    print('Запрос не удался')
