from config import settings

import json
import requests


class MrStoneAPI:
    def __init__(self) -> None:
        self.url = settings.mrstone_api_url
        self.auth_token = settings.mrstone_api_auth_token

    def sendRequest(self, method: str, url: str, data: dict = {}, headers: dict = {}) -> dict:
        """Sends request to Telegram API.

        :param request_method: http request method (`get`, `post`, `patch`, `delete`).
        :param api_method: the required method in Telegram API.
        """

        args = (url, data)
        kwargs = {'headers': headers}
        match method.upper():
            case 'GET': r = requests.get(*args, **kwargs)
            case 'POST': r = requests.post(*args, **kwargs)
            case 'PATCH': r = requests.patch(*args, **kwargs)
            case 'DELETE': r = requests.delete(*args, **kwargs)

        response = {
            'code': r.status_code,
            'text': r.text,
        }
        
        return response

    def getOrder(self, order_id: str) -> dict:
        endpoint_url = self.url + f'store/orders/{order_id}/'

        response = self.sendRequest('get', endpoint_url)
        response_data = json.loads(response['text'])
        
        order = response_data['details']['order']
        return order

    def getOrdersByContact(self, contact: str, contact_type: str) -> list:
        endpoint_url = self.url + 'store/orders/'
        data = {'contact': contact, 'contact_type': contact_type}

        response = self.sendRequest('get', endpoint_url, data)
        response_data = json.loads(response['text'])
        
        orders = response_data['details']['orders']
        return orders

