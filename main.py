import os.path
from config_file import ConfigFile
from society import Society, User
from prototype_math import SymbolMath


DIRECT_DESCRIBE = """Прямая задача предполагает внесение информации об индивидах, альтернативах, отношениях в группе
Основная цель задачи определить выбор индивида, чье решение является целевым.
Отличительной особенностью является то, что в заданном Мире целевой индивид не делал выбор в пользу альтернативы."""
NOT_DIRECT_DESCRIBE = """Обратная задача предполагает внесение информации об индивидах, альтернативах, отношениях в группе
Основная цель задачи определить варианты влияний целевого индивида на группу для достижения его желаемого исхода.
Отличительно особенностью является то, что программа приводит реальный исход к желаемому."""
DIRECT_NOT_CALC = """{} находится в состоянии фрустрации и не может принять решение"""
NOT_DIRECT_NOT_CALC = """В заданных условиях нет вариантов влияний на индивида '{}', в которых реальный исход будет равен желаемому"""


def __inputer(prompt: str) -> str:
    print(prompt)
    return input(" >>> ").strip()


def get_choice_about_task_direction() -> str:
    return __inputer("Выберите тип задачи ('1' - прямая; '2' - обратная; прочее - выйти)")


def get_json_file() -> str:
    print()
    json_path = __inputer("Введите имя json файла (или путь до него) с конфигурацией\nЕсли такого нет, придумайте новое название")
    while json_path.replace(".json", "") == "":
        json_path = __inputer("Введите заново имя файла")
    if not json_path.endswith(".json"):
        json_path += ".json"
    if not os.path.exists(json_path):
        if json_path.count("/"):
            json_name = json_path.split("/")[-1]
        elif json_path.count("\\"):
            json_name = json_path.split("\\")[-1]
        else:
            json_name = json_path
        try:
            path_without_name = json_path.replace(json_name, "")
            if path_without_name != "":
                os.makedirs(path_without_name, exist_ok=True)
            with open(json_path, "w") as jf:
                jf.write("here will be config data...")
        except (FileNotFoundError, IsADirectoryError):
            print("Такого файла нет и я не могу его создать (возможно неверное указан путь)")
            json_path = get_json_file()
    return json_path


def print_relationship_graph(users: list[User]):
    user_score = len(users)
    print("'*' - отношение конфликта; '---' - отношение союза\n")
    if user_score == 2:
        a1 = str(users[0].var)
        a2 = str(users[1].var)
        a1_a2 = "---" if users[0].relations[1] == 1 else " * "
        print(a1, a1_a2 * 4, a2)
    elif user_score == 3:
        a1 = str(users[0].var)
        a2 = str(users[1].var)
        a3 = str(users[2].var)
        a1_a2 = "/" if users[0].relations[1] == 1 else "*"
        a1_a3 = "\\" if users[0].relations[2] == 1 else "*"
        a2_a3 = "---" if users[1].relations[2] == 1 else " * "
        high = 5
        for i in range(high):
            if i == 0:
                print("  " + " " * (high - i) + a1)
            print("  " + " " * (high - i) + a1_a2 + "  " * i + a1_a3)
            if i == 4:
                print(f" {a2} " + a2_a3 * (i - 1) + f" {a3}")
    else:
        raise TypeError("Prototype can create polynomial for no more that 3 users")
    print()


direct_choice = get_choice_about_task_direction()
while direct_choice in ["1", "2"]:
    direct_task = direct_choice == "1"
    print(DIRECT_DESCRIBE if direct_task else NOT_DIRECT_DESCRIBE)
    input("press ENTER to continue...")

    init_data = ConfigFile(get_json_file(), direct_task=direct_task)
    if len(init_data.user_names) > 3:  # TODO: улучшить до большего числа
        print("Упс, в настоящей момент наш прототип не может считать отношения, в которых находятся больше трёх персон")
        print("Ваш файл с конфигурацией сохранён, возвращайтесь с ним позже)")
        direct_choice = get_choice_about_task_direction()
        continue

    actual_society = Society(
        users=init_data.user_names, alternatives=init_data.alternatives,
        choices=init_data.get_wishes(), relations=init_data.get_relations()
    )
    symbol_math = SymbolMath(actual_society.users.copy())
    main_user = actual_society.get_user(username=init_data.main_character)

    print()
    print_relationship_graph(actual_society.users)
    print(f"Полином для текущего вида отношений: {symbol_math.get_polynomial()}")
    print(f"Решение для уравнения ", end="")
    left, right = symbol_math.get_eq(main_user).args
    print("'", left, " = ", str(right).replace("|", "+").replace(" & ", ""), "':", sep="")
    try:
        A, B = symbol_math.solve_eq(
            main_user=main_user, alternatives=actual_society.alternatives
        )
        print(f"(A = {A}) >= {main_user.username} >= (B = {B})")
    except ArithmeticError:
        print(DIRECT_NOT_CALC.format(main_user.username) if direct_task else NOT_DIRECT_NOT_CALC.format(main_user.username))
    print()

    direct_choice = get_choice_about_task_direction()

print("До следующего свидания!")
