from typing import List, Optional, Union

from wechaty_puppet import FileBox  # type: ignore

from wechaty import Wechaty, Contact
from wechaty.user import Message, Room

import salt.config
from salt import log
from salt.trigger import handle_list
from salt.config import modules_on
import importlib

__version__ = '0.0.1'

# from wechaty_plugin_contrib import (
#     AutoReplyRule,
#     AutoReplyPlugin,
#     AutoReplyOptions,
# )
logger = log.new_logger("salt_init")


def init() -> "SaltBot":
    for modules in modules_on:
        """
        将modules_on(模块)文件夹内的所有py都进行导入
        """
        try:
            importlib.import_module(f'salt.modules.{modules}')
            logger.info(f'Succeeded to load modules "{modules}"')
        except ImportError:
            logger.warning(f"Load modules {modules} not successful")
    return SaltBot()


class SaltBot(Wechaty):
    async def on_message(self, msg: Message):
        """
        listen for message event
        """
        from_contact: Optional[Contact] = msg.talker()
        # print(f"{from_contact.gender()} | {from_contact.city()} | {from_contact.contact_id}" if from_contact is not None else "From contact is None")

        text = msg.text()  # 获取到的信息
        room: Optional[Room] = msg.room()
        # print(f"{from_contact}, {room}")
        """
        if text == 'test' and await msg.mention_self():
            member_list = await room.member_list()
            text_message = ""
            for member in member_list:
                text_message += member.name + " "
            print(text_message)

            
            await conversation.ready()
            await conversation.say(f'测试回复 - {datetime.now()} from {conversation.room_id} AllMembers: {text_message}')
            # file_box = FileBox.from_url(
            #     'https://ss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/'
            #     'u=1116676390,2305043183&fm=26&gp=0.jpg',
            #     name='ding-dong.jpg')
            # await conversation.say(file_box)
        """
        conversation: Union[Room, Contact] = from_contact if room is None else room
        # if not from_contact.is_self():
        for name in salt.config.BOT_NAME:
            if text.startswith(name):
                text = text[len(name):]  # 切去前缀(bot名字)
                for handler in handle_list:
                    if len(text) == 0:
                        return
                    ret = handler.is_match(text)  # 返回包含服务函数的列表
                    if len(ret) > 0:
                        for sf in ret:
                            await sf.func(conversation, text)
                        return
                break


