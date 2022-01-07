import re
import aiohttp
from salt.service import Service
from typing import Union, Coroutine
from wechaty import Room, Contact, Message
from salt.config import GOOGLE_TRANSLATE_API_KEY
from urllib.parse import quote

sv = Service("翻译", enable_on_default=True)


@sv.on_prefix("翻译")
async def translate(event: "Message", msg: str):
    conversation: "Room" = event.room()
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
    url1 = "https://google-translate53.p.rapidapi.com/Google/Translate"
    querystring = {"text": message, "language": "zh-CN"}
    headers1 = {
        'x-rapidapi-host': "google-translate53.p.rapidapi.com",
        'x-rapidapi-key': GOOGLE_TRANSLATE_API_KEY
    }
    try:
        await conversation.say("翻译中~")
        message = "翻译结果:"
        async with aiohttp.request('POST', url, data=payload, headers=headers) as resp:
            json = await resp.json()

            if "data" in json:
                if 'detectedSourceLanguage' in json["data"]['translations'][0]:
                    message += f"检测到{json['data']['translations'][0]['detectedSourceLanguage']}"
                message += f"\n{json['data']['translations'][0]['translatedText']}"
                await conversation.say(message)
                return
            sv.logger.warning("First google translate API not working")
        async with aiohttp.request('GET', url1, headers=headers1, params=querystring) as resp:
            json = await resp.json()
            if "text" in json:
                message += f"\n{json['text']}"
                await conversation.say(message)
                return
        raise RuntimeError("Translate fail")
    except Exception as e:
        await conversation.say("www翻译出错了~")
        sv.logger.error(e)
