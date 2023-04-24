import json
from typing import Any, Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sse_starlette.sse import EventSourceResponse

from app import schemas
from app.api import deps
from app.schemas.response import Message

router = APIRouter()


@router.post("/", status_code=status.HTTP_200_OK)
async def create_chat_completions(
    *,
    wenxin_chat=Depends(deps.get_wenxin_chat),
    body: schemas.Request.Wenxin,
    request: Request,
    valid_user: bool = Depends(deps.is_valid_user)
):
    question = body.messages[-1]
    if question.role == "user":
        pass
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No Question Found")

    messages = []
    for message in body.messages:
        if message.role == "system":
            messages.append(Message(role="user", content=message.content))
            messages.append(Message(role="assistant", content="OK"))
        else:
            messages.append(message)
    if body.stream:

        async def eval_chatglm():
            sends = 0
            first = True
            for response in wenxin_chat.chat(messages=messages, stream=True):
                if await request.is_disconnected():
                    return
                try:
                    ret = json.loads(response)["result"]
                    end_flag = json.loads(response)["is_end"]
                except:
                    print(response)
                    ret = ""
                    end_flag = True
                if first:
                    first = False
                    # sse start
                    yield sse_data(delta_data={"role": "assistant"})
                # sse response
                if end_flag:
                    # sse stop
                    yield sse_data(delta_data={}, finish_reason="stop")
                    yield "[DONE]"
                yield sse_data(delta_data={"content": ret})

        return EventSourceResponse(eval_chatglm(), ping=10000)
    else:
        status_code, response = wenxin_chat.chat(messages=messages)
        if status_code == 200 and "error_code" not in response:
            return data(response["result"])
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "WenXin Error!")


def data(
    response: str,
) -> schemas.Response.ChatCompletion:
    message = schemas.Response.Message(content=response)
    choice = schemas.Response.Choice(message=message)
    return schemas.Response.ChatCompletion(choices=[choice])


def sse_data(
    delta_data: Dict[str, str], finish_reason: str = None
) -> Union[str, bytes]:
    message = schemas.Response.DeltaChoice(
        delta=delta_data, finish_reason=finish_reason
    )
    return schemas.Response.DeltaChatCompletion(choices=[message]).json(
        ensure_ascii=False
    )
