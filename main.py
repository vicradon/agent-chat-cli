import signal

from colorama import init

from core.welcome import welcome_user
from core.cleanup import graceful_exit
from core.database import create_tables
from core.prompt import decide_on_prompts, ask_question

init(autoreset=True)

def main():
    welcome_user()
    decide_on_prompts()
    ask_question()

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

if __name__ == "__main__":
    create_tables()
    main()
