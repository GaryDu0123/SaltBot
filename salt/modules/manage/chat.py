from typing import Union
from wechaty import Room, Contact
from salt.service import Service
from salt.res import Resource as R
import random
sv = Service("聊天", enable_on_default=True)


@sv.on_full_match("不需要提示", only_to_me=False)
async def test(conversation: Union[Room, Contact], msg: str):
    await conversation.say("这是不需要mention的信息")


@sv.on_full_match("需要提示")
async def test2(conversation: Union[Room, Contact], msg: str):
    await conversation.say("这是需要mention的信息")


@sv.on_keyword("yysy", "有一说一", "确实")
async def yysy(conversation: Union[Room, Contact], msg: str):
    if random.random() < 0.10:
        await conversation.say(R("img/确实.jpg").img)
