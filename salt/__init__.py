__version__ = '0.0.1'

from functools import wraps
from typing import Union

from wechaty_puppet import FileBox  # type: ignore
from wechaty import Wechaty, Contact
from wechaty.user import Message, Room
import salt.config
from salt import log
from salt.trigger import handle_list
from salt.service import ServiceFunc, Service
from salt.config import MODULES_ON
from salt.message_processor import message_processor
import importlib

# from wechaty_plugin_contrib import (
#     AutoReplyRule,
#     AutoReplyPlugin,
#     AutoReplyOptions,
# )
logger = log.new_logger("salt_init")
system_sv = Service("__system__", enable_on_default=True, visible=False)


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


def on_command(*word, only_to_me: bool = True):
    """
    系统级别的触发, 不需要新建服务对象, 阻止用户对系统级别的消息进行控制, todo 未完成
    :return:
    """

    def registrar(func):
        @wraps(func)
        async def wrapper(conversation: Union[Room, Contact], msg: str):
            # 此处可以加日志记录或者判断
            return await func(conversation, msg)

        # 在此处执行function(service)注册
        sf = ServiceFunc(system_sv, only_to_me, func)
        for w in word:
            if isinstance(w, str):
                trigger.systemTrigger.add(w, sf)
                system_sv.logger.info(f"Success bind system trigger function {sf.__name__} to keyword {w} @{system_sv.name}")
            else:
                system_sv.logger.error(f'Failed to add system trigger `{w}`, expecting `str` but `{type(w)}` given!')
        return wrapper

    return registrar
