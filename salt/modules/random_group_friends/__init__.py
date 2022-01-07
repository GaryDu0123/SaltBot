#!/usr/bin/env python
# -*-coding:utf-8 -*-
from salt.service import Service
from wechaty import Message, Contact
import random
sv = Service("随机群友", enable_on_default=False)


@sv.on_full_match("随机群友", only_to_me=True)
async def random_group_friend(event: "Message", msg: str):
    room = event.room()
    room_friend_list: list = await room.member_list()
    lucky_friend: "Contact" = room_friend_list[random.randint(0, len(room_friend_list)-1)]
    friend_alias = await room.alias(lucky_friend)
    lucky_friend_name = friend_alias if bool(friend_alias) else lucky_friend.name
    await room.say(f"\n幸运的群友是: {lucky_friend_name}",  [lucky_friend.contact_id])
    await room.say(await lucky_friend.avatar())
