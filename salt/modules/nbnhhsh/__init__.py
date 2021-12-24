import aiohttp
import re
from salt.service import Service
from wechaty import Message, Room

help_manual = """发送 [?不知道的拼音缩写]
触发只接受英文字母
比如 ?nbnhhsh -> 能不能好好说话
"""

sv = Service("能不能好好说话", enable_on_default=True,
             _help=help_manual)


@sv.on_regex(re.compile(r"^[?？] *[a-z]+$"), only_to_me=False)
async def nbnhhsh(event: "Message", msg: str):
    conversation: "Room" = event.room()
    msg = re.match(r"^[?？] *(?P<message>[a-z]+)$", msg).group("message")
    try:
        async with aiohttp.TCPConnector(ssl=False) as connector:
            async with aiohttp.request(
                    'POST',
                    url='https://lab.magiconch.com/api/nbnhhsh/guess',
                    json={"text": msg},
                    connector=connector,
            ) as resp:
                j = await resp.json()
                if len(j) > 0 and "trans" in j[0]:
                    name = j[0].get("name", msg)
                    result = j[0].get('trans', "没有结果")
                    await conversation.say(f"{name}:\n{' '.join(result) if isinstance(result, list) else result}")
                    return
                await conversation.say(f"{msg}:\n没有结果")
    except Exception as e:
        await conversation.say(f"{msg}:\n没有结果")
        sv.logger.error(e)
