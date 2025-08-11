import json
import base64
from typing import Optional
from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
    SystemPromptPart,
)
from pydantic_ai.agent import AgentRunResult

from core.database import con
from core.models import Conversation
from core.state import RuntimeState


class ConversationManager:
    def __init__(self):
        pass

    def create_message_history(self, json_history):
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

        return message_history


    def load_conversation(
        self, conversation_id: Optional[int] = None
    ) -> Optional[AgentRunResult]:
        """Load conversation from database and return AgentRunResult if exists"""
        if not conversation_id and RuntimeState.current_conversation:
            conversation_id = RuntimeState.current_conversation.id

        if not conversation_id:
            return None

        try:
            conversation = next(Conversation.select(where=f"id='{conversation_id}'"))

            if not conversation.content:
                return None

            json_str = base64.b64decode(conversation.content.encode("ascii")).decode("utf-8")

            json_history = json.loads(json_str)
            message_history = self.create_message_history(json_history)

            # Create a mock AgentRunResult-like object that has all_messages method
            class MockResult:
                def __init__(self, messages):
                    self.messages = messages

                def all_messages(self):
                    return self.messages

            return MockResult(message_history)

        except Exception as e:
            print(f"Error loading conversation: {e}")
            return None


    def save_conversation(self, result: AgentRunResult[str]):
        """Save conversation to database"""
        if not RuntimeState.current_conversation:
            return

        try:
            json_history = self.conversation_to_json(result)
            json_str = json.dumps(json_history)

            json_base64 = base64.b64encode(json_str.encode("utf-8")).decode("ascii")

            Conversation.update(
                set_query=f"content='{json_base64}'",
                where=f"id='{RuntimeState.current_conversation.id}'",
            )
            con.commit()

        except Exception as e:
            print(f"Error saving conversation: {e}")

    def conversation_to_json(self, result: AgentRunResult[str]):
        try:
            all_messages = json.loads(result.all_messages_json().decode("utf-8"))
        except json.JSONDecodeError as e:
            print(f"Could not parse conversation history: {e}")
            return []

        return all_messages


conversation_manager = ConversationManager()
