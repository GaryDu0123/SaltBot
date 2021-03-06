__version__ = '1.0.0-alpha'

from functools import wraps

from wechaty_puppet import FileBox, ContactQueryFilter, EventReadyPayload  # type: ignore
from wechaty import Wechaty
from wechaty.user import Message
import salt.config
from salt import log
from salt.trigger import handle_list
from salt.service import ServiceFunc, Service, scheduler
from salt.config import MODULES_ON
from salt.message_processor import message_processor
from salt.utils import init_utils
import salt.priv as priv
import importlib
from salt.priv import refresh_all

salt_bot: "SaltBot"
logger = log.new_logger("salt_init")
system_sv = Service("__system__", enable_on_default=True, visible=False, _help="系统运行服务, 这个帮助文字不应该出现",
                    manage_priv=priv.ADMIN)


def init() -> "SaltBot":
    init_utils()
    for modules in MODULES_ON:
        """
        将modules_on(模块)文件夹内的所有py都进行导入
        """
        try:
            importlib.import_module(f'salt.modules.{modules}')
            logger.info(f'Succeeded to load modules "{modules}"')
        except ImportError:
            logger.warning(f"Load modules {modules} not successful")
    global salt_bot  # 全局的变量方便后面调用Room查询
    salt_bot = SaltBot()  # 初始化bot
    scheduler.start()  # 开启日程调用
    return salt_bot


class SaltBot(Wechaty):

    on_ready_once = True  # 解决on_ready事件会调用两次的bug,等待wechaty开发者修复

    async def on_ready(self, payload: EventReadyPayload) -> None:
        if SaltBot.on_ready_once:
            await refresh_all(self)
            SaltBot.on_ready_once = False

    async def on_message(self, msg: Message) -> None:
        """
        listen for message event
        """
        await message_processor(msg)


def on_command(*word, only_to_me: bool = True):
    """
    系统级别的触发, 使用系统的对象, 阻止用户对系统级别的消息进行控制, todo 未完成
    :return:
    """

    def registrar(func):
        @wraps(func)
        async def wrapper(event: "Message", msg: str):
            # 此处可以加日志记录或者判断
            return await func(event, msg)

        # 在此处执行function(service)注册
        sf = ServiceFunc(system_sv, only_to_me, func)
        for w in word:
            if isinstance(w, str):
                trigger.systemTrigger.add(w, sf)
                system_sv.logger.info(
                    f"Success bind system trigger function {sf.__name__} to keyword {w} @{system_sv.name}")
            else:
                system_sv.logger.error(f'Failed to add system trigger `{w}`, expecting `str` but `{type(w)}` given!')
        return wrapper

    return registrar
