from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core import config
from app.wenxin import WenXinChat

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")


def get_wenxin_chat():
    wenxin_chat = WenXinChat(
        base_url=config.wenxin.base_url,
        chat_completion_path=config.wenxin.chat_completion_path,
        access_token=config.wenxin.access_token,
    )
    return wenxin_chat


def is_valid_user(token: str = Depends(reusable_oauth2)) -> bool:
    if token in config.token:
        return True
    raise HTTPException(
        status_code=400, detail="Token is not valid. Please check your token."
    )
