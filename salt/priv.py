# -*- coding: utf-8 -*
"""
负责权限控制, 还未实现
"""
from typing import Dict, List
from wechaty import Message, Contact, Room
from collections import defaultdict

from wechaty_puppet import ContactQueryFilter

from salt.config import SUPER_USER_LIST

BLACK = -999
DEFAULT = 0
NORMAL = 1
PRIVATE = 10
ADMIN = 21
OWNER = 22
WHITE = 51
SUPERUSER = 999

"""超级用户的列表"""
_superuser_list: List["Contact"] = []

"""存放黑名单群聊"""
_black_room_list: Dict["Room", str] = {}

"""存放黑名单用户"""
_black_user_list: Dict["Contact", str] = {}

"""用于存储所有管理权限的人, 储存方式为 [群名: 管理员列表] 因为web版不具备获取群管理的能力, 所以必须每个群手动添加"""
_admin_user_dict: Dict[str, List["Contact"]] = defaultdict(list)


async def refresh_superuser_list(bot):
    _superuser_list.clear()
    for name in SUPER_USER_LIST:
        sp_user = await bot.Contact.find(ContactQueryFilter(name=name))
        if sp_user not in _superuser_list:
            _superuser_list.append(sp_user)


async def get_user_priv(event: "Message"):
    talker: "Contact" = event.talker()
    room: "Room" = event.room()
    room_name = await room.topic()
