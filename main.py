import os
import telebot
from bot.menu_guid_vaccine import (
    get_all_vaccination_info,
    get_drug_info,
    get_infection_info,
    get_info_by_period,
    list_vac_next,
    send_drug_info,
    send_infection_info,
    send_info_first,
)
from bot.utils import (
    get_session,
    menu_guid_vaccine,
    menu_my_vaccine,
    menu_risk,
    start,
)
from bot.menu_my_vaccine import (
    baby_registration,
    get_future_vac,
    handler_baby_buttons,
    handler_baby_vaccine_info,
    handler_vaccine_future,
    handler_vaccine_registration,
    write_user,
    write_vaccine_baby,
    write_vaccine_drug,
    write_vaccine_drug_dose,
    write_vaccine_patogen,
)
from bot.menu_risk import get_last_result, handler_question, start_check_risk
from log import Logging
from dbase.library import fix_all_pics

token = ""
bot = telebot.TeleBot(token)


# метод обработчик команды start, вызывает отрисовку кнопок главного меню
@bot.message_handler(commands=["start"])
def router_message(message):
    start(message, bot, session)


# метод обработчик текстовых сообщений
@bot.message_handler(content_types=["text"])
def router_message(message):
    text = message.text
    log = Logging(__name__, bot)
    log.info(message, __name__, __file__, " " + text)
    write_user(message, session)
    # возврат в главное меню
    if "Главное меню" in text:
        start(message, bot, session, 1)
        return

    # возврат в предыдущее меню
    if text == "💊 Назад":
        menu_risk(message, bot)
        return
    elif text == "💉 Назад":
        menu_my_vaccine(message, bot)
        return
    elif text == "📖 Назад":
        menu_guid_vaccine(message, bot)
        return
    elif text == "фикс_картинок":
        fix_all_pics(session, bot)
    # обработка нажатия кнопок меню
    if "Риски ПЭ/СЗРП" in text:
        menu_risk(message, bot)
    elif "Оценить риски в текущую беременность" in text:
        start_check_risk(message, 1, bot, user_dict, session)
    elif "Показать предыдущий результат" in text:
        get_last_result(message, session, bot)
    elif "Справочник" in text:
        menu_guid_vaccine(message, bot)
    elif "Моя вакцинация" in text:
        menu_my_vaccine(message, bot)
    elif "Общий график вакцинации" in text:
        get_all_vaccination_info(message, bot, session)
    elif "Список прививок за месяц" in text:
        get_info_by_period(message, session, bot)
    elif "Инфекции" in text:
        get_infection_info(message, session, bot)
    elif "Препараты" in text:
        get_drug_info(message, session, bot)
    elif "Регистрация ребенка" in text:
        baby_registration(message, session, bot, baby_reg_dict)
    elif "Сертификат прививок" in text:
        handler_baby_buttons(message, session, bot)
    elif "Добавить вакцинацию" in text:
        handler_vaccine_registration(message, session, bot, vacc_reg_dict)
    elif "План вакцинации" in text:
        handler_vaccine_future(message, session, bot)


# метод обработчик нажатий на инлайн кнопки
@bot.callback_query_handler(func=lambda call: (call.data != ""))
def router_call(message):
    text = message.data
    call_name = text.split("#")[0]

    log = Logging(__name__, bot)
    log.info(message, __name__, __file__, " " + text)

    # возврат в главное меню
    if text == "Главное меню":
        start(message, bot, session, 1)

    # обработка кнопок.
    if call_name == "preg_test":
        # обработчик ответов на вопросы о рисках ПЭ и СЗРП
        handler_question(message, user_dict, bot, session)
    elif call_name == "get_baby":
        # обработчик выбранного ребенка для получения списка вакцинации
        handler_baby_vaccine_info(message, session, bot)
    elif call_name == "get_vac":
        # обработчик выбранного ребенка для записи пройденной вакцинации
        write_vaccine_baby(message, session, bot, vacc_reg_dict)
    elif call_name == "get_pat":
        # обработчик выбранного патогена для записи пройденной вакцинации
        write_vaccine_patogen(message, session, bot, vacc_reg_dict)
    elif call_name == "get_drug":
        # обработчик выбранного препарата для записи пройденной вакцинации
        write_vaccine_drug(message, session, bot, vacc_reg_dict)
    elif call_name == "get_drug_dose":
        # обработчик выбранной дозы препарата  для записи пройденной вакцинации
        write_vaccine_drug_dose(message, session, bot, vacc_reg_dict)
    elif call_name == "get_future":
        # обработчик выбранного ребенка для получения списка пропущенной и предстоящей вакинации
        get_future_vac(message, session, bot)
    elif call_name == "pat_info_first":
        # обработчик, вызывающий отрисовку кнопко с буквами патогенов
        send_info_first(message, session, bot, "patogen")
    elif call_name == "drug_info_first":
        # обработчик, вызывающий отрисовку кнопко с буквами препаратов
        send_info_first(message, session, bot, "drug")
    elif call_name == "pat_info":
        # обработчик, вызывающий вывод информации по выбранному патогену
        send_infection_info(message, session, bot)
    elif call_name == "drug_info":
        # обработчик, вызывающий вывод информации по выбранному препарату
        send_drug_info(message, session, bot)
    elif call_name == "list_vac_next":
        # обработчик кнопок да/нет после вывода информации о вакцинации за месяц
        list_vac_next(message, session, bot)


if __name__ == "__main__":
    # path = ".." + os.path.sep + "data"
    path = ""
    db_file = "database.db"
    file_name = os.path.join(path, db_file)

    session = get_session(str(file_name))
    user_dict = {}
    baby_reg_dict = {}
    vacc_reg_dict = {}
    print("Бот запущен!")

    bot.delete_webhook()
    bot.infinity_polling()
