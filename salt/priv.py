# -*- coding: utf-8 -*
"""
负责权限控制, 还未实现
"""
from typing import Dict, List
from wechaty import Message, Contact, Room
from collections import defaultdict
from datetime import timedelta, datetime
from wechaty_puppet import ContactQueryFilter

from salt.config import SUPER_USER_LIST

BLACK = -999
PRIVATE = -10
DEFAULT = 0
NORMAL = 1
ADMIN = 21
OWNER = 22
WHITE = 51
SUPERUSER = 999

"""超级用户的列表"""
_superuser_list: List["Contact"] = []

"""存放黑名单群聊"""
_black_room_dict: Dict["Room", "datetime"] = {}

"""存放黑名单用户"""
_black_user_dict: Dict["Contact", "datetime"] = {}

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

    for uid in SUPER_USER_LIST:
        sp_user = await bot.Contact.find(ContactQueryFilter(id=uid))  # todo 还不确定这里到底应该做什么权限处理
        from . import system_sv
        if sp_user is None:
            system_sv.logger.critical(f"Could not load the SUPERUSER {uid}: User not found")
            system_sv.logger.critical(f"警告: 无法载入超级用户 {uid}, 请检查该人id是否正确且为Bot好友")
            continue
        if sp_user not in _superuser_list:
            _superuser_list.append(sp_user)
            system_sv.logger.info(f"Successful load SUPERUSER {uid}")


async def get_user_priv(event: "Message") -> int:
    talker: "Contact" = event.talker()
    room: "Room" = event.room()
    if talker in _superuser_list:  # 在超级管理员字典中返回SUPERUSER
        return SUPERUSER
    elif await event.room().owner() == talker:
        return OWNER
    elif room is not None and talker in _admin_user_dict[room]:  # 考虑到可能为私聊, 判断一下room是不是为None, 然后判断一下管理员组
        return ADMIN
    elif talker in _black_user_dict:  # 如果user对象在黑名单中, 返回BLACK
        return BLACK
    elif room in _black_room_dict:  # 如果room对象在黑名单中, 返回BLACK
        return BLACK
    elif room is None:  # 没有房间对象表示为私聊消息
        return PRIVATE
    return NORMAL


def set_block_room(room: "Room", block_time: "timedelta"):
    _black_room_dict[room] = datetime.now() + block_time


def set_block_user(contact: "Contact", block_time: "timedelta"):
    _black_user_dict[contact] = datetime.now() + block_time


def check_is_block_user(contact: "Contact"):
    if contact in _black_user_dict:
        if datetime.now() > _black_user_dict[contact]:  # 如果现在的时间大于拉黑时间, 删除拉黑记录
            del _black_user_dict[contact]
            return False  # 返回该用户不是被拉黑的
        return True  # True表示被拉黑
    return False


def check_is_block_room(room: "Room"):
    if room in _black_room_dict:
        if datetime.now() > _black_room_dict[room]:
            del _black_room_dict[room]
            return False
        return True
    return False


def check_priv(user_priv: int, need_priv: int):
    return user_priv >= need_priv
