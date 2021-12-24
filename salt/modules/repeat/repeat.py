from salt.service import Service
from wechaty import Room, Message
from salt import config
import re

sv = Service("复读", _help=f"发送 [{config.BOT_NAME[0]}复读 需要复读的消息]\n"
                         f"群 友 都 是 复 读 机")


@sv.on_prefix("复读")
async def repeat(event: "Message", msg: str):
    conversation: "Room" = event.room()
    msg = re.match(r"^复读(?P<message>.*)", msg)
    message = msg.group("message").strip()
    if message == "":
        message = "w复读内容是空的!!!(•́へ•́╬)"
    await conversation.ready()
    await conversation.say(message)
