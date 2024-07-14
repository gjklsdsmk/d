from kb import *
from config import *
from telebot import TeleBot
from requests import post, get
from telebot.types import *
from sqlite3 import connect
from time import time, ctime
from send import Send
from AaioAPI import AaioAPI
from random import choice
from io import FileIO
from fastapi import FastAPI, Request, HTTPException
from codes import CodeFlooder, check_proxies
from multiprocessing import Process
from fake_headers import Headers
from threading import Thread
from faker import Faker
from phone_gen import PhoneNumber



fuck = Faker()
headers = Headers(headers=True)
bot = TeleBot(BOT_TOKEN, "HTML")
con = connect("users.db", isolation_level=None, check_same_thread=False)
cursor = con.cursor()   
crypto = Send(CRYPTO_TOKEN)
symbols = list('wertyuioplkjhgfdsazxcvbnmERTYUIOPLKJHGFDSAZXCVBNM123456789')
for owner in OWNERS_IDS:
    cursor.execute("SELECT * FROM admins WHERE id=?", (owner,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO admins VALUES(?)", (owner,))
        con.commit()
aaio = AaioAPI(api_key, secret, merchant_id)
url = "http://twtonly.online/"
dem_pon = {}



def random_string(rnag: int = None):
    if rnag is None: return ''.join([choice(symbols) for _ in range(64)])
    else: return ''.join([choice(symbols) for _ in range(rnag)])



@bot.message_handler(['create_api'])
def create_api(message: Message):
    if message.from_user.id not in OWNERS_IDS: return
    try:
        hours = float(message.text.replace('/create_api ', "").strip())
        api = random_string(32)
        cursor.execute("INSERT INTO api_keys VALUES(?,?)", (api, time() + hours * 3600))
        con.commit()
        bot.reply_to(message, f'<b>API ключ на {hours} часов был успешно создан!\n\nВот он: <code>{api}</code></b>')
    except Exception as e:
        print(e, flush=True)
        bot.reply_to(message, f'<b>Ошибка!\nВы должны вводить команду вот так: <code>/create_api [количество часов]</code></b>')


@bot.message_handler(['delete_api'])
def delete_api(message: Message):
    if message.from_user.id not in OWNERS_IDS: return
    try:
        api = message.text.replace("/delete_api ", '')
        cursor.execute("SELECT * FROM api_keys WHERE key=?", (api,))
        if cursor.fetchone() is None: raise Exception
        cursor.execute("DELETE FROM api_keys WHERE key=?", (api,))
        con.commit()
        bot.reply_to(message, "Успешно, ключ был удалён")
    except: bot.reply_to(message, f'<b>Ошибка!\nЛибо ключ введен неправильно, либо он уже не существует\nПопробуйте так: <code>/delete_api [API ключ]</code>\n</b>')



def get_data(id: int, username: str = None, name: str = None):
    cursor.execute("SELECT * FROM users WHERE id=?", (id,))
    data = cursor.fetchone()
    if data is None:
        data = (id, username, name, None, None, None)
        cursor.execute("INSERT INTO users VALUES(?,?,?,?,?,?)", tuple(data))
    else:
        if username and name is None:
            return data
        cursor.execute("UPDATE users SET username=?, name=? WHERE id=?", (username, name, id))
        data = (id, username, name, data[3], data[4], data[5])
    return data


def create_invoice(amount, system):
    if "send" in system:
        return crypto.create_invoice(amount)
    else:
        order_id = random_string(8)
        desc = f"Пополнение в @{BOT_USERNAME}"
        return aaio.create_payment(order_id, amount, 'ru', 'RUB', desc), order_id


@bot.callback_query_handler(lambda message: not get_data(message.from_user.id, message.from_user.username, message.from_user.first_name.replace(">", "").replace(">", ""))[4] is None)
@bot.message_handler(func=lambda message: not get_data(message.from_user.id, message.from_user.username, message.from_user.first_name.replace(">", "").replace(">", ""))[4] is None)
def banned(message: Message):
    try:
        bot.reply_to(message, f"Вы забанены!")
    except:
        bot.answer_callback_query(message.id, f"Вы забанены!", True)



@bot.message_handler(['online'])
def online(message: Message):
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    bot.reply_to(message, f'''<b>На данный момент {ctime(time())[4:-8].replace("  ", ' ')}, {len(users)} пользователей\nПользователей с подпиской: {len(list(filter(lambda user: not user[3] is None, users)))}</b>''')


@bot.message_handler(['send'])
def senddada(message: Message):
    if message.from_user.id not in OWNERS_IDS: return
    cursor.execute("SELECT * FROM users")
    good, all = 0, 0
    for user in cursor.fetchall():
        try:
            bot.send_message(user[0], message.text.replace("/send", '').strip())
            good += 1
        except:
            all += 1
    bot.reply_to(message, f"Успешная рассылка\nБыло доставлено {good} пользователям из {all}")



@bot.message_handler(['ban'])
def ban(message: Message):
    cursor.execute("SELECT * FROM admins WHERE id=?", (message.from_user.id,))
    adm = cursor.fetchone()
    if adm is None: ...
    else:
        try:
            banning = int(message.text.replace('/ban ', ""))
            cursor.execute("UPDATE users SET rejected=1, subscribed=? WHERE id=?", (None, banning))
            con.commit()
            bot.reply_to(message, "Успешно!")
        except:
            bot.reply_to(message, "Вы должны вводить команду вот так: <code>/ban [ID пользователя]</code>")


@bot.message_handler(['unban'])
def unban(message: Message):
    cursor.execute("SELECT * FROM admins WHERE id=?", (message.from_user.id,))
    adm = cursor.fetchone()
    if adm is None: ...
    else:
        try:
            banning = int(message.text.replace('/unban ', ""))
            cursor.execute("UPDATE users SET rejected=? WHERE id=?", (None, banning))
            con.commit()
            bot.reply_to(message, "Успешно!")
        except:
            bot.reply_to(message, "Вы должны вводить команду вот так: <code>/unban [ID пользователя]</code>")


@bot.callback_query_handler(lambda call: call.data == "subscribe")
def subscribe(call: CallbackQuery):
    get_data(call.from_user.id, call.from_user.username, call.from_user.first_name.replace(">", "").replace("<", ""))
    bot.edit_message_text("Выберите способ оплаты", call.message.chat.id, call.message.id, reply_markup=subscribe_kb())


@bot.inline_handler(lambda query: query.query == 'share')
def inline_handler(query: InlineQuery):
    ref_link = f'https://t.me/{BOT_USERNAME}?start={query.from_user.id}'
    pon = InlineQueryResultArticle(query.id, "Поделится", InputTextMessageContent(f'<b>Привет!\nЗаходи в лучшего бота для сноса: <a href="{ref_link}">@{BOT_USERNAME}</a></b>', "HTML", disable_web_page_preview=True), description="Ссылка будет спрятана :)")
    bot.answer_inline_query(query.id, [pon])


@bot.callback_query_handler(lambda call: call.data == "ref_system")
def ref_system(call: CallbackQuery):
    data = get_data(call.from_user.id, call.from_user.username, call.from_user.first_name.replace(">", "").replace("<", ""))
    cursor.execute("SELECT id FROM users WHERE ref=?", (call.from_user.id,))
    ref_c = len(cursor.fetchall())
    ref_link = f'https://t.me/{BOT_USERNAME}?start={call.from_user.id}'
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Поделится", switch_inline_query="share"))
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))
    text = f'''<b>Приглашая по данной ссылке пользователей в бота вы будете получать 20% времени с купленной ими подписки\n\nВаша ссылка: <code>{ref_link}</code>\nКоличество ваших рефералов: {ref_c}</b>'''
    bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)


@bot.message_handler(['create_promo'])
def create_promo(message: Message):
    cursor.execute("SELECT * FROM admins WHERE id=?", (message.from_user.id,))
    if cursor.fetchone() is None: return
    try:
        hours = float(message.text.replace('/create_promo ', "").split()[0])
        try:
            count = int(message.text.replace('/create_promo ', '').split()[1])
        except:
            count = 1
        promo = random_string(6)
        cursor.execute("INSERT INTO promos VALUES(?,?,?,?)", (promo, hours, count, ""))
        con.commit()
        bot.reply_to(message, f'<b>Промокод на {hours} часов и {count} активаций был успешно создан!\n\nВот он: <code>{promo}</code></b>')
    except Exception as e:
        print(e, flush=True)
        bot.reply_to(message, f'<b>Ошибка!\nВы должны вводить команду вот так: <code>/create_promo [количество часов] [количество активаций]</code></b>')


@bot.message_handler(['stats'])
def stats(message: Message):
    cursor.execute("SELECT * FROM attacks")
    atks = cursor.fetchall()
    c = 0
    e = 0
    for atk in atks:
        if ctime(atk[5])[:-14]:
            c += atk[3]
            e += atk[2]
    if c > 1000:
        c = f"{round(c / 1000, 2)} тыс."
    if e > 1000:
        e = f'{round(e / 100, 2)} тыс.'
    bot.reply_to(message, f'<b>В нашем боте за последний день было произведено {len(atks)} атак\n\nЭто примерно {c} писем и {e} запросов на сайт поддержки телеграм.</b>')


@bot.callback_query_handler(lambda call: call.data == "start")
@bot.message_handler(['start'])
def start(message: Message):
    data = get_data(message.from_user.id, message.from_user.username, message.from_user.first_name.replace(">", "").replace("<", ""))
    try:
        ref = int(message.text.replace("/start ", ""))
        cursor.execute("SELECT * FROM users WHERE id=?", (ref,))
        if (ref_data := cursor.fetchone()) is None or ref == message.from_user.id:
            raise Exception
        else:
            cursor.execute("UPDATE users SET ref=? WHERE id=?", (ref, message.from_user.id))
            con.commit()
        bot.send_message(ref, f'<b>По вашей ссылке зарегистрировался пользователь {message.from_user.first_name.replace("<","").replace(">","")}</b>')
    except:
        ...
    if data[3] is None or (not data[3] is None and data[3] < time()):
        cursor.execute("UPDATE users SET subscribed=? WHERE id=?", (None, message.from_user.id))
        con.commit()
        keyboard = unsubscribed_kb()
        text = f'''<b>Добро пожаловать в {BOT_NAME}!\n\nС помощью нашего бота вы сможете отправлять большое количество жалоб на пользователей и их каналы\nПриобретите подписк кнопке ниже!</b>'''
    else:
        keyboard = subscribed_kb()
        text = f'''<b>Добро пожаловать в {BOT_NAME}!\n\nНачинайте пакости!\nВаша подписка длится до {ctime(float(data[3]))[4:-8].replace("  ", ' ')}</b>'''
    if type(message) is Message:
        bot.reply_to(message, text, reply_markup=keyboard)
    else:
        bot.edit_message_text(text, message.message.chat.id, message.message.id, reply_markup=keyboard)


@bot.message_handler(['users'], func=lambda message: message.from_user.id in OWNERS_IDS)
def usersdad(message: Message):
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    with open("users.csv", 'wb+') as file:
        file.write("ID  username  name subscribed  banned  ref".encode())
        for user in users:
            file.write(f'\n{user[0]}  {user[1]}  {user[2]}  {user[3]}  {user[4]}  {user[5]}'.encode())
    file = FileIO('users.csv', 'rb')
    file.name = "users.txt"
    bot.send_document(message.from_user.id, file, caption="Вся БД с пользователями")
    


@bot.message_handler(func=lambda message: len(message.text) == 6)
def promo_(message: Message):
    cursor.execute("SELECT * FROM promos WHERE promo=?", (message.text,))
    promo_data = cursor.fetchone()
    if promo_data is None:
        bot.reply_to(message, f'<b>Промокод <code>{message.text}</code> не найден</b>')
    else:
        if promo_data[2] <= 0:
            bot.reply_to(message, f'<b>Промокод на {promo_data[1]} часов уже активирован :(</b>')
        elif str(message.from_user.id) in promo_data[3]:
            bot.reply_to(message, f'<b>Вы уже активировали этот промокод</b>')
        else:    
            data = get_data(message.from_user.id, message.from_user.username, message.from_user.first_name.replace(">", "").replace("<", ""))
            pon = promo_data[3].split(";")
            pon.append(str(message.from_user.id))
            cursor.execute("UPDATE promos SET count=count-1, who_activated=? WHERE promo=?", (";".join(pon), message.text))
            if data[3] is None or float(data[3]) < time():
                cursor.execute("UPDATE users SET subscribed=? WHERE id=?", (time() + promo_data[1] * 3600, message.from_user.id))
            else:
                cursor.execute("UPDATE users SET subscribed=? WHERE id=?", (float(data[3]) + promo_data[1] * 3600, message.from_user.id))
            con.commit()
            bot.reply_to(message, f'<b>Успешно!\nПромокод на {promo_data[1]} часов был активирован, обновите главное меню - /start</b>')


@bot.callback_query_handler(lambda call: call.data == "promo_system")
def promo_system(call: CallbackQuery):
    text = '''<b>Вы можете ввести промокод и получить подписку на какое то количество часов\nПериодически происходят раздачи промокодов в @twtproject\nТак же промокоды можно ввести в любой момент, не обязательно находиться в этом меню\nПример промокода: aaaaaa</b>'''
    bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Назад", callback_data="start")))


@bot.callback_query_handler(lambda call: call.data == "cancel")
def cancel(call: CallbackQuery):
    bot.clear_step_handler(call.message)
    start(call)




class BigProcess():
    def __init__(self) -> None:
        self.proc_list = []
    
    def add(self, Process: Process):
        self.proc_list.append(Process)
    
    def run(self):
        for proc in self.proc_list:
            proc.start()

    def kill(self):
        for proc in self.proc_list:
            proc.kill()
    
    def stats(self):
        c = 0
        for proc in self.proc_list:
            if proc.is_alive():
                c += 1
        return c, len(self.proc_list)
    
    def is_alive(self):
        for proc in self.proc_list:
            if not proc.is_alive(): return False
        return True
    

def web_demolite(text, id):
    for proxy in proxies:
        try:
            post("https://telegram.org/support",
                {'message': text,
                    'email': fuck.company_email(),
                    "phone": PhoneNumber("Russia").get_number(),
                    "setln": 'ru'},
                headers=headers.generate(),
                proxies={"http": proxy, "https": proxy},
                timeout=1
            ).status_code
            cursor.execute("UPDATE attacks SET web=web+1 WHERE id=?", (id,))
            con.commit()
        except:
            cursor.execute("UPDATE attacks SET try=try+1  WHERE id=?", (id,))
            con.commit()



def email_demolite(text, id):
    for _ in range(100):
        try:
            sender = Faker(["RU"]).company_email()
            data = {
                "name": sender,
                "sender": sender,
                "title": text.split("\n")[0],
                "to": ", ".join(tg_emails),
                "text": text
            }
            r = get(url, data)
            print(r.content)
            if b"error" in r.content: raise Exception
            cursor.execute("UPDATE attacks SET mail=mail+1  WHERE id=?", (id,))
        except Exception as e: print(f"\n============================================\n{e}\n============================================\n") 
        cursor.execute("UPDATE attacks SET try=try+1  WHERE id=?", (id,))
        con.commit()



def demolitefunc(text: str, id: str):
    ufff = BigProcess()
    ufff.add(Process(target=email_demolite, args=(text,id), daemon=True))
    ufff.add(Process(target=web_demolite, args=(text,id), daemon=True))
    return ufff



def dem_check(message: Message, old_id):
    if len(message.text.strip()) > 50:
        bot.delete_message(message.chat.id, message.id)
        attack_id = random_string(32)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Подробнее", callback_data=f'a_{attack_id}'))
        msg = bot.edit_message_text(f"<b>Атака запущена!\nID: #{attack_id}\nПодробнее в истории атак</b>", message.chat.id, old_id, reply_markup=keyboard)
        cursor.execute("INSERT INTO attacks VALUES(?,?,?,?,?,?,?,?)", (attack_id, message.from_user.id, 0, 0, message.text.strip(), time(), len_proxies + 100, 0))
        con.commit()
        dem_pon[attack_id] = demolitefunc(message.text.strip(), attack_id)
        dem_pon[attack_id].run()
    else:
        try:
            bot.delete_message(message.chat.id, message.id)
        except: ...
        msg = bot.edit_message_text(f'''<b>Введите текст письма с жалобой
Первая строка будет использоваться в качестве заголовка!
Пример текста можете взять по <a href="https://telegra.ph/pon-05-29-3">этой ссылке</a>
                                
    <blockquote>Длина текста должна быть больше 50 символов!</blockquote></b>''', message.chat.id, old_id, reply_markup=cancel_kb())
        bot.register_next_step_handler(msg, dem_check, old_id)



@bot.callback_query_handler(lambda call: call.data == "demolite")
def demolite(call: CallbackQuery):
    data = get_data(call.from_user.id, call.from_user.username, call.from_user.first_name.replace(">", "").replace("<", ""))
    if data[3] is None or float(data[3]) < time():
        cursor.execute("UPDATE users SET subscribed=? WHERE id=?", (None, call.from_user.id))
        bot.answer_callback_query(call.id, "У вас нет подписки!")
        return start(call)
    cursor.execute("SELECT * FROM attacks WHERE cid=?", (call.from_user.id, ))
    atts = cursor.fetchall()
    for attack in atts:
        if time() - attack[5] < 1200: return bot.answer_callback_query(call.id, f"""Следующее рассылку вы сможете сделать в {ctime(attack[5] + 1200)[4:-8].replace("  ", ' ')}""", True)
    text = f'''<b>Введите текст письма с жалобой
Первая строка будет использоваться в качестве заголовка!
Пример текста можете взять по <a href="https://telegra.ph/pon-05-29-3">этой ссылке</a></b>'''
    msg = bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=cancel_kb())
    bot.register_next_step_handler(msg, dem_check, msg.id)


def is_phone(phone: str):
    if phone.isalnum() and 10 < len(phone) < 14: return True
    return False


def send_codeshand(message, old_id):
    try: bot.delete_message(message.chat.id, message.id)
    except: ...    
    try:
        phone = message.text.strip().replace("+", "").replace(" ", "")
        if not is_phone(phone):
            msg = bot.edit_message_text("<b>Введите НОМЕР ТЕЛЕФОНА</b>", message.chat.id, old_id, reply_markup=cancel_kb())
            bot.register_next_step_handler(msg, send_codeshand, old_id)
        else:
            cf = CodeFlooder(phone, proxies)
            Process(target=cf._send).start()
            bot.edit_message_text(f"<b>Началась попытка отправки запросов на номер +{phone}</b>", message.chat.id, old_id, reply_markup=cancel_kb())
    except Exception as e: 
        msg = bot.edit_message_text(f"<b>Введите номер телефона\nОшибка: {e}</b>", message.chat.id, old_id, reply_markup=cancel_kb())
        bot.register_next_step_handler(msg, send_codeshand, old_id)



@bot.callback_query_handler(lambda call: call.data == "codes")
def codes(call: CallbackQuery):
    msg = bot.edit_message_text("<b>Введите номер телефона</b>", call.message.chat.id, call.message.id, reply_markup=cancel_kb())
    bot.register_next_step_handler(msg, send_codeshand, msg.id)



@bot.callback_query_handler(lambda call: call.data.startswith("kill_"))
def kill_(call: CallbackQuery):
    attack_id = call.data.replace("kill_", "", 1)
    cursor.execute("SELECT * FROM attacks WHERE cid=?", (call.from_user.id,))
    atk = cursor.fetchall()
    if atk is None: bot.answer_callback_query(call.id, "Не получилось. Попробуйте обновить меню")
    else:
        if attack_id in dem_pon:
            dem_pon[attack_id].kill()
            bot.answer_callback_query(call.id, "Успешно! Aтака остановлена!")
        else:
            bot.answer_callback_query(call.id, "Атака и так остановлена")
        attacks(call)



@bot.callback_query_handler(lambda call: call.data == "attacks")
def attacks(call: CallbackQuery):
    cursor.execute("SELECT * FROM attacks WHERE cid=?", (call.from_user.id,))
    atk = cursor.fetchall()
    current_time = time()
    atcks = []
    for attack in atk:
        if current_time - attack[5] > 24 * 3600:
            cursor.execute("DELETE FROM attacks WHERE id=?", (attack[0],))
            con.commit()
        else:
            atcks.append(attack)
    
    if atcks == []: bot.answer_callback_query(call.id, "Вы не делали ни одну атаку за последний день", True)
    else:
        keyboard = InlineKeyboardMarkup()
        for attack in atcks:
            if attack[0] in dem_pon and dem_pon[attack[0]].is_alive():
                keyboard.row(InlineKeyboardButton(f"🟢 {attack[4][:21]}",  callback_data=f"a_{attack[0]}"))
            else:
                keyboard.row(InlineKeyboardButton(f"🔴 {attack[4][:21]}",  callback_data=f"a_{attack[0]}"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))
        bot.edit_message_text(f'<b>На данный момент у вас сохранено {len(atcks)} атак</b>', call.message.chat.id, call.message.id , reply_markup=keyboard)



@bot.callback_query_handler(lambda call: call.data.startswith("a_"))
def a_(call: CallbackQuery):
    attack_id = call.data.replace("a_", "", 1)
    cursor.execute("SELECT * FROM attacks WHERE id=?", (attack_id, ))
    attack_data = cursor.fetchone()
    if attack_data is None: bot.answer_callback_query(call.id, "Не найдено. Попробуйте обновить меню")
    else:
        keyboard = InlineKeyboardMarkup()
        percent = round(attack_data[7] / attack_data[6], 3) * 100
        text = f'<b>Атака #{attack_data[0]}\n<blockquote>{attack_data[4].replace(">", "").replace("<", "")}</blockquote>\nУспешных WEB запросов: {attack_data[2]}/{len_proxies}\nУспешных EMAIL писем: {attack_data[3]}/100\n\nАтака была завершена\nПроцесс выполнения {percent}%</b>'
        if attack_data[0] not in dem_pon:
            keyboard.row(InlineKeyboardButton("Назад", callback_data="attacks"))
        else:
            atk = dem_pon[attack_id]
            stat = atk.stats()
            if stat[0] == 0:
                keyboard.row(InlineKeyboardButton("♻️Обновить", callback_data=f"a_{attack_data[0]}"))
                keyboard.row(InlineKeyboardButton("Назад", callback_data="attacks"))
            else:
                percent = round(stat[0] / stat[1] * 100, 2)
                keyboard.row(InlineKeyboardButton("❌Стоп", callback_data=f"kill_{attack_data[0]}"), InlineKeyboardButton("♻️Обновить", callback_data=f"a_{attack_data[0]}"))
                keyboard.row(InlineKeyboardButton("Назад", callback_data="attacks"))
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)



@bot.callback_query_handler(lambda call: call.data in ("aaio", "send"))
def add_bal(call: CallbackQuery):
    text = f"<b>Выбранный способ оплаты: {call.data.capitalize()}\n\nВыберите срок на который хотите купить подписку</b>"
    keyboard = InlineKeyboardMarkup()
    if call.data == 'send':
        keyboard.row(InlineKeyboardButton("1 день - 60p", callback_data=f'{call.data}1'))
        keyboard.row(InlineKeyboardButton("Неделя - 200p", callback_data=f'{call.data}7'))
        keyboard.row(InlineKeyboardButton("Месяц - 400p", callback_data=f'{call.data}31'))
    else:
        keyboard.row(InlineKeyboardButton("Месяц - 400p", callback_data=f'{call.data}31'))
    keyboard.row(InlineKeyboardButton("Навсегда - 1200p", callback_data=f'{call.data}9999999'))
    keyboard.row(InlineKeyboardButton("Назад", callback_data=f'subscribe'))
    bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)



@bot.callback_query_handler(lambda call: call.data.startswith("aaio") or call.data.startswith("send"))
def create_sum(call: CallbackQuery):
    invo = create_invoice(PRICES[call.data.replace("aaio", "").replace("send", "")], call.data[:5])
    print(invo, "==============================", PRICES[call.data.replace("aaio", "").replace("send", "")], call.data[:4])
    if "send" in call.data:
        text = f'''<b>ID: {invo['invoice_id']}

После оплаты счёта не забудьте нажать кнопку проверить оплату
</b>'''
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Оплатить счёт", invo['pay_url']))
        keyboard.row(InlineKeyboardButton("Проверить оплату", callback_data="check_send"))
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)
    else:
        text = f'''<b>ID: {invo[1]}

После оплаты счёта не забудьте нажать кнопку проверить оплату
</b>'''
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Оплатить счёт", invo[0]))
        keyboard.row(InlineKeyboardButton("Проверить оплату", callback_data="check_aaio"))
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard, disable_web_page_preview=True)



@bot.callback_query_handler(lambda call: call.data == "check_aaio")
def check_aaio(call: CallbackQuery):
    order_id = call.message.text.split("\n")[0].replace("ID: ", '')
    if aaio.is_expired(order_id):
        bot.answer_callback_query(call.id, "Счёт удалён!", True)
        start(call)
    if aaio.is_success(order_id):
        data = get_data(call.from_user.id, call.from_user.username, call.from_user.first_name.replace(">", "").replace("<", ""))
        payment = aaio.get_payment_info(order_id)
        days = PRICE_TO_DAYS[payment['amount']]
        timing = time() + days * 24 * 3600
        if days > 9999:
            ref_days = time() + 24 * 3600 * 31
        else:
            ref_days = time() + 24 * 3600 * days * 0.2
        if not data[5] is None:
            try:
                bot.send_message(data[5], f'''Ваш реферал {call.from_user.first_name.replace("<", "").replace(">","")} купил подписку\nВам была выдана подписка до {ctime(ref_days)[4:-8].replace("  ", ' ')}!''')
                cursor.execute("UPDATE users SET subscribed=? WHERE id=?", (ref_days, data[5]))
            except:
                cursor.execute("UPDATE users SET ref=? WHERE id=?", (None, data[5]))
            con.commit()
        cursor.execute("UPDATE users SET subscribed=? WHERE id=?", (timing, call.from_user.id))
        con.commit()
        bot.answer_callback_query(call.id, f"Вам была выдана подписка навсегда", True)
        start(call)
    else:
        bot.answer_callback_query(call.id, "Счёт не был оплачен", True)





@bot.callback_query_handler(lambda call: call.data == "check_send")
def send_check(call: CallbackQuery):
    inv_id = call.message.text.split("\n")[0].replace("ID:", "", 1)
    invoice = crypto.get_invoice(inv_id)
    try:
        if invoice['status'] == "active":
            bot.answer_callback_query(call.id, f"Счёт не был оплачен!", True)
        elif invoice['status'] == 'paid':
            data = get_data(call.from_user.id, call.from_user.username, call.from_user.first_name.replace(">", "").replace("<", ""))
            days = PRICE_TO_DAYS[int(invoice['amount'])]
            timing = time() + days * 24 * 3600
            ref_days = days * 24 * 3600 * 0.8
            if not data[5] is None:
                try:
                    bot.send_message(data[5], f'''Ваш реферал {call.from_user.first_name.replace("<", "").replace(">","")} купил подписку до {ctime(timing)[4:-8].replace("  ", ' ')}.\nВам была выдана подписка до {ctime(timing - ref_days)[4:-8].replace("  ", ' ')}!''')
                    cursor.execute("UPDATE users SET subscribed=? WHERE id=?", (timing - ref_days, data[5]))
                except:
                    cursor.execute("UPDATE users SET ref=? WHERE id=?", (None, data[5]))
                con.commit()
            cursor.execute("UPDATE users SET subscribed=? WHERE id=?", (timing, call.from_user.id))
            con.commit()
            bot.answer_callback_query(call.id, f"""Вам была выдана подписка до {ctime(timing)[4:-8].replace("  ", ' ')}""", True)
            start(call)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Скорее всего счёт уже оплачен, удален и подписка была выдана", True)
        start(call)


class ExHandler:
    def handle(error):
        print(f'============================================\n{error}\n============================================')

pr = open("proxies.txt")
proxies = list(check_proxies(set(pr.read().split("\n")), True))



if __name__ == "__main__":
    print(len(proxies))
    len_proxies = len(proxies)
    bot.exception_handler = ExHandler
    bot.infinity_polling(timeout=100)
    # # bot.polling(True, timeout=100, interval=1)