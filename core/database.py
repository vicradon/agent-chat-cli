from simplesqlite import SimpleSQLite
from config.cli_config import config
from core.models import User, Prompts, Conversation

con = SimpleSQLite(config.sqlite_db_name, "a")

def create_tables():
    User.attach(con)
    Prompts.attach(con)
    Conversation.attach(con)
    User.create()
    Prompts.create()
    Conversation.create()