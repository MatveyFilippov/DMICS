class User:
    def __init__(self, user_id: int, username: str, choice: str, relations: list[int]):
        self.user_id = user_id
        self.username = username
        self.choice = {choice}
        self.relations = {}
        for another_user_id, relation in enumerate(relations):
            if self.user_id == another_user_id:
                continue
            self.__set_relation(another_user_id, relation)
        self.var = None

    def __set_relation(self, user_id: int, relation: int):
        if user_id == self.user_id:
            raise KeyError("Impossible to set relation with itself")
        if relation not in [0, 1]:
            raise ValueError("Relation must be [0, 1]")
        self.relations[user_id] = relation

    def set_var(self, var):
        self.var = var


class Society:
    def __init__(self, users: list[str], alternatives: list[str], choices: list[str], relations: list[list[int]]):
        self.users = []
        self.alternatives = set(alternatives) - {''}
        for i, username in enumerate(users):
            self.users.append(User(user_id=i, username=username, choice=choices[i], relations=relations[i]))
        self.relation_table = relations

    def get_user(self, user_id: int | None = None, username: str | None = None) -> User:
        if user_id is not None:
            return self.users[user_id]
        if username is not None:
            for user in self.users:
                if user.username == username:
                    return user
            raise KeyError(f"User with username '{username}' not exists")
