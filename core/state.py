from typing import Optional
import dataclasses
from dataclasses import dataclass
from core.models import User

@dataclass
class RuntimeState:
    login_user: Optional[User] = dataclasses.field(default=None)
    system_prompt: str = dataclasses.field(default="You are simply an AI")
    personality_prompt: str = dataclasses.field(default="")

