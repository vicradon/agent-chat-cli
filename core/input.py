from typing import Optional
from colorama import Fore, Style
from core.cleanup import graceful_exit
from core.interfaces import PromptInput

def sinput(prompt):
    try:
        return input(prompt)
    except EOFError:
        return graceful_exit()

def prompt_input_to_str(prompt_input: PromptInput, index: Optional[int] = None):
    extra_line = "\n" if prompt_input.add_new_line else ""
    start_line = f"{index+1}. " if index is not None else ""

    return prompt_input.color + start_line + prompt_input.text + extra_line 

def prompt_inputs_to_input(prompt_inputs: list[PromptInput], opening_question: Optional[PromptInput] = None):
    input_string = ""

    if opening_question:
        opening_question.is_choice = False
        input_string += prompt_input_to_str(opening_question)
    else:
        input_string += prompt_input_to_str(PromptInput(text="Would you like to:", is_choice=False))

    for index, prompt_input in enumerate(prompt_inputs):
        input_string += prompt_input_to_str(prompt_input, index)

    input_string += prompt_input_to_str(PromptInput(text="Choice: ", color=Fore.WHITE, is_choice=False, add_new_line=False))

    return sinput(input_string).strip()
