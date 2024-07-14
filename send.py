from requests import post
from json import dumps



class errors(BaseException):
    class UNAUTHORIZED(Exception):
        def __init__(self, name) -> None:
            self.name = name
        def __str__(self) -> str:
            return self.name
    class NOT_ENOUGH_MONEY(Exception):
        def __init__(self, name) -> None:
            self.name = name
        def __str__(self) -> str:
            return self.name

            


class Send:
    def __init__(self, TOKEN: str) -> None:
        self.TOKEN = TOKEN
        self.url = "https://pay.crypt.bot/api/"
        self.headers = {'Content-Type': 'application/json', 'Crypto-Pay-API-Token': TOKEN}
    

    def create_invoice(self, amount: float) -> dict:
        res = post(self.url + "createInvoice", json={'amount': amount, "currency_type": 'fiat', 'fiat': 'rub'}, headers=self.headers).json()
        if 'error' in res and res['error']['name'] == "UNAUTHORIZED":
            raise errors.UNAUTHORIZED("ТОКЕН НЕ ПОДХОДИТ")
        res = res['result']
        return res


    def get_invoice(self, invoice_id) -> dict:
        res = post(self.url + "getInvoices", json={'fiat': 'rub', 'invoice_ids': invoice_id}, headers=self.headers).json()
        if 'error' in res and res['error']['name'] == "UNAUTHORIZED":
            raise errors.UNAUTHORIZED("ТОКЕН НЕ ПОДХОДИТ")
        res = res['result']['items'][0]
        return res


    def create_cheque(self, amount, asset):
        res = post(self.url + "createCheck", json={'amount': amount, 'asset': asset}, headers=self.headers).json()
        if not 'result' in res:
            raise errors.NOT_ENOUGH_MONEY("ДЕНЯК НЕТУ")
        else:
            return res['result']
    
    def getMe(self):
        res = post(self.url + "getMe", headers=self.headers).json()
        return res
    
    def getBalance(self):
        res = post(self.url + "getBalance", headers=self.headers).json()
        return res


    





if __name__ == "__main__":
    send = Send("176102:AA5j7RnscqMCrTgqcuy3cmjP2EKhvS1tptT")
    # print(send.get_invoice(10330215))
    # print(send.create_invoice(1200))
    print(send.getBalance())