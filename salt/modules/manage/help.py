import salt
from salt.service import Service
from typing import Union
from wechaty import Room, Contact

sv = Service('__help__')

MANUAL = f"""
功能清单
Version: {salt.__version__}
[复读] 复读所发送的文本
[翻译] 翻译一些文字到中文 

""".strip()


@sv.on_full_match("help", "帮助")
async def help_manual(conversation: Union[Room, Contact], msg: str):
    await conversation.ready()
    await conversation.say(MANUAL)


@sv.on_full_match("lssv", "帮助列表", "帮助清单")
async def list_service(conversation: Union[Room, Contact], msg: str):
    message = "开启的服务为:\n" + "\n".join(Service.get_loaded_services())
    await conversation.ready()
    await conversation.say(message)


