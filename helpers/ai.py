import json
from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
    SystemPromptPart,
)
from pydantic_ai.agent import AgentRunResult

from core.models import Conversation


class AIHelper:
    def __init__(self):
        pass

    def create_message_history(json_history):
        message_history = []

        for obj in json_history:
            parts = []
            is_request = False

            for part in obj.get("parts", []):
                if not part:
                    continue
                part_kind = part.get("part_kind")
                content = part.get("content")

                if part_kind == "system-prompt":
                    parts.append(SystemPromptPart(content=content))
                    is_request = True
                elif part_kind == "user-prompt":
                    parts.append(UserPromptPart(content=content))
                    is_request = True
                elif part_kind == "text":
                    parts.append(TextPart(content=content))
                    is_request = False

            if parts:
                if is_request:
                    message_history.append(ModelRequest(parts=parts))
                else:
                    message_history.append(ModelResponse(parts=parts))

        json_history = [
            {
                "parts": [
                    {
                        "content": "You are a good ai agent with name: MasterGuy. You try to help when you can. Your personality is: You are stoic",
                        "timestamp": "2025-08-11T13:50:35.315026Z",
                        "dynamic_ref": None,
                        "part_kind": "system-prompt",
                    },
                    {
                        "content": "hi",
                        "timestamp": "2025-08-11T13:50:35.315036Z",
                        "part_kind": "user-prompt",
                    },
                ]
            },
            {"parts": [{"content": "Greetings.", "part_kind": "text"}]},
            {
                "parts": [
                    {
                        "content": "what's the answer to life the universe and everything?",
                        "timestamp": "2025-08-11T13:50:45.558265Z",
                        "part_kind": "user-prompt",
                    }
                ]
            },
            {
                "parts": [
                    {
                        "content": 'The answer to life, the universe, and everything is 42. This is according to the supercomputer Deep Thought in "The Hitchhiker\'s Guide to the Galaxy."',
                        "part_kind": "text",
                    }
                ]
            },
        ]

    def load_conversation(self, conversation_id: int):
        return None

    def save_conversation(self, result):
        conversation_json = self.conversation_to_json(result)

    def conversation_to_json(self, result: AgentRunResult[str]):
        try:
            all_messages = json.loads(result.all_messages_json().decode("utf-8"))
        except json.JSONDecodeError as e:
            print(f"Could not parse conversation history: {e}")
            
        json_history = []

        for msg in all_messages:
            json_history.extend(msg.get("parts", []))

        return json_history


ai_helper = AIHelper()
