from wechaty import Room, Contact, Message
from salt import on_command
from salt.service import _loaded_service
import re


@on_command("开启", "启用")
async def enable_service(event: "Message", msg: str):
    conversation: "Room" = event.room()
    command = re.match("^(开启|启用) *(?P<command>.+)", msg).group("command")
    for sv_name, sv in _loaded_service.items():
        if sv_name.lower() == command.lower():
            await sv.enable_service(conversation)
            await conversation.say(f"已成功开启服务 - {sv_name}")
            sv.logger.info(f"服务{sv_name}已成功在{await conversation.topic()}开启")
            return
    await conversation.say(f"未找到服务{command}")


@on_command("关闭", "禁用")
async def enable_service(event: "Message", msg: str):
    conversation: "Room" = event.room()
    command = re.match("^(关闭|禁用) *(?P<command>.+)", msg).group("command")
    for sv_name, sv in _loaded_service.items():
        if sv_name.lower() == command.lower():
            await sv.disable_service(conversation)
            await conversation.say(f"已成功禁用服务 - {sv_name}")
            sv.logger.info(f"服务{sv_name}已成功在{await conversation.topic()}关闭")
            return
    await conversation.say(f"未找到服务{command}")
