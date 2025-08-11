from colorama import Fore

from core.input import prompt_inputs_to_input, sinput
from core.models import Conversation
from core.state import RuntimeState
from core.interfaces import PromptInput
from core.prompt import decide_on_prompts, ask_question
from helpers.ai import ai_helper


def start_new_conversation() -> bool:
    # Create a new conversation record
    new_conversation = Conversation(user_id=RuntimeState.login_user.id)
    
    try:
        Conversation.insert(new_conversation)
        from core.database import con
        con.commit()
        
        # Get the created conversation
        created_conversation = list(
            Conversation.select(
                where=f"user_id='{RuntimeState.login_user.id}'"
            )
        )[-1]  # Get the last inserted conversation
        
        RuntimeState.current_conversation = created_conversation
        print(Fore.GREEN + "New conversation started!")
        
        # Now go through the prompt selection flow
        decide_on_prompts()
        return True
    except Exception as e:
        print(Fore.RED + f"Error creating conversation: {e}")
        return False


def select_existing_conversation() -> bool:
    conversations = list(
        Conversation.select(
            where=f"user_id='{RuntimeState.login_user.id}'"
        )
    )
    
    if not conversations:
        print(Fore.YELLOW + "No existing conversations found. Let's start a new one.")
        return start_new_conversation()
    
    print(Fore.MAGENTA + "\nYour conversations:")
    for conv in conversations:
        display_title = conv.title if conv.title else f"Conversation {conv.id}"
        print(Fore.CYAN + f"{conv.id}. {display_title}")
    
    while True:
        choice = sinput(
            Fore.CYAN + "Choose a conversation ID, or 0 to start a new conversation: "
        ).strip()
        
        if choice == "0":
            return start_new_conversation()
        
        try:
            choice_id = int(choice)
            selected = next((c for c in conversations if c.id == choice_id), None)
            if selected:
                RuntimeState.current_conversation = selected
                print(Fore.GREEN + f"Selected conversation: {selected.title or f'Conversation {selected.id}'}")
                
                # Load the conversation and start asking questions
                result = ai_helper.load_conversation(selected.id)
                ask_question()
                return True
            else:
                print(Fore.RED + "Invalid choice. Try again.")
        except ValueError:
            print(Fore.RED + "Invalid input. Try again.")


def conversation_selection() -> bool:
    """Handle conversation selection for logged-in users or direct conversation for non-logged users"""
    
    # If user is not logged in, go straight to prompt selection
    if not RuntimeState.login_user:
        decide_on_prompts()
        return True
    
    prompt_inputs = [
        PromptInput(color=Fore.GREEN, text="Start a new conversation"),
        PromptInput(color=Fore.YELLOW, text="Select an existing conversation"),
    ]
    
    intent_map = {
        "1": start_new_conversation,
        "new": start_new_conversation,
        "2": select_existing_conversation,
        "existing": select_existing_conversation,
    }
    
    while True:
        intent = prompt_inputs_to_input(prompt_inputs)
        
        if intent in intent_map:
            return intent_map[intent]()
        print(Fore.RED + "Unknown choice, please try again.")