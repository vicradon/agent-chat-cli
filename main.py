import os
import sys
import signal
import dataclasses
from dataclasses import dataclass
from typing import Optional, Literal

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from dotenv import load_dotenv
from simplesqlite import SimpleSQLite
from simplesqlite.model import Integer, Model, Text
from simplesqlite.error import OperationalError

from colorama import Fore, init

init(autoreset=True)

load_dotenv()

gemini_model = os.getenv("GEMINI_MODEL")
gemini_api_key = os.getenv("GEMINI_API_KEY")

model = GoogleModel(
    gemini_model,
    provider=GoogleProvider(api_key=gemini_api_key),
)


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


@dataclass
class RuntimeState:
    login_user: Optional[User] = dataclasses.field(default=None)
    system_prompt: str = dataclasses.field(default="You are simply an AI")
    personality_prompt: str = dataclasses.field(default="")


def sinput(prompt):
    try:
        return input(prompt)
    except EOFError:
        return graceful_exit()


con = SimpleSQLite("database.db", "a")


def create_tables():
    User.attach(con)
    Prompts.attach(con)
    User.create()
    Prompts.create()


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
        print(Fore.GREEN + "You registered successfully!")
        return True
    except OperationalError as e:
        print(Fore.RED + e.message)
        return False
    except Exception as e:
        print(Fore.RED + str(e))
        return False


def ask_question():
    system_prompt = f"""
        {RuntimeState.system_prompt}
        
        Your personality is: {RuntimeState.personality_prompt}
    """

    agent = Agent(
        model,
        system_prompt=system_prompt,
    )

    result = None

    while True:
        user_input = sinput(Fore.CYAN + "ask a question: ")
        message_history = result.all_messages() if result else []
        result = agent.run_sync(user_input, message_history=message_history)
        print(Fore.YELLOW + f"assistant: {result.output}\n")


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

def create_prompt(ptype: Literal["system", "personality"]) -> str:
    while True:
        text = sinput(Fore.CYAN + f"Enter your {ptype} prompt: ").strip()
        if not text:
            print(Fore.RED + "Prompt cannot be empty.")
            continue

        try:
            Prompts.insert(
                Prompts(
                    user_id=RuntimeState.login_user.id,
                    prompt_type=ptype,
                    prompt_text=text,
                )
            )
            con.commit()
            print(Fore.GREEN + f"{ptype.capitalize()} prompt created successfully!")
            return text
        except Exception as e:
            print(Fore.RED + f"Error saving prompt: {e}")
            print(Fore.YELLOW + "Let's try again.")


def choose_prompt(ptype: Literal["system", "personality"]) -> str:
    prompts = list(
        Prompts.select(
            where=f"prompt_type='{ptype}' AND user_id='{RuntimeState.login_user.id}'"
        )
    )
    if not prompts:
        print(Fore.YELLOW + f"No {ptype} prompts found. Let's create one.")
        return create_prompt(ptype)

    print(Fore.MAGENTA + f"\nAvailable {ptype} prompts:")
    for p in prompts:
        print(Fore.CYAN + f"{p.id}. {p.prompt_text}")

    while True:
        choice = sinput(
            Fore.CYAN + f"Choose a {ptype} prompt ID, 0 to create a new one, or -1 to exit this input: "
        ).strip()

        if choice == "0":
            return create_prompt(ptype)
        elif choice == "-1" and ptype == "system":
            return RuntimeState.system_prompt
        elif choice == "-1" and ptype == "personality":
            return RuntimeState.personality_prompt
        
        try:
            choice_id = int(choice)
            selected = next((p for p in prompts if p.id == choice_id), None)
            if selected:
                print(Fore.GREEN + f"Selected {ptype} prompt.")
                return selected.prompt_text
            else:
                print(Fore.RED + "Invalid choice. Try again.")
        except ValueError:
            print(Fore.RED + "Invalid input. Try again.")


def system_prompt_flow():
    RuntimeState.system_prompt = choose_prompt("system")


def personality_prompt_flow():
    RuntimeState.personality_prompt = choose_prompt("personality")


def create_prompt_flow():
    type_map = {
        "1": lambda: create_prompt("system"),
        "sys": lambda: create_prompt("system"),
        "system": lambda: create_prompt("system"),
        "2": lambda: create_prompt("personality"),
        "personality": lambda: create_prompt("personality"),
        "person": lambda: create_prompt("personality"),
    }
    while True:
        choice = sinput(
            Fore.MAGENTA + "Create:\n" +
            Fore.GREEN + "1. System prompt\n" +
            Fore.YELLOW + "2. Personality prompt\n" +
            Fore.WHITE + "Choice: "
        ).strip()

        if choice not in type_map:
            print(Fore.RED + "Invalid choice.")
            continue

        result = type_map[choice]()

        if not result:
            break

        if choice in {"1", "sys", "system"}:
            RuntimeState.system_prompt = result

            follow_up = sinput(
                Fore.CYAN + "Would you like to create a personality prompt as well? (Y/n): "
            ).strip().lower()

            if follow_up != "n":
                result = create_prompt("personality")
                RuntimeState.personality_prompt = result

        elif choice in {"person", "personality", "2"}:
            RuntimeState.personality_prompt = result

        break


def existing_prompt_flow():
    system_prompt_flow()
    personality_prompt_flow()
    print(Fore.GREEN + "Prompts loaded successfully.")
    ask_question()


def decide_on_prompts():
    intent_map = {
        "1": create_prompt_flow,
        "new": create_prompt_flow,
        "2": existing_prompt_flow,
        "existing": existing_prompt_flow,
        "3": ask_question,
    }

    while True:
        intent = sinput(
            Fore.MAGENTA + "Would you like to:\n" +
            Fore.GREEN + "1. Create a new prompt\n" +
            Fore.YELLOW + "2. Start a conversation with an existing prompt\n" + 
            Fore.MAGENTA + "3. Simply start a conversation\n" + 
            Fore.WHITE + "Choice: "
        ).strip()

        if intent in intent_map:
            intent_map[intent]()
            break
        print(Fore.RED + "Unknown choice, please try again.")


def main():
    welcome_user()
    decide_on_prompts()
    ask_question()


def graceful_exit(*_):
    print("\ngoodbye...")
    sys.exit(0)


signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

if __name__ == "__main__":
    create_tables()
    main()
