from typing import Union
from wechaty import Room, Contact, Message
from salt.service import Service
from salt.res import Resource as R
from salt import on_command
import random

sv = Service("聊天", enable_on_default=True, _help="日常聊天模块")

"""
@sv.on_full_match("不需要提示", only_to_me=False)
async def test(event: "Message", msg: str):
    conversation: Union[Room, Contact] = event.room()
    await conversation.say("这是不需要mention的信息")


@sv.on_full_match("需要提示")
async def test2(event: "Message", msg: str):
    conversation: Union[Room, Contact] = event.room()
    await conversation.say("这是需要mention的信息")
"""


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


@on_command("在?", "在吗?", "在？", only_to_me=True)
async def zaima(event: "Message", msg: str):
    conversation = event.room() if event.room() is not None else event.talker()
    await conversation.say('はい！私はいつも貴方の側にいますよ！')


@on_command("获取uid", only_to_me=True)
async def getUid(event: "Message", msg: str):
    talker: Contact = event.talker()
    room: Room = event.room()
    if room is not None:
        await room.say("请私聊使用该功能~")
        return
    await talker.say(f"您的uid是\n{talker.contact_id}")
