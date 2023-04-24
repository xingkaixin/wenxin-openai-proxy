from typing import List

import httpx
from pydantic import BaseModel

from app.schemas.response import Message


class WenXinChat(BaseModel):
    base_url: str
    chat_completion_path: str
    access_token: str

    def chat(self, messages: List[Message], stream: bool = False):
        request_url = f"{self.base_url}{self.chat_completion_path}"
        headers = {"Content-Type": "application/json"}
        params = {"access_token": self.access_token}
        data = {"messages": [message.dict() for message in messages], "stream": stream}
        if stream:
            with httpx.Client(timeout=None) as client:
                with client.stream(
                    "POST", request_url, headers=headers, params=params, json=data
                ) as response:
                    for event in response.iter_raw():
                        print(event)
                        if event[0:6] == b"data: ":
                            data = event[6:].decode("utf-8").strip()
                            yield data
                        else:
                            yield ""
        else:
            with httpx.Client() as client:
                response = client.post(
                    request_url, headers=headers, params=params, json=data, timeout=30
                )
            if response.status_code == 200:
                json_data = response.json()
                print(json_data)
                return response.status_code, json_data
            else:
                print("Request failed with code {}".format(response.status_code))
                return response.status_code, None
