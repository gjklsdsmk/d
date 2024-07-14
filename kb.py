from telebot.types import *








def subscribed_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Снос", callback_data="demolite"), InlineKeyboardButton("Спам кодами", callback_data="codes"))
    keyboard.row(InlineKeyboardButton("История атак", callback_data="attacks"))
    keyboard.row(InlineKeyboardButton("Рефералка", callback_data="ref_system"), InlineKeyboardButton("Промокоды", callback_data="promo_system"))
    keyboard.row(InlineKeyboardButton("Поддержка/API доступ", "https://t.me/CACYH_HEHE"))
    return keyboard

def unsubscribed_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Купить подписку", callback_data="subscribe"))
    keyboard.row(InlineKeyboardButton("История атак", callback_data="attacks"))
    keyboard.row(InlineKeyboardButton("Рефералка", callback_data="ref_system"), InlineKeyboardButton("Промокоды", callback_data="promo_system"))
    keyboard.row(InlineKeyboardButton("Поддержка/API доступ", "https://t.me/CACYH_HEHE"))
    return keyboard

def subscribe_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("AAIO", callback_data="aaio"))
    keyboard.row(InlineKeyboardButton("CryptoBot", callback_data="send"))
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))
    return keyboard

def cancel_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Отмена", callback_data="cancel"))
    return keyboard