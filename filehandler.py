import json
import os

from telebot.types import User


class FileHandler:
    __usersFile = "users.json"

    @classmethod
    def write_json(cls, data, need_update: bool, filename=__usersFile):
        if need_update:
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
        need_update = True
        if self.file_exist(self.__usersFile):
            data = self.get_json_data()
            data[user.id] = user_data
            if str(user.id) in data.keys():
                need_update = False

            self.write_json(data, need_update)
        else:
            user_dict[user.id] = user_data
            self.write_json(user_dict, need_update)

    def save_location(self, user_id: int, location: str):
        if self.file_exist(self.__usersFile):
            with open(self.__usersFile, encoding='utf-8') as json_file:
                data = json.load(json_file)
                data[str(user_id)]['location'] = location

            self.write_json(data, True)

    @classmethod
    def file_exist(cls, file_path):
        return os.path.isfile(file_path) and os.access(file_path, os.R_OK)

    @classmethod
    def get_json_data(cls, json_file=__usersFile):
        with open(json_file, encoding='utf-8') as json_file:
            return json.load(json_file)

    def get_users(self):
        if self.file_exist(self.__usersFile):
            with open(self.__usersFile, encoding='utf-8') as json_file:
                data = json.load(json_file)

                return list(data.keys())
        return []
