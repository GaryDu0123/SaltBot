from salt.service import Service
from typing import Union
from wechaty import Room, Contact

sv = Service("复读")


@sv.on_full_match("复读")
async def repeat(conversation: Union[
                Room, Contact], msg: str):

    await conversation.ready()
    await conversation.say(msg)


def hello():
    # print("hello")
    # from salt.trigger import
    # list_p.append("hello")
    pass