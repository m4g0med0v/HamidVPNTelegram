import requests

API_KEY = "6f4169a6dfb3d646ae40d27f4891ad33"
BASE_URL = "https://my.aeza.net/api/services/orders"

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

data = {
    "count": 1,
    "term": "hour",
    "name": "hamidvpn-2",
    "productId": 163,
    "parameters": {"os": 4320},
    "autoProlong": False,
    "method": "balance",
    "backups": False,
}

response = requests.post(BASE_URL, headers=headers, json=data)

if response.status_code == 200:
    print("Заказ успешно создан:", response.json())
else:
    print(f"Ошибка {response.status_code}: {response.text}")
