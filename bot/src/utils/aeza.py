from dataclasses import dataclass
from typing import Optional

import requests
from requests import Response


@dataclass
class AezaResponse:
    status: str
    context: str


class Aeza:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.HEADERS = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        self.BASE_URL = "https://my.aeza.net/api"
        self.TIMEOUT = 10

    def _check_response(self, response: Response) -> AezaResponse:
        """Проверка ответа сервера."""
        try:
            response.raise_for_status()
            return AezaResponse(status="ok", context=response.json())
        except requests.exceptions.JSONDecodeError:
            return AezaResponse(
                status="error",
                context=(
                    "Ошибка: Некорректный JSON-ответ."
                    f"Ответ сервера: {response.text}"
                ),
            )
        except requests.exceptions.RequestException as e:
            return AezaResponse(
                status="error",
                context=(
                    f"Ошибка запроса: {str(e)}. Ответ сервера: {response.text}"
                ),
            )

    def _request(self, method: str, endpoint: str, **kwargs) -> AezaResponse:
        """Обёртка для запросов с обработкой ошибок."""
        try:
            response = requests.request(
                method,
                self.BASE_URL + endpoint,
                headers=self.HEADERS,
                timeout=self.TIMEOUT,
                **kwargs,
            )
            return self._check_response(response)
        except requests.exceptions.RequestException as e:
            return AezaResponse(
                status="error", context=f"Ошибка сети: {str(e)}"
            )

    def get_os(self) -> AezaResponse:
        """Выводит список OS доступных для установки на сервер."""
        return self._request("GET", "/os")

    def get_recipe(self) -> AezaResponse:
        """
        Выводит список программных обеспечений,
        которые могут быть установлены на сервер.
        """
        return self._request("GET", "/vm/recipe")

    def get_payment_currencies(self):
        """Выводит список множителей для преобразования валют.

        В настройках можно выбрать отображение цен в другой валюте.
        На стороне сервера и API все цены рассчитаны в стандартной валюте,
        в рублях. Для отображения в другой валюте они перемножаются на текущий
        курс данной валюты по отношению к главной.

        Чтобы получить список множителей нужно отправить
        запрос GET payment/currencies. Для преобразования средств в другую
        валюту используется формула: ceil(value * multiplier * R) / R, где R,
        это 10 ** round, value - средства в изначальном виде,
        multiplier - множитель валюты, round - количество знаков после запятой
        для округления валюты.
        """
        return self._request("GET", "/payment/currencies")

    def get_my_services(self) -> AezaResponse:
        """Выводит список купленных услуг."""
        return self._request("GET", "/services")

    def get_sevices_list(self) -> AezaResponse:
        """Выводит список всех доступных для покупки услуг."""
        return self._request("GET", "/services/products")

    def get_service(self, service_id: int) -> AezaResponse:
        """Получение информации об услуге по его id."""
        return self._request("GET", f"/services/{service_id}")

    def get_order_list(self) -> AezaResponse:
        """Выводит информацию о заказе."""
        return self._request("GET", "/services/orders")

    def create_service(
        self,
        count: int,
        term: str,
        name: str,
        product_id: int,
        parameters: dict,
        auto_prolog: bool,
        method: str,
        backups: bool,
    ) -> AezaResponse:
        """Заказ сервера."""
        data = {
            "count": count,
            "term": term,
            "name": name,
            "productId": product_id,
            "parameters": parameters,
            "autoProlong": auto_prolog,
            "method": method,
            "backups": backups,
        }
        return self._request("POST", "/services/orders", json=data)

    def _control_service(self, service_id: int, action: str) -> AezaResponse:
        """
        Универсальный метод для управления сервером
        (запуск, стоп, перезагрузка).
        """
        if action not in {"resume", "suspend", "reboot"}:
            return AezaResponse(
                status="error", context="Некорректное действие"
            )
        return self._request(
            "POST", f"/services/{service_id}/ctl", json={"action": action}
        )

    def start_service(self, service_id: int) -> AezaResponse:
        """Запуск сервера."""
        return self._control_service(service_id, "resume")

    def stop_service(self, service_id: int) -> AezaResponse:
        """Остановка сервера."""
        return self._control_service(service_id, "suspend")

    def reboot_service(self, service_id: int) -> AezaResponse:
        """Перезагрузка сервера."""
        return self._control_service(service_id, "reboot")

    def reinstall_service(
        self,
        service_id: int,
        os: int,
        password: str,
        recipe: Optional[int] = None,
    ):
        """Переустановка сервера."""
        return self._request(
            "POST",
            f"/services/{service_id}/reinstall",
            json={"os": os, "recipe": recipe, "password": password},
        )

    def change_password(self, service_id: int, password: str) -> AezaResponse:
        """Смена пороля сервера."""
        return self._request(
            "PUT",
            f"/services/{service_id}/changePassword",
            json={"password": password},
        )

    def change_name(self, service_id: int, name: str) -> AezaResponse:
        """Смена имени сервера."""
        return self._request(
            "PUT", f"/services/{service_id}/changeName", json={"name": name}
        )

    def delete_service(self, service_id: int) -> AezaResponse:
        """Удаление сервера."""
        return self._request("DELETE", f"/services/{service_id}")
