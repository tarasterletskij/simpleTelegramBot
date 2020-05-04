import json
import os

from telebot.types import User


class FileHandler:
    __usersFile = "users.json"

    @classmethod
    def write_json(cls, data, is_new_user: bool, filename=__usersFile):
        if is_new_user:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False)

    def save_user(self, user: User, chat_id: int):
        user_dict = {}
        user_data = {
            'id': user.id,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'chatId': chat_id
        }
        is_new_user = True
        if os.path.isfile(self.__usersFile) and os.access(self.__usersFile, os.R_OK):
            with open(self.__usersFile, encoding='utf-8') as json_file:
                data = json.load(json_file)
                data[user.id] = user_data
                if str(user.id) in data.keys():
                    is_new_user = False

            self.write_json(data, is_new_user)
        else:
            user_dict[user.id] = user_data
            self.write_json(user_dict, is_new_user)
