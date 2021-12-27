from typing import Union
from wechaty import Room, Contact, Message
from salt.service import Service
from salt.res import Resource as R
import random
sv = Service("聊天", enable_on_default=True, _help="日常聊天模块")


@sv.on_full_match("不需要提示", only_to_me=False)
async def test(event: "Message", msg: str):
    conversation: Union[Room, Contact] = event.room()
    await conversation.say("这是不需要mention的信息")


@sv.on_full_match("需要提示")
async def test2(event: "Message", msg: str):
    conversation: Union[Room, Contact] = event.room()
    await conversation.say("这是需要mention的信息")


@sv.on_keyword("yysy", "有一说一", "确实")
async def yysy(event: "Message", msg: str):
    conversation: Union[Room, Contact] = event.room()
    if random.random() < 0.10:
        await conversation.say(R("img/确实.jpg").img)


@sv.on_full_match("获取头像")
async def get_a(event: "Message", msg: str):
    room = event.room()
    talker = event.talker()
    file = await talker.avatar()
    await file.to_file(f"./res/test/{file.name}", True)