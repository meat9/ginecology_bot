from bot.utils import draw_buttons, start
from dbase.library import (
    getListVacByMonth,
    get_all_drugs,
    get_all_drugs_by_like,
    get_all_patogen_with_drugs,
    get_all_patogens_by_like,
    get_drug_full_info,
    get_patogen_info,
    prep_str_future_vac,
)
from log import Logging
from telebot import types as teletypes


def get_all_vaccination_info(message, bot, session):
    chat_id = message.chat.id
    is_result = 0
    for i in range(0, 25):

        res = getListVacByMonth(session, i)
        if res:
            is_result = 1
            mess = prep_str_future_vac(res, i)
            bot.send_message(
                chat_id,
                mess,
            )
    if not is_result:
        log = Logging(__name__,bot)
        log.error(message, __name__, __file__, " Для указанного интервала нет прививок")
        bot.send_message(chat_id, "Для указанного интервала нет прививок")
    return


def get_info_by_period(message, session, bot):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "Введите интервал месяцев в формате 'начало'-'конец'. Например 3-4 месяца для получения информации с 3его по 4ый месяцы",
    )
    bot.send_message(
        chat_id,
        "Так же можно просто ввести номер месяца для получения информации на указанный месяц",
    )
    bot.register_next_step_handler(message, list_vac_month_main, session, bot)


def list_vac_month_main(message, session, bot):
    chat_id = message.chat.id
    text = message.text
    if "Главное меню" in text:
        start(message, bot, session, 1)
        return
    elif "Общий график вакцинации" in text:
        get_all_vaccination_info(message, bot, session)
        return
    elif "Список прививок за месяц" in text:
        get_info_by_period(message, session, bot)
        return
    elif "Инфекции" in text:
        get_infection_info(message, session, bot)
        return
    elif "Препараты" in text:
        get_drug_info(message, session, bot)
        return

    try:
        number = int(text)
        list_vac_sender(bot, session, chat_id, number)
    except:
        try:
            monts = text.split("-")
            start_m = int(monts[0])
            stop_m = int(monts[1])
            for number in range(start_m, stop_m + 1):
                list_vac_sender(bot, session, chat_id, number)
        except:
            log = Logging(__name__,bot)
            log.error(message, __name__, __file__, " Ошибка при вводе месяца. Пользователь ввел: '"+text+"'")
            bot.send_message(chat_id, "Ошибка при вводе месяца")
            bot.send_message(
                chat_id,
                "Необходимо ввести число или диапазон чисел через - (например 3 или 2-3)",
            )
            bot.send_message(
                chat_id, "Пожалуйста повторите попытку, или выберите нужный пункт меню"
            )
            bot.register_next_step_handler(
                message, list_vac_month_main, session, bot
            )
            return

    keyboard = teletypes.InlineKeyboardMarkup()
    buttons = ()
    for answer in ["Да", "Нет"]:
        text = answer
        buttons += (
            teletypes.InlineKeyboardButton(
                text=text,
                callback_data="list_vac_next#" + str(text) + "#" + str(chat_id),
            ),
        )
    keyboard.add(*buttons)
    bot.send_message(
        chat_id, "Понадобятся данные за другой месяц?", reply_markup=keyboard
    )


def list_vac_sender(bot, session, chat_id, number):
    res = getListVacByMonth(session, number)
    is_result=0
    if res:
        is_result = 1
        mess = prep_str_future_vac(res, number)
        bot.send_message(
            chat_id,
            mess,
        )
        
    if not is_result:
        bot.send_message(chat_id, "Для указанного интервала нет прививок")
    return


def list_vac_next(call, session, bot):
    answer = call.data.split("#")[1]
    chat_id = call.data.split("#")[2]
    if answer == "Да":
        bot.send_message(chat_id, "Введите номер месяца")
        bot.register_next_step_handler(
            call.message, list_vac_month_main, session, bot
        )
    else:
        bot.send_message(chat_id, "Выберите действие")


def get_infection_info(message, session, bot):
    handler_info_buttons(message, session, bot, "patogen")


def get_drug_info(message, session, bot):
    handler_info_buttons(message, session, bot, "drug")


def handler_info_buttons(message, session, bot, type_message):
    chat_id = message.chat.id

    keyboard = teletypes.InlineKeyboardMarkup()
    buttons = [["Главное меню", "📖 Назад"]]
    draw_buttons(bot, message, buttons, "row", "📖")
    if type_message == "patogen":
        call_back_head = "pat_info_first#"
        info_dict = get_all_patogen_with_drugs(session)
        res_message = "Выберите первую букву инфекции"
    elif type_message == "drug":
        call_back_head = "drug_info_first#"
        info_dict = get_all_drugs(session)
        res_message = "Выберите первую букву препарата"
    obj_first_letter = set()
    for i in info_dict:
        obj_first_letter.add(i["name"][0].lower())

    buttons = ()
    obj_first_letter = sorted(obj_first_letter)

    for elem in obj_first_letter:
        msg_text = elem
        callback_text = elem + "#" + str(chat_id)
        buttons += (
            teletypes.InlineKeyboardButton(
                text=msg_text,
                callback_data=call_back_head + callback_text,
            ),
        )
    keyboard.add(*buttons)

    bot.send_message(chat_id, res_message, reply_markup=keyboard)


def send_info_first(call, session, bot, type_message):
    first_letter = call.data.split("#")[1]
    chat_id = call.data.split("#")[2]
    keyboard = teletypes.InlineKeyboardMarkup()
    if type_message == "patogen":
        call_back_head = "pat_info#"
        info_dict_lower = get_all_patogens_by_like(session, first_letter)
        info_dict_upper = get_all_patogens_by_like(session, first_letter.upper())
        info_dict = info_dict_lower + info_dict_upper
        res_message = "Выберите инфекцию"
    elif type_message == "drug":
        call_back_head = "drug_info#"
        info_dict_lower = get_all_drugs_by_like(session, first_letter)
        info_dict_upper = get_all_drugs_by_like(session, first_letter.upper())
        info_dict = info_dict_lower + info_dict_upper
        res_message = "Выберите препарат"
    buttons = ()
    for elem in info_dict:
        msg_text = elem["name"]
        callback_text = str(elem["id"]) + "#" + str(chat_id)
        buttons += (
            teletypes.InlineKeyboardButton(
                text=msg_text,
                callback_data=call_back_head + callback_text,
            ),
        )
    keyboard.add(*buttons)

    bot.send_message(chat_id, res_message, reply_markup=keyboard)


def send_infection_info(call, session, bot):
    patogen_id = call.data.split("#")[1]
    chat_id = call.data.split("#")[2]
    patogen_dict_info = get_patogen_info(session, patogen_id)

    str_drugs = patogen_dict_info["drugs_names"].replace(";", ", ")
    str_res = "Название инфекции: " + patogen_dict_info["name"] + "\n" + "\n"
    str_res += "Описание: " + patogen_dict_info["title"] + "\n" + "\n"
    if str_drugs != "":
        str_res += "Список препаратов: " + str_drugs + "\n" + "\n"
    str_res += "Подробнее: " + patogen_dict_info["link"] + "\n"
    bot.send_message(chat_id, str_res)


def send_drug_info(call, session, bot):
    drug_id = call.data.split("#")[1]
    chat_id = call.data.split("#")[2]
    drug_dict_info = get_drug_full_info(session, drug_id)
    str_patogens = drug_dict_info["patogens_names"].replace(";", ", ")
    str_res = "Название препарата: " + drug_dict_info["name"] + "\n"
    if str_patogens != "":
        str_res += "Список инфекций: " + str_patogens + "\n"
    str_res += "Описание: " + drug_dict_info["title"] + "\n"
    if drug_dict_info["description"] != "":
        str_res += drug_dict_info["description"] + "\n"
    str_res += (
        "\n"
        + "Противопоказания: "
        + drug_dict_info["warning"].replace(";\n", ", ")
        + "\n"
        + "\n"
    )
    str_res += "Возраст: " + drug_dict_info["age"] + "\n"
    str_res += "Подробнее: " + drug_dict_info["link"] + "\n"

    bot.send_message(chat_id, str_res)
