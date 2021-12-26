# -*- coding: utf-8 -*
"""
负责权限控制, 还未实现
"""
from typing import Dict, List
from wechaty import Message, Contact, Room
from collections import defaultdict

BLACK = -999
DEFAULT = 0
NORMAL = 1
PRIVATE = 10
ADMIN = 21
OWNER = 22
WHITE = 51
SUPERUSER = 999

_black_room_list: Dict["Room", str] = {}
_black_user_list: Dict["Contact", str] = {}

"""用于存储所有管理权限的人"""
_admin_user_dict: Dict[str, List["Contact"]] = defaultdict(list)

"""用于储存所有有群主权限的人"""
_owner_user_dict: Dict[str, List["Contact"]] = defaultdict(list)


def get_user_priv(event: "Message"):
    talker: "Contact" = event.talker()
    room: "Room" = event.room()
