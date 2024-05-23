import json
from enum import Enum


class ConfigFile:
    CONFIG_TYPE = dict[str, list[str] | list[list[int] | str]]

    class Keys(Enum):
        users = "пользователь"
        alternatives = "альтернатива"
        relations = "отношение"
        wish = "предпочтение"
        main_character = "от лица"

    def __init__(self, config_path: str, direct_task: bool):
        self.direct_task = direct_task
        self.data = self.__init_json_dict(config_path)
        self.config_path = config_path

    def __init_json_dict(self, config_path: str) -> CONFIG_TYPE:
        result = {}
        try:
            with open(file=config_path, mode="r", encoding="UTF-8") as jf:
                result = dict(json.load(jf))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            with open(file=config_path, mode="w", encoding="UTF-8") as jf:
                json.dump(result, jf)
        return result

    def __write_data(self):
        with open(file=self.config_path, mode="w", encoding="UTF-8") as jf:
            json.dump(self.data, jf, ensure_ascii=False)

    @property
    def main_character(self) -> str:
        if (self.Keys.main_character.name in self.data) and (type(self.data[self.Keys.main_character.name]) == str):
            return self.data[self.Keys.main_character.name]
        return self.__write_main_character()

    @property
    def user_names(self) -> list[str]:
        return self.__get_unic_list(self.Keys.users)

    @property
    def alternatives(self) -> list[str]:
        return self.__get_unic_list(self.Keys.alternatives) + ['']

    def __get_unic_list(self, section: Keys) -> list[str]:
        if (section.name in self.data) and (type(self.data[section.name]) == list) and (len(self.data[section.name]) == len(set(self.data[section.name]))):
            return self.data[section.name].copy()
        written = self.__write_list(section)
        if len(written) != len(set(written)):
            raise UserWarning(f"list of '{section}' not unic!")
        return written.copy()

    def __write_list(self, section: Keys) -> list[str]:
        self.data[section.name] = []
        to_stop = "quit"
        print(f"\nВ файле инициализации не верно указан раздел '{section.name}' (должен быть массив, содержащий '{section.value}')")
        print(f"Давайте попробуем заполнить заново (чтоб прекратить, введите '{to_stop}')")
        while to_stop not in self.data[section.name]:
            self.data[section.name].append(
                input(f" >>> Введите '{section.value}_{len(self.data[section.name])+1}': ").strip()
            )
        while to_stop in self.data[section.name]:
            self.data[section.name].remove(to_stop)

        self.__write_data()
        return self.data[section.name]

    def __write_main_character(self) -> str:
        description = f"{self.Keys.main_character.value} которого вводятся данные" if self.direct_task else "на лицо которое вы хотите повлиять"
        print(f"\nВ файле инициализации не верно указан раздел '{self.Keys.main_character.name}' (должна быть строчка {description}, на выбор {self.user_names})")
        while True:
            self.data[self.Keys.main_character.name] = input(" >>> Введите лицо: ").strip()
            if self.data[self.Keys.main_character.name] in self.user_names:
                self.__write_data()
                return self.data[self.Keys.main_character.name]
            print(f" ! {self.Keys.main_character.name} должно быть из раздела '{self.Keys.users.name}' -> {self.user_names}")

    def get_wishes(self) -> list[str]:
        alternatives = self.alternatives
        users_len = len(self.user_names)
        try:
            if (self.Keys.wish.name in self.data) and (len(self.data[self.Keys.wish.name]) == users_len):
                for wish in self.data[self.Keys.wish.name]:
                    if wish not in alternatives:
                        raise ValueError
                return self.data[self.Keys.wish.name]
            raise ValueError
        except (TypeError, ValueError):
            return self.__write_wishes()

    def __write_wishes(self) -> list[str]:
        main_character = self.main_character
        users = self.user_names
        users_len = len(users)
        alternatives = self.alternatives
        self.data[self.Keys.wish.name] = []
        print(f"\nВ файле инициализации не верно указан раздел '{self.Keys.wish.name}' (должен быть массив размером {users_len}, содержащий значения из {alternatives})")

        for user in users:
            if user == main_character:
                self.data[self.Keys.wish.name].append('')
                continue
            response = None
            while response is None:
                try:
                    response = input(f" >>> Введите {self.Keys.wish.value} для '{user}': ").strip()
                    if response not in alternatives:
                        response = None
                        raise ValueError
                except ValueError:
                    print(f" ! {self.Keys.wish.value} должно быть из раздела '{self.Keys.alternatives.name}' -> {alternatives}")
            self.data[self.Keys.wish.name].append(response)

        self.__write_data()
        return self.data[self.Keys.wish.name]

    def get_relations(self) -> list[list[int]]:
        users_len = len(self.user_names)
        try:
            if (self.Keys.relations.name in self.data) and (len(self.data[self.Keys.relations.name]) == users_len):
                for arr in self.data[self.Keys.relations.name]:
                    arr = list(arr)
                    arr.sort()
                    if len(arr) != users_len or (arr[-1] != 1 and arr[-1] != 0):
                        raise ValueError
                return self.data[self.Keys.relations.name]
            raise ValueError
        except (TypeError, ValueError):
            return self.__write_relations()

    def __write_relations(self) -> list[list[int]]:
        users = self.user_names
        users_len = len(users)
        temp_result = [[None for _ in range(users_len)] for _ in range(users_len)]
        print(f"\nВ файле инициализации не верно указан раздел '{self.Keys.relations.name}' (должен быть двумерный массив размером {users_len}x{users_len}, содержащий '1 - 'союз' или 0 - 'конфликт'')")

        for id1, user1 in enumerate(users):
            for id2, user2 in enumerate(users):
                if user1 == user2:
                    temp_result[id1][id2] = 1
                if temp_result[id2][id1] is not None:
                    temp_result[id1][id2] = temp_result[id2][id1]
                    continue
                response = None
                while response is None:
                    try:
                        response = int(input(f" >>> Введите {self.Keys.relations.value} '{user1}-{user2}': "))
                        if response not in [1, 0]:
                            response = None
                            raise ValueError
                    except ValueError:
                        print(f" ! {self.Keys.relations.value} должно быть целочисленным (1 - 'союз'; 0 - 'конфликт')")
                temp_result[id1][id2] = response

        self.data[self.Keys.relations.name] = temp_result
        self.__write_data()
        return self.data[self.Keys.relations.name]

    def __del__(self):
        try:
            self.__write_data()
        except NameError:
            pass
