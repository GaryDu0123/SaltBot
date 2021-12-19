__version__ = '0.0.1'
from wechaty_puppet import FileBox  # type: ignore
from wechaty import Wechaty, Contact
from wechaty.user import Message, Room
import salt.config
from salt import log
from salt.trigger import handle_list
from salt.config import MODULES_ON
from salt.message_processor import message_processor
import importlib



# from wechaty_plugin_contrib import (
#     AutoReplyRule,
#     AutoReplyPlugin,
#     AutoReplyOptions,
# )
logger = log.new_logger("salt_init")


def init() -> "SaltBot":
    for modules in MODULES_ON:
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
        # file_box = FileBox.from_url(
        #     'https://ss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/'
        #     'u=1116676390,2305043183&fm=26&gp=0.jpg',
        #     name='ding-dong.jpg')
        # await conversation.say(file_box)
        await message_processor(msg)
