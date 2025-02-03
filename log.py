import logging
import logging.handlers
import os


class Logging:
    def __init__(self, name, bot):
        self.bot = bot
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.addHandler(self.get_file_handler())

    def get_file_handler(self):
        fmtstr = "[%(asctime)s] [%(levelname)s] => %(message)s"
        fmtdate = "%Y-%m-%d %H:%M:%S"
        # path = ".."+os.path.sep+"data"
        path = ""
        db_file = "log.log"
        file_name = os.path.join(path, db_file)

        file_handler = logging.handlers.RotatingFileHandler(
            file_name, maxBytes=1048576, backupCount=4, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        # file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(logging.Formatter(fmtstr, fmtdate))
        return file_handler

    # def get_logger(self, name):
    #     self.logger = logging.getLogger(name)
    #     self.logger.setLevel(logging.INFO)
    #     self.logger.addHandler(self.get_file_handler())
    #     return self.logger

    def get_chat_id(self, message):
        try:
            message = message.message
            chat_id = message.chat.id
            name = self.get_user_name(message)
            return str(chat_id) + " user: @" + name
        except:
            try:
                message = message
                chat_id = message.chat.id
                name = self.get_user_name(message)
                return str(chat_id) + " user: @" + name
            except:
                try:
                    return str(message)
                except:
                    return ""

    def get_user_name(self, message):
        name = getattr(message.chat, "username")

        if name == None:
            name = "first_name " + str(getattr(message.chat, "first_name"))
            name += " last_name " + str(getattr(message.chat, "last_name"))
        return str(name)

    def get_file_name(self, file):
        file = file.replace("\\", "/")
        file = file.split("/")[len(file.split("/")) - 1]
        return file

    def get_message(self, message, name, file, text):
        file = self.get_file_name(file)
        chat_id = self.get_chat_id(message)
        return (
            "file: "
            + file
            + " func: "
            + name
            + " chat_id: "
            + chat_id
            + " text: "
            + text
        )

    def get_message_library(self, model_name, name, file, text):
        file = self.get_file_name(file)
        return (
            "file: "
            + file
            + " func: "
            + name
            + " Model: "
            + model_name
            + " text: "
            + text
        )

    def send_message_tg_group(self, text):
        self.bot.send_message("-4546417606", text)
        return

    def info(self, message, name, file, text):
        message = self.get_message(message, name, file, text)
        self.logger.info(message)
        self.send_message_tg_group(message)
        del self

    def error(self, message, name, file, text):
        message = self.get_message(message, name, file, text)
        self.logger.error(message)
        self.send_message_tg_group(message)
        del self

    def error_library(self, model_name, name, file, text):
        message = self.get_message_library(model_name, name, file, text)
        self.logger.error(message)
        self.send_message_tg_group(message)
        del self
