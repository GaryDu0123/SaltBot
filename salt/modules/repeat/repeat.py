from salt.service import Service
from typing import Union
from wechaty import Room, Contact
import re

sv = Service("复读")


@sv.on_prefix("复读")
async def repeat(conversation: Union[
                Room, Contact], msg: str):
    msg = re.match(r"^复读(?P<message>.*)", msg)
    message = msg.group("message").strip()
    if message == "":
        message = "w复读内容是空的!!!(•́へ•́╬)"
    await conversation.ready()
    await conversation.say(message)
