from colorama import Fore
from simplesqlite.error import OperationalError

from core.input import sinput
from core.models import User
from core.state import RuntimeState
from core.database import con
from core.prompt import ask_question


def execute_login() -> bool:
    username_input = sinput(Fore.CYAN + "Enter your username: ")
    password_input = sinput(Fore.CYAN + "Enter your password: ")

    try:
        user = User.select(where=f"username='{username_input}'")
        if not user:
            print(Fore.RED + "Invalid username or password.")
            return False

        stored_user: User = next(user)
        if password_input == stored_user.password:
            print(Fore.GREEN + f"Welcome back, {username_input}!\n")
            RuntimeState.login_user = stored_user
            return True
        else:
            print(Fore.RED + "Invalid username or password.")
            return False
    except Exception as e:
        print(Fore.RED + f"Login error: {str(e)}")
        return False


def execute_registration() -> bool:
    username_input = sinput(Fore.CYAN + "choose a username: ")
    password_input = sinput(Fore.CYAN + "choose a password: ")

    new_user = User(username=username_input, password=password_input)

    try:
        User.insert(new_user)
        con.commit()

        created_user = next(User.select(where=f"username='{username_input}'"))

        RuntimeState.login_user = created_user
        print(Fore.GREEN + "You registered successfully!")
        return True
    except OperationalError as e:
        print(Fore.RED + e.message)
        return False
    except Exception as e:
        print(Fore.RED + str(e))
        return False


def welcome_user():
    intent_to_action_map = {
        "1": execute_registration,
        "register": execute_registration,
        "login": execute_login,
        "2": execute_login,
        "question": ask_question,
        "ask": ask_question,
        "ask a question": ask_question,
        "simply ask a question": ask_question,
        "3": ask_question,
    }

    while True:
        intent = sinput(
            Fore.LIGHTMAGENTA_EX + "What do you wish to do?\n" +
            Fore.GREEN + "1. Register\n" +
            Fore.YELLOW + "2. Login\n" +
            Fore.CYAN + "3. Simply ask a question\n" +
            Fore.WHITE + "Choose: "
        )
        
        intent = intent.lower()

        if intent not in intent_to_action_map:
            print(Fore.RED + "Unknown intent, please try again.")
        else:
            is_success = intent_to_action_map[intent]()
            if is_success:
                break

