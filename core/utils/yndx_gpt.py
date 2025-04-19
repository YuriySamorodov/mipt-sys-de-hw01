import os
import json
import time
import jwt
import requests
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class YandexGPTManager:
    def __init__(self):
        self.model_uri = f"gpt://{os.getenv('YC_FOLDER_ID')}/yandexgpt-lite"
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.conversation_threads = {}
        self.key_file = r"C:\Users\Администратор\Desktop\YNDX_TG_BOT\authorized_key.json"
        self.iam_token = self._generate_iam_token()

    def _generate_iam_token(self):
        """Генерирует IAM-токен из authorized_key.json."""
        try:
            # 1. Читаем key.json
            with open(self.key_file, 'r') as f:
                key_data = json.load(f)

            # 2. Загружаем приватный ключ
            private_key = serialization.load_pem_private_key(
                key_data['private_key'].encode(),
                password=None,
                backend=default_backend()
            )

            # 3. Создаём JWT
            now = int(time.time())
            payload = {
                'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
                'iss': key_data['service_account_id'],
                'iat': now,
                'exp': now + 3600
            }
            headers = {'kid': key_data['id']}
            jwt_token = jwt.encode(
                payload,
                private_key,
                algorithm='PS256',
                headers=headers
            )

            # 4. Отправляем JWT для получения IAM-токена
            response = requests.post(
                'https://iam.api.cloud.yandex.net/iam/v1/tokens',
                json={'jwt': jwt_token}
            )

            # 5. Проверяем ответ
            if response.status_code == 200:
                return response.json().get('iamToken')
            else:
                raise Exception(f"Ошибка генерации IAM-токена: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(f"Не удалось сгенерировать IAM-токен: {str(e)}")

    def get_thread(self, chat_id):
        if chat_id not in self.conversation_threads:
            self.conversation_threads[chat_id] = [
                {"role": "system", "text": "Вы - полезный ассистент."}
            ]
        return self.conversation_threads[chat_id]

    async def send_message(self, chat_id, user_message):
        # Получаем историю сообщений для чата
        thread = self.get_thread(chat_id)
        # Добавляем сообщение пользователя
        thread.append({"role": "user", "text": user_message})

        # Формируем тело запроса
        payload = {
            "modelUri": self.model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": 1000
            },
            "messages": thread
        }

        # Заголовки с IAM-токеном
        headers = {
            "Authorization": f"Bearer {self.iam_token}",
            "Content-Type": "application/json"
        }

        try:
            # Отправляем асинхронный HTTP-запрос
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(self.api_url, headers=headers, json=payload)
            )

            # Проверяем статус ответа
            if response.status_code == 200:
                result = response.json()
                assistant_message = result["result"]["alternatives"][0]["message"]["text"]
                # Добавляем ответ ассистента в историю
                thread.append({"role": "assistant", "text": assistant_message})
                return assistant_message
            elif response.status_code == 401:
                # Пробуем обновить IAM-токен и повторить запрос
                self.iam_token = self._generate_iam_token()
                headers["Authorization"] = f"Bearer {self.iam_token}"
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.post(self.api_url, headers=headers, json=payload)
                )
                if response.status_code == 200:
                    result = response.json()
                    assistant_message = result["result"]["alternatives"][0]["message"]["text"]
                    thread.append({"role": "assistant", "text": assistant_message})
                    return assistant_message
                else:
                    return f"Ошибка API после обновления токена: {response.status_code} - {response.text}"
            else:
                return f"Ошибка API: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Ошибка: {str(e)}"