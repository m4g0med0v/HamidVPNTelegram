import json

import requests

# /services - получение всех купленных серверов
# /services/products - получение всех серверов для покупки
# /services/<ID> - получение информации про определенный сервер
#

API_KEY = "6f4169a6dfb3d646ae40d27f4891ad33"
BASE_URL = "https://my.aeza.net/api"
ENDPOINT = "/services"

headers = {"X-API-Key": API_KEY}

# vps_list = ["DEs-1", "VIEs-1", "NLs-1", "SWEs-1", "HELs-1", "PARs-1", "LNDs-1", "ALBs-1"]

response = requests.get(BASE_URL + ENDPOINT, headers=headers)

# # Проверяем статус-код перед обработкой JSON
if response.status_code == 200:
    try:
        # response = response.json()
        #     item_list = []
        #     for item in response["data"]["items"]:
        #         if item["type"] == "vps" and item["name"] in vps_list:
        #             print((item["id"], item["name"], item["type"]))
        #             item_list.append((item["id"], item["name"], item["type"]))

        with open(f"aeza/{ENDPOINT[1:].replace('/', '_')}.json", "w") as file:
            json.dump(response.json(), file, indent=2)
    except requests.exceptions.JSONDecodeError:
        print("Ошибка: сервер вернул пустой или некорректный JSON-ответ")
else:
    print(
        f"Ошибка: {response.status_code}, {json.dumps(response.json(), indent=2)}"
    )
