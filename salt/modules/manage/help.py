from salt.service import Service
from wechaty import Message
from salt.config import MANUAL
import re

sv = Service('__help__', enable_on_default=True, visible=False)

MANUAL = MANUAL.strip()


@sv.on_prefix("help", "帮助", only_to_me=True)
async def help_manual(event: "Message", msg: str):
    conversation = event.room()
    service_name = re.match(r"^(help|帮助) *(?P<service_name>.*)", msg).group("service_name").strip()
    if len(service_name) == 0:
        # await conversation.ready()
        await conversation.say(MANUAL)
        return
    if service_name in Service.get_loaded_services() and Service.get_loaded_services()[service_name].visible:
        help_text = Service.get_loaded_services()[service_name].help.strip()
        await conversation.say(f"帮助: {service_name}\n{help_text}")
        return
    await conversation.say(f"未知的服务: {service_name}")


@sv.on_full_match("lssv", "帮助列表", "帮助清单", only_to_me=False)
async def list_service(event: "Message", msg: str):
    conversation = event.room()
    message = "本群开启的服务为:\n"
    sv_status = sorted(list((await Service.get_all_services_status(event, with_not_visible=False)).items()),
                       key=lambda x: x[1], reverse=True)
    sv.logger.info(sv_status)
    message += "\n".join([f"|{'○' if status else '×'}| {sv_name}" for sv_name, status in sv_status])
    # await conversation.ready()
    await conversation.say(message)
