from typing import Literal
from colorama import Fore
from pydantic_ai import Agent


from core.ai_models import general_model
from core.models import Prompts, Conversation
from core.input import prompt_inputs_to_input, sinput
from core.state import RuntimeState
from core.database import con
from core.interfaces import PromptInput
from helpers.conversation import conversation_manager


def ask_question():
    system_prompt = f"{RuntimeState.system_prompt}"

    if RuntimeState.personality_prompt:
        system_prompt += f"Your personality is: {RuntimeState.personality_prompt}"

    agent = Agent(
        general_model,
        system_prompt=system_prompt,
    )

    result = conversation_manager.load_conversation(1)

    while True:
        user_input = sinput(Fore.CYAN + "ask a question: ")
        message_history = result.all_messages() if result else []

        result = agent.run_sync(user_input, message_history=message_history)
        
        conversation_manager.save_conversation(result)

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
            Fore.CYAN
            + f"Choose a {ptype} prompt ID, 0 to create a new one, or -1 to exit this input: "
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
            Fore.MAGENTA
            + "Create:\n"
            + Fore.GREEN
            + "1. System prompt\n"
            + Fore.YELLOW
            + "2. Personality prompt\n"
            + Fore.WHITE
            + "Choice: "
        ).strip()

        if choice not in type_map:
            print(Fore.RED + "Invalid choice.")
            continue

        result = type_map[choice]()

        if not result:
            break

        if choice in {"1", "sys", "system"}:
            RuntimeState.system_prompt = result

            follow_up = (
                sinput(
                    Fore.CYAN
                    + "Would you like to create a personality prompt as well? (Y/n): "
                )
                .strip()
                .lower()
            )

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

    a_or_the = "the" if RuntimeState.login_user else "a"
    prompt_inputs = [
        PromptInput(color=Fore.GREEN, text="Create a new prompt"),
        PromptInput(
            color=Fore.YELLOW, text=f"Start {a_or_the} conversation with an existing prompt"
        ),
        PromptInput(color=Fore.MAGENTA, text=f"Simply start {a_or_the} conversation"),
    ]

    while True:
        intent = prompt_inputs_to_input(prompt_inputs)

        if intent in intent_map:
            intent_map[intent]()
            break
        print(Fore.RED + "Unknown choice, please try again.")


def new_conversation():
    # Create a new conversation record
    new_conv = Conversation(user_id=RuntimeState.login_user.id)
    
    try:
        Conversation.insert(new_conv)
        con.commit()
        
        # Get the created conversation
        created_conversation = list(
            Conversation.select(
                where=f"user_id='{RuntimeState.login_user.id}'"
            )
        )[-1]  # Get the last inserted conversation
        
        RuntimeState.current_conversation = created_conversation
        print(Fore.GREEN + "New conversation started!")
        
    except Exception as e:
        print(Fore.RED + f"Error creating conversation: {e}")
    
    decide_on_prompts()

def select_existing_conversation():
    conversations = list(
        Conversation.select(
            where=f"user_id='{RuntimeState.login_user.id}'"
        )
    )
    
    if not conversations:
        print(Fore.YELLOW + "No existing conversations found. Let's start a new one.")
        return new_conversation()
    
    print(Fore.MAGENTA + "\nYour conversations:")
    for conv in conversations:
        display_title = conv.title if conv.title else f"Conversation {conv.id}"
        print(Fore.CYAN + f"{conv.id}. {display_title}")
    
    while True:
        choice = sinput(
            Fore.CYAN + "Choose a conversation ID, or 0 to start a new conversation: "
        ).strip()
        
        if choice == "0":
            return new_conversation()
        
        try:
            choice_id = int(choice)
            selected = next((c for c in conversations if c.id == choice_id), None)
            if selected:
                RuntimeState.current_conversation = selected
                print(Fore.GREEN + f"Selected conversation: {selected.title or f'Conversation {selected.id}'}")
                
                # Load the conversation context and return - ask_question() will be called from main()
                conversation_manager.load_conversation(selected.id)
                return
            else:
                print(Fore.RED + "Invalid choice. Try again.")
        except ValueError:
            print(Fore.RED + "Invalid input. Try again.")


def decide_on_conversation():
    intent_map = {
        "1": new_conversation,
        "new": new_conversation,
        "2": select_existing_conversation,
        "existing": select_existing_conversation,
    }

    prompt_inputs = [
        PromptInput(color=Fore.GREEN, text="Start a new conversation"),
        PromptInput(
            color=Fore.YELLOW, text="Select an existing conversation"
        ),
    ]

    while True:
        intent = prompt_inputs_to_input(prompt_inputs)

        if intent in intent_map:
            intent_map[intent]()
            break
        print(Fore.RED + "Unknown choice, please try again.")
