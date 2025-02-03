from dbase.create import check_db, create_db, start_write_table
from dbase.library import get_all_children
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from telebot import types as teletypes


def start(message, bot, session, nomess=0):
    buttons = [
        ["💊 Риски ПЭ/СЗРП"],
        ["👶 Регистрация ребенка"],
        ["📖 Справочник"],
    ]
    chat_id = message.chat.id
    check_baby = get_all_children(session, chat_id)
    if check_baby[chat_id]:
        buttons[2].append("💉 Моя вакцинация")

    if not nomess:
        hellowmessage = "Привет! Этот бот умеет оценивать риски СЗРП и преэклампсии во время беременности. Создан на основании данных RCOG"

    if nomess:
        hellowmessage = "возврат в главное меню"

    draw_buttons(bot, message, buttons, "row", hellowmessage)


def menu_guid_vaccine(message, bot):
    buttons = [
        ["📖 Общий график вакцинации"],
        ["📖 Список прививок за месяц"],
        ["📖 Инфекции", "📖 Препараты"],
        ["Главное меню"],
    ]
    draw_buttons(bot, message, buttons, "row")
    return


def draw_buttons(
    bot, message, list_names, type_add="add", msg_text="Выберите действие"
):
    chat_id = message.chat.id

    keyboard = teletypes.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(list_names)):
        list_buttons = []
        for btn in range(len(list_names[i])):
            list_buttons.append(teletypes.InlineKeyboardButton(text=list_names[i][btn]))
        if type_add == "row":
            keyboard.row(*list_buttons)
        else:
            for i in range(len(list_buttons)):
                keyboard.add(list_buttons[i])

    bot.send_message(chat_id, msg_text, reply_markup=keyboard)


def get_session(db_file):

    if not check_db(db_file):
        print(db_file)
        engine = create_db(db_file)
        session = Session(bind=engine)
        start_write_table(session)
    else:
        engine = create_engine("sqlite:///" + db_file)
        session = Session(bind=engine)

    return session


def menu_risk(message, bot):
    buttons = [
        [
            "💊 Оценить риски в текущую беременность",
            "💊 Показать предыдущий результат",
            "Главное меню",
        ]
    ]
    draw_buttons(bot, message, buttons, "add")
    return


def menu_my_vaccine(message, bot):
    buttons = [
        ["💉 Сертификат прививок"],
        ["💉 План вакцинации", "💉 Добавить вакцинацию"],
        ["Главное меню"],
    ]
    draw_buttons(bot, message, buttons, "row")
    return
