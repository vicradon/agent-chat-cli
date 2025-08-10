from typing import Literal
from colorama import Fore
from pydantic_ai import Agent

from core.ai_models import general_model
from core.models import Prompts
from core.input import prompt_inputs_to_input, sinput
from core.state import RuntimeState
from core.database import con
from core.interfaces import PromptInput


def ask_question():
    system_prompt = f"""
        {RuntimeState.system_prompt}
        
        Your personality is: {RuntimeState.personality_prompt}
    """

    agent = Agent(
        general_model,
        system_prompt=system_prompt,
    )

    result = None

    while True:
        user_input = sinput(Fore.CYAN + "ask a question: ")
        message_history = result.all_messages() if result else []
        result = agent.run_sync(user_input, message_history=message_history)
        print(Fore.YELLOW + f"assistant: {result.output}\n")

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

    prompt_inputs = [
        PromptInput(color=Fore.GREEN, text="Create a new prompt"),
        PromptInput(color=Fore.YELLOW, text="Start a conversation with an existing prompt"),
        PromptInput(color=Fore.MAGENTA, text="Simply start a conversation"),
    ]

    while True:
        intent = prompt_inputs_to_input(prompt_inputs)

        if intent in intent_map:
            intent_map[intent]()
            break
        print(Fore.RED + "Unknown choice, please try again.")
