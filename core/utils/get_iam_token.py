import json
import time
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import requests

# 1. Читаем key.json
with open('../../authorized_key.json', 'r') as f:
    key_data = json.load(f)

# 2. Загружаем приватный ключ
private_key = serialization.load_pem_private_key(
    key_data['private_key'].encode(),
    password=None,
    backend=default_backend()
)

# 3. Создаём JWT
now = int(time.time())  # Текущее время в Unix формате
payload = {
    'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
    'iss': key_data['service_account_id'],
    'iat': now,
    'exp': now + 3600  # Токен действителен 1 час
}
headers = {
    'kid': key_data['id']
}
jwt_token = jwt.encode(
    payload,
    private_key,
    algorithm='PS256',
    headers=headers
)

# 4. Отправляем JWT в Yandex Cloud для получения IAM-токена
response = requests.post(
    'https://iam.api.cloud.yandex.net/iam/v1/tokens',
    json={'jwt': jwt_token}
)

# 5. Проверяем ответ
if response.status_code == 200:
    iam_token = response.json().get('iamToken')
    print('IAM-токен:', iam_token)
    print('Установите его в переменную окружения:')
    print(f'export YC_IAM_TOKEN={iam_token}')
else:
    print('Ошибка:', response.text)