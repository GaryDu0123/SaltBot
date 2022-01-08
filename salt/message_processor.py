from wechaty import Room, Contact, Message
from typing import Union, Optional
from salt import handle_list
from salt.config import BOT_NAME
from salt.utils.text_cleaner import clean_text


async def is_mention_self(msg: "Message") -> bool:
    bot_room_name = await msg.room().alias(msg.wechaty)
    if await msg.mention_self():
        return True
    elif f"@{bot_room_name} " in msg.text():
        return True
    return False


async def message_processor(msg: "Message"):
    # talker: Optional[Contact] = msg.talker()  # 始终会返回说话者的对象
    room: Optional[Room] = msg.room()  # 私聊的时候这里为None
    text: str = msg.text()  # 获取到信息

    is_mention = False
    bot_room_name = await room.alias(msg.wechaty)

    # print(await msg.mention_text())

    if await is_mention_self(msg):
        text = text.replace(f"@{bot_room_name} ", "")
        is_mention = True

    text = clean_text(text).strip()

    if not text:  # 理论上不可能, 因为不允许发送空消息
        return

    message_to_me = False  # 检查是不是叫了名字
    for name in BOT_NAME:
        if text.startswith(name):
            message_to_me = True
            text: str = text[len(name):].strip()  # 切去前缀(bot名字)
            break

    if not text:
        return

    for handler in handle_list:
        ret = handler.search_handler(text)  # 寻找触发器
        if len(ret) > 0:
            for sf in ret:
                # 检查服务是否开启
                if not (await sf.service.check_all_user_priv(msg)):
                    continue
                # 命令必须@(叫名字)触发->{only_to_me == True || 是否@bot } not True or后面必须为True
                # 命令不是必须叫名字   ->{only_to_me == False} 永真式
                if not sf.only_to_me or message_to_me or is_mention:
                    try:
                        sf.service.logger.info(f"Message {text} handled by {sf.__name__}")
                        await sf.func(msg, text)
                    except Exception as e:
                        sf.service.logger.error(f"{type(e)} occurred when {sf.__name__} handling message {text}")
                        sf.service.logger.exception(e)
            # return  # 被一个类型的触发器handle了直接返回
