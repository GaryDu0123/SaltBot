from salt.service import Service
from wechaty import Message
from salt.config import MANUAL

sv = Service('__help__', enable_on_default=True, visible=False)

MANUAL = MANUAL.strip()


@sv.on_full_match("help", "帮助", only_to_me=False)
async def help_manual(event: "Message", msg: str):
    conversation = event.room()
    await conversation.ready()
    await conversation.say(MANUAL)


@sv.on_full_match("lssv", "帮助列表", "帮助清单", only_to_me=False)
async def list_service(event: "Message", msg: str):
    conversation = event.room()
    message = "本群开启的服务为:\n"
    sv_status = sorted(list((await Service.get_all_services_status(event)).items()),
                       key=lambda x: x[1], reverse=True)
    sv.logger.info(sv_status)
    message += "\n".join([f"|{'○'if status else '×'}| {sv_name}" for sv_name, status in sv_status])
    await conversation.ready()
    await conversation.say(message)