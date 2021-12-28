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
_black_room_dict: Dict["Room", str] = {}

"""存放黑名单用户"""
_black_user_dict: Dict["Contact", str] = {}

"""用于存储所有管理权限的人, 储存方式为 [room对象: 管理员列表] 因为web版不具备获取群管理的能力, 所以必须每个群手动添加"""
_admin_user_dict: Dict["Room", List["Contact"]] = defaultdict(list)


async def refresh_all(bot):
    """
    刷新超级用户的列表, 因为每次登入都要web版微信的id都会发生变化
    :param bot: salt bot
    :return: None
    """
    _black_user_dict.clear()
    _black_room_dict.clear()
    _superuser_list.clear()

    for name in SUPER_USER_LIST:
        sp_user = await bot.Contact.find(ContactQueryFilter(name=name))
        if sp_user not in _superuser_list:
            _superuser_list.append(sp_user)


async def get_user_priv(event: "Message") -> int:
    talker: "Contact" = event.talker()
    room: "Room" = event.room()
    if talker in _superuser_list:  # 在超级管理员字典中返回SUPERUSER
        return SUPERUSER
    elif room is not None and talker in _admin_user_dict[room]:  # 考虑到可能为私聊, 判断一下room是不是为None, 然后判断一下管理员组
        return ADMIN
    elif talker in _black_user_dict:  # 如果user对象在黑名单中, 返回BLACK
        return BLACK
    elif room in _black_room_dict:  # 如果room对象在黑名单中, 返回BLACK
        return BLACK
    elif room is None:  # 没有房间对象表示为私聊消息
        return PRIVATE
    return NORMAL
