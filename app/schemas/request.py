from typing import List, Optional

from pydantic import BaseModel

from .chat_completion import Message


class Wenxin(BaseModel):
    messages: List[Message]
    stream: Optional[bool] = False