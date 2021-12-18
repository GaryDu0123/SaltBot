import re
import aiohttp
from salt.service import Service
from typing import Union
from wechaty import Room, Contact
from salt.config import GOOGLE_TRANSLATE_API_KEY
from urllib.parse import quote

sv = Service("翻译")


@sv.on_prefix("翻译")
async def translate(conversation: Union[Room, Contact], msg: str):
    url = "https://google-translate1.p.rapidapi.com/language/translate/v2"
    msg = re.match(r"^翻译 *(?P<message>.*)", msg)
    message = msg.group("message").strip()
    payload = f"q={quote(message, 'utf-8')}&target=zh-CN"
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'accept-encoding': "application/gzip",
        'x-rapidapi-host': "google-translate1.p.rapidapi.com",
        'x-rapidapi-key': GOOGLE_TRANSLATE_API_KEY
    }
    try:
        await conversation.say("翻译中~")
        async with aiohttp.request('POST', url, data=payload, headers=headers) as resp:
            json = await resp.json()
            message = "翻译结果:"
            if 'detectedSourceLanguage' in json["data"]['translations'][0]:
                message += f"检测到{json['data']['translations'][0]['detectedSourceLanguage']}"
            message += f"\n{json['data']['translations'][0]['translatedText']}"
            await conversation.say(message)
    except Exception as e:
        await conversation.say("www翻译出错了~")
        sv.logger.error(e)
