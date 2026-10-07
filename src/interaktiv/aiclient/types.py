from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from typing_extensions import TypeAlias


Message: TypeAlias = Dict[str, Any]
Prompt: TypeAlias = List[Message]
BatchPrompts: TypeAlias = List[Optional[Prompt]]
Response: TypeAlias = Optional[str]
BatchResponse: TypeAlias = List[Union[Response, BaseException]]
