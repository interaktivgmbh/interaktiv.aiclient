from langchain_core.messages.base import BaseMessage
from typing import List
from typing import Optional
from typing_extensions import TypeAlias


Prompt: TypeAlias = List[BaseMessage]
BatchPrompts: TypeAlias = List[Optional[Prompt]]
Response: TypeAlias = Optional[str]
