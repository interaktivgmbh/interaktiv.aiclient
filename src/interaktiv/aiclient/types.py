from typing import List, Optional
from typing_extensions import TypeAlias
from langchain_core.messages.base import BaseMessage

Prompt: TypeAlias = List[BaseMessage]
BatchPrompts: TypeAlias = List[Optional[Prompt]]
Response: TypeAlias = Optional[str]
