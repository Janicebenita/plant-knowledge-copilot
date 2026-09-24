from datetime import datetime, timezone
import os
import uuid


class ConversationHistory:
    def __init__(self) -> None:
        self.uri = os.getenv("MONGODB_URI")
        self.collection = None
        if self.uri:
            from pymongo import MongoClient
            client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            self.collection = client[os.getenv("MONGODB_DATABASE", "plant_knowledge_copilot")]["messages"]

    @property
    def durable(self) -> bool:
        return self.collection is not None

    def save(self, conversation_id: str, role: str, content: str) -> None:
        if self.collection is not None:
            self.collection.insert_one({"conversation_id": conversation_id, "role": role, "content": content, "created_at": datetime.now(timezone.utc)})

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())

