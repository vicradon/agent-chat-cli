from simplesqlite.model import Integer, Model, Text, Blob

class User(Model):
    id = Integer(primary_key=True)
    username = Text(not_null=True, unique=True)
    password = Text(not_null=True)


class Prompts(Model):
    id = Integer(primary_key=True)
    user_id = Integer(not_null=True)
    prompt_type = Text(not_null=True)
    prompt_text = Text(not_null=True)

    __constraints__ = [
        "FOREIGN KEY(user_id) REFERENCES User(id)",
        "CHECK(prompt_type IN ('system', 'personality'))",
    ]

class Conversation(Model):
    id = Integer(primary_key=True)
    user_id = Integer(not_null=True)
    title = Text()
    content = Blob()

    __constraints__ = [
        "FOREIGN KEY(user_id) REFERENCES User(id)"
    ]