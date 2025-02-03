from bot.utils import start, draw_buttons, menu_risk
from dbase.library import (
    date_to_str,
    get_question_by_id,
    get_image_by_id,
    get_last_risk_result,
    user_exist,
    write_to_bd,
)
from log import Logging
from telebot import types as teletypes
import datetime


def start_check_risk(message, id_question, bot, user_dict, session):
    chat_id = message.chat.id
    user_dict[chat_id] = {}
    user_dict[chat_id]["user_id"] = chat_id
    user_dict[chat_id]["name"] = message.chat.username
    user_dict[chat_id]["points_szrp"] = 0
    user_dict[chat_id]["points_pre"] = 0
    buttons = [["Главное меню", "💊 Назад"]]
    draw_buttons(
        bot,
        message,
        buttons,
        "row",
        "Тест на риски преэклампсии (ПЭ) и синдрома замедления роста плода (СЗРП)",
    )

    question = get_question_by_id(session, id_question)
    if question:
        res = send_question(message, user_dict, question, session, bot)
        return res
    log = Logging(__name__,bot)
    log.info(message, __name__, __file__, f" Нет вопроса с id {id_question}")
    return 0


def handler_question(call, user_dict, bot, session):

    try:
        message = call.message
    except:
        message = call

    chat_id = message.chat.id
    message_id = message.message_id
    msg = message.text
    if msg == "Главное меню":
        start(message, bot, session, 1)
        return

    if not user_dict.get(chat_id):
        bot.send_message(
            chat_id,
            "Проводились технические работы на сервере, пожалуйста начните тест заново",
        )
        return "stop"

    point_szrp = int(call.data.split("#")[1])
    point_pre_eclamp = int(call.data.split("#")[2])
    answer_text = call.data.split("#")[4]
    user_dict[chat_id]["points_szrp"] += point_szrp
    user_dict[chat_id]["points_pre"] += point_pre_eclamp
    next_id = call.data.split("#")[3]
    if next_id == "None":
        final_testing(session, bot, user_dict[chat_id])
        return

    next_id = int(next_id)

    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message.text + "✅ " + "\nответ: " + answer_text,
        )
    except:
        pass

    question = get_question_by_id(session, next_id)
    if question:
        send_question(message, user_dict, question, session, bot)
        return
    return


def send_question(message, user_dict, questObj, session, bot):
    chat_id = message.chat.id
    msg = message.text
    if msg == "Главное меню":
        try:
            del user_dict[chat_id]
        except:
            pass
        start(message, bot, session, 1)
        return
    elif msg == "💊 Назад":
        try:
            del user_dict[chat_id]
        except:
            pass
        menu_risk(message, bot)
        return
    questText = questObj["text"]
    questType = questObj["type"]
    questAnswers = questObj["answers"]
    picture_id = questObj.get("picture")

    if questType == "button":
        if picture_id != None:
            image_dict = get_image_by_id(session, picture_id)
            bot.send_photo(chat_id, image_dict["picture"])
        keyboard = teletypes.InlineKeyboardMarkup()
        buttons = ()
        for answer in questAnswers:
            text = answer["text"]
            pointsSZRP = answer["points_szrp"]
            pointsPreEc = answer["points_pre"]
            next_id = answer["next_question_id"]
            buttons += (
                teletypes.InlineKeyboardButton(
                    text=text,
                    callback_data="preg_test#"
                    + str(pointsSZRP)
                    + "#"
                    + str(pointsPreEc)
                    + "#"
                    + str(next_id)
                    + "#"
                    + str(text),
                ),
            )
        keyboard.add(*buttons)
        bot.send_message(chat_id, questText, reply_markup=keyboard)

    elif questType == "height" or questType == "weight":
        bot.send_message(chat_id, questText)
        next_id = questObj["next_question_id"]
        bot.register_next_step_handler(
            message, add_height_or_weight, user_dict, next_id, questType, session, bot
        )


def add_height_or_weight(message, user_dict, next_id, types, session, bot):
    chat_id = message.chat.id
    user_dict[chat_id][types] = message.text.replace(",", ".")
    question = get_question_by_id(session, next_id)
    if question:
        send_question(message, user_dict, question, session, bot)


def check_risk(user_dict):
    height = user_dict["height"]
    weight = user_dict["weight"]
    imt = imt_create(height, weight)
    user_dict["imt"] = imt
    user_dict["result"] = 0
    if imt < 19.8:
        user_dict["points_szrp"] += 2
    elif 19.8 <= imt < 30:
        pass
    elif imt >= 30:
        user_dict["points_szrp"] += 2
        user_dict["points_pre"] += 1

    user_dict["result_szrp"] = get_results_testing_szrp(
        user_dict, user_dict["points_szrp"]
    )
    user_dict["result_pre"] = get_results_testing_pre_eclamp(
        user_dict, user_dict["points_pre"]
    )
    return 1


def imt_create(height, weight):
    try:
        return round(float(weight) / ((float(height) / 100) ** 2), 2)
    except:
        return 0


def get_results_testing_szrp(user_dict, summ_points_szrp):
    if summ_points_szrp >= 5:
        user_dict["result"] = 1
        result = (
            "Риск СЗРП высокий. Набрано "
            + str(summ_points_szrp)
            + " баллов."
            + " Рекомендовано проведение ультразвукового исследования совместно с"
            + " допплерометрией маточно-плацентарного и фето-плацентарного кровотоков"
            + " во втором (при сроке беременности 19-20+6 недель) и в третьем"
            + " (при сроке беременности 30-34 недели) триместрах беременности."
        )
    else:
        result = "Риск СЗРП низкий. Набрано " + str(summ_points_szrp) + " баллов"
    return result


def get_results_testing_pre_eclamp(user_dict, summ_points_pre_eclamp):
    if summ_points_pre_eclamp >= 2:
        user_dict["result"] = 1
        result = (
            "Риск преэклампсии высокий. Набрано "
            + str(summ_points_pre_eclamp)
            + " баллов."
            + "Рекомендована профилактика ацетилсалициловой кислотой в сроки 12 - 36 недель беременности."
        )
    else:
        result = (
            "Риск преэклампсии низкий. Набрано "
            + str(summ_points_pre_eclamp)
            + " баллов"
        )
    return result


def write_user_result(session, user_dict):
    chat_id = user_dict["user_id"]
    dict_result = {}
    dict_result["result"] = user_dict["result"]
    dict_result["result_szrp"] = user_dict["result_szrp"]
    dict_result["result_pre"] = user_dict["result_pre"]
    dict_result["date"] = datetime.date.today()
    dict_result["user_id"] = chat_id

    dict_user_params = {}
    dict_user_params["weight"] = user_dict["weight"]
    dict_user_params["height"] = user_dict["height"]
    dict_user_params["imt"] = user_dict["imt"]
    dict_user_params["user_id"] = chat_id

    if not user_exist(session, chat_id):
        create_user = {}
        create_user["chat_id"] = chat_id
        create_user["name"] = user_dict["name"]

        write=write_to_bd(session, "User", **create_user)


    write=write_to_bd(session, "Risk_result", **dict_result)
    write=write_to_bd(session, "User_params", **dict_user_params)


def final_testing(session, bot, user_dict):
    chat_id = user_dict["user_id"]
    check_risk(user_dict)
    write_user_result(session, user_dict)
    mess = "Результаты тестирования:\n" + prepare_result_message(user_dict)

    bot.send_message(chat_id, mess)
    try:
        del user_dict
    except:
        pass


def prepare_result_message(dict_result):
    mess = (
        "ИМТ = "
        + str(dict_result["imt"])
        + "\n"
        + "\n"
        + dict_result["result_szrp"]
        + "\n"
        + "\n"
        + dict_result["result_pre"]
    )
    if dict_result["result"] == 1:
        mess = (
            mess
            + "\n"
            + "\n"
            + "Рекомендовано обратиться к лечащему врачу для перерасчета рисков и корреции назначения."
        )
    mess = (
        mess
        + "\n"
        + "\n"
        + "При возникновении вопросов - можно записаться на онлайн консультацию, подробнее тут: https://t.me/iseeastrongwoman/5"
    )
    return mess


def get_last_result(message, session, bot):
    chat_id = message.chat.id
    last_result = get_last_risk_result(session, chat_id)

    if last_result == {}:
        mess = "Нет ранее пройденных тестов"
        log = Logging(__name__,bot)
        log.error(message, __name__, __file__, " "+mess)
        
    else:
        mess_result = prepare_result_message(last_result)
        mess = (
            "Результат тестирования от "
            + date_to_str(last_result["date"])
            + "\n"
            + "\n"
            + mess_result
        )

    bot.send_message(chat_id, mess)
