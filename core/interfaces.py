from pydantic import BaseModel
from colorama import Fore

class PromptInput(BaseModel):
    color: str = Fore.MAGENTA
    text: str
    is_choice: bool = True
    add_new_line: bool = True
