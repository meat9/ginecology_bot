from telebot import types as teletypes
from bot.utils import start, draw_buttons, menu_my_vaccine
from log import Logging
from dbase.library import (
    prep_str_future_vac,
    user_exist,
    write_to_bd,
    str_to_date,
    get_all_children,
    get_children_vaccine_info,
    get_children_info,
    date_diff,
    get_all_patogen_with_drugs,
    get_drug_for_patogen,
    get_plain_vaccine,
    get_vacc_pass,
)


def baby_registration(message, session, bot, baby_reg_dict):
    buttons = [["Главное меню"]]
    draw_buttons(bot, message, buttons, "row", "Регистрация ребенка в базе")
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите имя ребенка")
    bot.register_next_step_handler(
        message, write_baby, session, bot, baby_reg_dict
    )


def write_baby(message, session, bot, baby_reg_dict):
    chat_id = message.chat.id
    if message.text == "Главное меню":
        try:
            del baby_reg_dict[chat_id]
        except:
            log = Logging(__name__,bot)
            log.error(
                message, __name__, __file__, " Ошибка при очистке словаря baby_reg_dict"
            )
        start(message, bot, session, 1)
        return
    if not baby_reg_dict.get(chat_id):
        baby_reg_dict[chat_id] = {}
        baby_reg_dict[chat_id]["name"] = message.text
        bot.send_message(chat_id, "Введите дату рождения ребенка в формате ДД.ММ.ГГГГ")
        bot.register_next_step_handler(
            message, write_baby, session, bot, baby_reg_dict
        )
        return "date"
    date = str_to_date(message.text)

    if date == "error":
        bot.send_message(
            chat_id,
            "Ошибка при вводе даты. Введите дату рождения ребенка в формате ДД.ММ.ГГГГ",
        )
        bot.register_next_step_handler(
            message, write_baby, session, bot, baby_reg_dict
        )
        return "date"

    baby_reg_dict[chat_id]["birth_date"] = date
    baby_reg_dict[chat_id]["parent_id"] = chat_id
    write_user(message, session)
    write=write_to_bd(session, "Baby", **baby_reg_dict[chat_id])
    if write==0:
        bot.send_message(chat_id, "Ребенок не сохранен в базе")
    else:
        bot.send_message(chat_id, "Ребенок успешно сохранен в базе")
    try:
        
        del baby_reg_dict[chat_id]
        start(message, bot, session, 1)
    except:
        log = Logging(__name__,bot)
        log.error(
            message, __name__, __file__, " Ошибка при очистке словаря baby_reg_dict"
        )


def write_user(message, session):
    chat_id = message.chat.id
    create_user = {}
    create_user[chat_id] = {}
    create_user[chat_id]["chat_id"] = chat_id
    create_user[chat_id]["name"] = message.chat.username
    if not user_exist(session, chat_id):
        write=write_to_bd(session, "User", **create_user[chat_id])
    try:
        del create_user[chat_id]
    except:
        log = Logging(__name__)
        log.error(message, __name__, __file__, " Ошибка при очистке словаря create_user")


def handler_baby_buttons(message, session, bot):
    chat_id = message.chat.id
    baby_dict = get_all_children(session, chat_id)
    keyboard = teletypes.InlineKeyboardMarkup()
    buttons = [["Главное меню", "💉 Назад"]]
    draw_buttons(bot, message, buttons, "row", "👶")
    if message.text == "💉 Сертификат прививок":
        call_back_head = "get_baby#"
    elif message.text == "💉 План вакцинации":
        call_back_head = "get_future#"
    else:
        call_back_head = "get_vac#"

    for i in baby_dict[chat_id]:
        id_baby = i["id"]
        name_baby = i["name"]
        birth_date = i["birth_date"]
        msg_text = name_baby + " дата рождения: " + str(birth_date)
        callback_text = str(id_baby) + "#" + str(name_baby) + "#" + str(chat_id)
        keyboard.add(
            teletypes.InlineKeyboardButton(
                text=msg_text,
                callback_data=call_back_head + callback_text,
            )
        )
    bot.send_message(chat_id, "Выберите ребенка", reply_markup=keyboard)


def handler_baby_vaccine_info(call, session, bot):
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id
    id_baby = call.data.split("#")[1]
    name_baby = call.data.split("#")[2]
    vacc_list = get_children_vaccine_info(session, id_baby)

    bot.delete_message(chat_id, message_id)
    message = "Ребенок: " + call.data.split("#")[2] + " ✅"
    bot.send_message(chat_id, message)
    if not vacc_list:
        bot.send_message(chat_id, "нет данных о вакцинации у " + name_baby)
    else:
        for i in vacc_list:
            bot.send_message(
                chat_id,
                "Вакцина: "
                + str(i.get("patogen"))
                + "\n"
                + "Препарат: "
                + str(i.get("drug"))
                + "\n"
                + "Дата прививки: "
                + str(i.get("date_medication"))
                + "\n"
                + "Возраст ребенка: "
                + str(i.get("baby_age"))
                + " мес.",
            )


def handler_vaccine_registration(message, session, bot, vacc_reg_dict):
    handler_baby_buttons(message, session, bot)
    bot.register_next_step_handler(
        message, write_vaccine_baby, session, bot, vacc_reg_dict
    )


def handler_patogen_buttons(chat_id, session, bot):

    patogen_list = get_all_patogen_with_drugs(session)
    keyboard = teletypes.InlineKeyboardMarkup()
    for i in patogen_list:
        id_patogen = i["id"]
        name_patogen = i["name"]
        keyboard.add(
            teletypes.InlineKeyboardButton(
                text=name_patogen,
                callback_data="get_pat#" + str(id_patogen) + "#" + str(name_patogen),
            )
        )
    bot.send_message(chat_id, "Выберите прививку", reply_markup=keyboard)


def handler_drugs_buttons(chat_id, patogen_id, session, bot, message):
    drug_list = get_drug_for_patogen(session, patogen_id)
    if drug_list == []:
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        bot.send_message(
            chat_id,
            "Нет препаратов для данной прививки, попробуйте внести данные чуть позднее",
        )
        menu_my_vaccine(message, bot)
        return
    keyboard = teletypes.InlineKeyboardMarkup()
    for i in drug_list:
        id_drug = i["id"]
        name_drug = i["name"]
        if len(name_drug) > 24:
            name_drug = name_drug[0:22] + "..."
        keyboard.add(
            teletypes.InlineKeyboardButton(
                text=name_drug,
                callback_data="get_drug#" + str(id_drug) + "#" + str(name_drug),
            )
        )
    bot.send_message(chat_id, "Выберите препарат", reply_markup=keyboard)


def handler_drugs_dose_buttons(chat_id, bot, message):
    keyboard = teletypes.InlineKeyboardMarkup()
    drug_list = [1, 2, 3]
    for i in drug_list:
        keyboard.add(
            teletypes.InlineKeyboardButton(
                text=i,
                callback_data="get_drug_dose#" + str(i),
            )
        )
    bot.send_message(chat_id, "Номер дозы", reply_markup=keyboard)


def handler_vaccine_future(message, session, bot):
    handler_baby_buttons(message, session, bot)


def get_future_vac(call, session, bot):
    baby_id = call.data.split("#")[1]
    chat_id = call.data.split("#")[3]
    data = get_children_info(session, baby_id)

    month = date_diff(data["birth_date"])
    vacc_pass_info = get_vacc_pass(session, baby_id)
    is_empty = 1
    first_mess = 1
    for i in range(0, month - 1):
        res = get_plain_vaccine(session, i, vacc_pass_info)
        if res:
            if first_mess:
                first_mess = 0
                mess = "Список пропущенной вакцинации"
                bot.send_message(chat_id, mess)
            is_empty = 0
            mess = prep_str_future_vac(res, i, 1)
            bot.send_message(chat_id, mess)

    if is_empty:
        bot.send_message(chat_id, "На текущий момент вакцинация выполнена полностью")

    is_empty = 1
    first_mess = 1
    for i in range(month, month + 3):
        res = get_plain_vaccine(session, i, vacc_pass_info)
        if res:
            if first_mess:
                first_mess = 0
                mess = "Список предстоящей вакцинации"
                bot.send_message(chat_id, mess)
            is_empty = 0
            mess = prep_str_future_vac(res, i)
            bot.send_message(chat_id, mess)

    if is_empty:
        bot.send_message(chat_id, "Ближайшее время вакцинация не требуется")


def write_vaccine_baby(call, session, bot, vacc_reg_dict):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    msg = call.message.text
    obj_message = call.message

    if back(msg, obj_message, bot, session, vacc_reg_dict, chat_id):
        return

    vacc_reg_dict[chat_id] = {}
    vacc_reg_dict[chat_id]["baby_id"] = call.data.split("#")[1]

    bot.delete_message(chat_id, message_id)
    message = "Ребенок: " + call.data.split("#")[2] + " ✅"
    bot.send_message(chat_id, message)

    handler_patogen_buttons(chat_id, session, bot)
    return


def write_vaccine_patogen(call, session, bot, vacc_reg_dict):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    msg = call.message.text
    obj_message = call.message

    if back(msg, obj_message, bot, session, vacc_reg_dict, chat_id):
        return

    patogen_id = call.data.split("#")[1]
    vacc_reg_dict[chat_id]["patogen_id"] = patogen_id

    bot.delete_message(chat_id, message_id)
    message = "Прививка: " + call.data.split("#")[2] + " ✅"
    bot.send_message(chat_id, message)
    handler_drugs_buttons(chat_id, patogen_id, session, bot, obj_message)

    return


def write_vaccine_drug(call, session, bot, vacc_reg_dict):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    msg = call.message.text
    obj_message = call.message

    if back(msg, obj_message, bot, session, vacc_reg_dict, chat_id):
        return

    drug_id = call.data.split("#")[1]
    vacc_reg_dict[chat_id]["drug_id"] = drug_id

    bot.delete_message(chat_id, message_id)
    message = "Препарат: " + call.data.split("#")[2] + " ✅"
    bot.send_message(chat_id, message)
    handler_drugs_dose_buttons(chat_id, bot, obj_message)

    return


def write_vaccine_drug_dose(call, session, bot, vacc_reg_dict):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    msg = call.message.text
    obj_message = call.message

    if back(msg, obj_message, bot, session, vacc_reg_dict, chat_id):
        return

    dose = call.data.split("#")[1]
    vacc_reg_dict[chat_id]["dose"] = dose

    bot.delete_message(chat_id, message_id)
    message = "Доза № " + dose + " ✅"
    bot.send_message(chat_id, message)
    bot.send_message(chat_id, "Введите дату вакцинации в формате ДД.ММ.ГГГГ")
    bot.register_next_step_handler(
        obj_message, write_vaccine_date, session, bot, vacc_reg_dict
    )

    return


def write_vaccine_date(call, session, bot, vacc_reg_dict):
    chat_id = call.chat.id
    msg = call.text
    obj_message = call

    if back(msg, obj_message, bot, session, vacc_reg_dict, chat_id):
        return
    date = str_to_date(msg)

    if date == "error":
        bot.send_message(
            chat_id,
            "Ошибка при вводе даты. Введите дату вакцинации в формате ДД.ММ.ГГГГ",
        )
        bot.register_next_step_handler(
            obj_message, write_vaccine_date, session, bot, vacc_reg_dict
        )
        return

    vacc_reg_dict[chat_id]["date_medication"] = date
    write_vaccine_to_db(obj_message, bot, session, vacc_reg_dict, chat_id)
    return


def write_vaccine_to_db(message, bot, session, vacc_reg_dict, chat_id):
    baby_info = get_children_info(session, vacc_reg_dict[chat_id].get("baby_id"))
    vacc_reg_dict[chat_id]["baby_age"] = date_diff(
        baby_info["birth_date"], vacc_reg_dict[chat_id]["date_medication"]
    )
    
    write=write_to_bd(session, "Vacc_pass", **vacc_reg_dict[chat_id])
    if write==0:
        bot.send_message(chat_id, "Данные о пройденной вакцинации не записаны")
    else:
        bot.send_message(chat_id, "Данные о пройденной вакцинации успешно записаны")
    try:
        del vacc_reg_dict[chat_id]
        menu_my_vaccine(message, bot)
    except:
          log = Logging(__name__,bot)
          log.error(message, __name__, __file__, " Ошибка при очистке словаря baby_reg_dict")
    return


def back(msg, obj_message, bot, session, vacc_reg_dict, chat_id):
    bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    if msg == "Главное меню":
        start(obj_message, bot, session, 1)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        try:
            del vacc_reg_dict[chat_id]
        except:
            pass
        return 1
    elif msg == "💉 Назад":
        menu_my_vaccine(obj_message, bot)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        try:
            del vacc_reg_dict[chat_id]
        except:
            pass
        return 1
    return 0
