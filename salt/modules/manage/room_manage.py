#!/usr/bin/env python
# -*-coding:utf-8 -*-
import os
from typing import Dict, List
from wechaty import Room, Message, Contact

import salt
from salt import on_command, config
from salt.priv import check_priv, get_user_priv
# from collections import defaultdict
import salt.priv as priv
from salt.priv import _admin_user_dict
from salt.service import Service
from wechaty_puppet import ContactQueryFilter, RoomMemberQueryFilter

try:
    import ujson as json
except ImportError:
    import json

sv = Service("__room__manage__", enable_on_default=True, visible=False,
             user_priv=priv.OWNER, manage_priv=priv.SUPERUSER)

# _admin_user_dict: Dict[str, List[str]] = defaultdict(list)
_config_dir = os.path.expanduser(f'{config.CONFIG_DIR}/room_config/'
                                 if config.CONFIG_DIR is not None else
                                 "~/.SaltBot/room_config/")
os.makedirs(_config_dir, exist_ok=True)
config_path = os.path.join(_config_dir, f'room_config.json')


def _update_room_admin_json():
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({
            room_name: _admin_user_dict[room_name]
            for room_name in _admin_user_dict
        },
            f,
            indent=2,
            ensure_ascii=False)


def _read_config_from_json() -> dict:
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        salt.logger.error(e)
        return {}


def init_modules():
    _admin_user_dict.clear()
    _admin_user_dict.update(_read_config_from_json())  # 初始化加载存到config里面的管理员


init_modules()


@sv.on_prefix("添加管理员", only_to_me=True)
async def add_admin(event: "Message", msg: str):
    room = event.room()
    if room is None:
        await event.talker().say("请在群聊内使用该命令")
        return

    # user_priv = await get_user_priv(event)
    # if not check_priv(user_priv, priv.OWNER):
    #     await event.room().say(f"权限不足, 修改所需要的权限为{priv.OWNER}, 而您的权限为{user_priv}")
    #     return
    mention_list = set(await event.mention_list())
    if not mention_list:
        await event.room().say("请@要添加的人")
        return
    is_changed = False  # 记录本次更改是否改变了管理员的设置的flag
    room_topic: str = await room.topic()
    failed_list = []
    for person in mention_list:  # todo 暂时还是使用群聊名做记录吧, 还是担心id可能会变
        if person.contact_id not in _admin_user_dict[room_topic]:
            is_changed = True
            _admin_user_dict[room_topic].append(person.contact_id)
        failed_list.append(person.name)
    if failed_list:
        await room.say(f"添加{' '.join(failed_list)}管理员身份失败")
    await room.say(f"操作完成")
    if is_changed:
        _update_room_admin_json()


@sv.on_full_match("删除管理员", only_to_me=True)
async def del_admin(event: "Message", msg: str):
    room = event.room()
    if room is None:
        await event.talker().say("请在群聊内使用该命令")
        return
    # user_priv = await get_user_priv(event)
    # if not check_priv(user_priv, priv.OWNER):
    #     await event.room().say(f"权限不足, 修改所需要的权限为{priv.OWNER}, 而您的权限为{user_priv}")
    #     return
    mention_list = set(await event.mention_list())
    if not mention_list:
        await event.room().say("请@要添加的人")
        return
    is_changed = False  # 记录本次更改是否改变了管理员的设置的flag
    room_topic: str = await room.topic()
    failed_list = []
    for person in mention_list:  # todo 暂时还是使用群聊名做记录吧, 还是担心id可能会变
        if person.contact_id in _admin_user_dict[room_topic]:
            is_changed = True
            _admin_user_dict[room_topic].remove(person.contact_id)
            continue
        failed_list.append(person.name)
    if failed_list:
        await room.say(f"取消{' '.join(failed_list)}管理员身份失败")
    await room.say(f"操作完成")
    if is_changed:
        _update_room_admin_json()


@on_command("管理员列表", only_to_me=True)
async def admin_list(event: "Message", msg: str):
    room = event.room()
    if room is None:
        await event.talker().say("请在群聊内使用该命令")
        return
    room_admin_list = _admin_user_dict[await room.topic()]
    # for contact_id in room_admin_list:
    #     await room.find(RoomMemberQueryFilter())
    await room.say("本群Bot管理员为\n" + "\n".join(room_admin_list))
import os
from typing import Dict, List
from wechaty import Room, Message, Contact

import salt
from salt import on_command, config
from salt.priv import check_priv, get_user_priv
# from collections import defaultdict
import salt.priv as priv
from salt.priv import _admin_user_dict
from salt.service import Service
from wechaty_puppet import ContactQueryFilter, RoomMemberQueryFilter

try:
    import ujson as json
except ImportError:
    import json

sv = Service("__room__manage__", enable_on_default=True, visible=False,
             user_priv=priv.OWNER, manage_priv=priv.SUPERUSER)

# _admin_user_dict: Dict[str, List[str]] = defaultdict(list)
_config_dir = os.path.expanduser(f'{config.CONFIG_DIR}/room_config/'
                                 if config.CONFIG_DIR is not None else
                                 "~/.SaltBot/room_config/")
os.makedirs(_config_dir, exist_ok=True)
config_path = os.path.join(_config_dir, f'room_config.json')


def _update_room_admin_json():
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({
            room_name: _admin_user_dict[room_name]
            for room_name in _admin_user_dict
        },
            f,
            indent=2,
            ensure_ascii=False)


def _read_config_from_json() -> dict:
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        salt.logger.error(e)
        return {}


def init_modules():
    _admin_user_dict.clear()
    _admin_user_dict.update(_read_config_from_json())  # 初始化加载存到config里面的管理员


init_modules()


@sv.on_prefix("添加管理员", only_to_me=True)
async def add_admin(event: "Message", msg: str):
    room = event.room()
    if room is None:
        await event.talker().say("请在群聊内使用该命令")
        return

    # user_priv = await get_user_priv(event)
    # if not check_priv(user_priv, priv.OWNER):
    #     await event.room().say(f"权限不足, 修改所需要的权限为{priv.OWNER}, 而您的权限为{user_priv}")
    #     return
    mention_list = set(await event.mention_list())
    if not mention_list:
        await event.room().say("请@要添加的人")
        return
    is_changed = False  # 记录本次更改是否改变了管理员的设置的flag
    room_topic: str = await room.topic()
    failed_list = []
    for person in mention_list:  # todo 暂时还是使用群聊名做记录吧, 还是担心id可能会变
        if person.contact_id not in _admin_user_dict[room_topic]:
            is_changed = True
            _admin_user_dict[room_topic].append(person.contact_id)
        failed_list.append(person.name)
    if failed_list:
        await room.say(f"添加{' '.join(failed_list)}管理员身份失败")
    await room.say(f"操作完成")
    if is_changed:
        _update_room_admin_json()


@sv.on_full_match("删除管理员", only_to_me=True)
async def del_admin(event: "Message", msg: str):
    room = event.room()
    if room is None:
        await event.talker().say("请在群聊内使用该命令")
        return
    # user_priv = await get_user_priv(event)
    # if not check_priv(user_priv, priv.OWNER):
    #     await event.room().say(f"权限不足, 修改所需要的权限为{priv.OWNER}, 而您的权限为{user_priv}")
    #     return
    mention_list = set(await event.mention_list())
    if not mention_list:
        await event.room().say("请@要添加的人")
        return
    is_changed = False  # 记录本次更改是否改变了管理员的设置的flag
    room_topic: str = await room.topic()
    failed_list = []
    for person in mention_list:  # todo 暂时还是使用群聊名做记录吧, 还是担心id可能会变
        if person.contact_id in _admin_user_dict[room_topic]:
            is_changed = True
            _admin_user_dict[room_topic].remove(person.contact_id)
            continue
        failed_list.append(person.name)
    if failed_list:
        await room.say(f"取消{' '.join(failed_list)}管理员身份失败")
    await room.say(f"操作完成")
    if is_changed:
        _update_room_admin_json()


@on_command("管理员列表", only_to_me=True)
async def admin_list(event: "Message", msg: str):
    room = event.room()
    if room is None:
        await event.talker().say("请在群聊内使用该命令")
        return
    room_admin_list = _admin_user_dict[await room.topic()]
    # for contact_id in room_admin_list:
    #     await room.find(RoomMemberQueryFilter())
    await room.say("本群Bot管理员为\n" + "\n".join(room_admin_list))
import os
from typing import Dict, List
from wechaty import Room, Message, Contact

import salt
from salt import on_command, config
from salt.priv import check_priv, get_user_priv
# from collections import defaultdict
import salt.priv as priv
from salt.priv import _admin_user_dict
from salt.service import Service
from wechaty_puppet import ContactQueryFilter, RoomMemberQueryFilter

try:
    import ujson as json
except ImportError:
    import json

sv = Service("__room__manage__", enable_on_default=True, visible=False,
             user_priv=priv.OWNER, manage_priv=priv.SUPERUSER)

# _admin_user_dict: Dict[str, List[str]] = defaultdict(list)
_config_dir = os.path.expanduser(f'{config.CONFIG_DIR}/room_config/'
                                 if config.CONFIG_DIR is not None else
                                 "~/.SaltBot/room_config/")
os.makedirs(_config_dir, exist_ok=True)
config_path = os.path.join(_config_dir, f'room_config.json')


def _update_room_admin_json():
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({
            room_name: _admin_user_dict[room_name]
            for room_name in _admin_user_dict
        },
            f,
            indent=2,
            ensure_ascii=False)


def _read_config_from_json() -> dict:
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        salt.logger.error(e)
        return {}


def init_modules():
    _admin_user_dict.clear()
    _admin_user_dict.update(_read_config_from_json())  # 初始化加载存到config里面的管理员


init_modules()


@sv.on_prefix("添加管理员", only_to_me=True)
async def add_admin(event: "Message", msg: str):
    room = event.room()
    if room is None:
        await event.talker().say("请在群聊内使用该命令")
        return

    # user_priv = await get_user_priv(event)
    # if not check_priv(user_priv, priv.OWNER):
    #     await event.room().say(f"权限不足, 修改所需要的权限为{priv.OWNER}, 而您的权限为{user_priv}")
    #     return
    mention_list = set(await event.mention_list())
    if not mention_list:
        await event.room().say("请@要添加的人")
        return
    is_changed = False  # 记录本次更改是否改变了管理员的设置的flag
    room_topic: str = await room.topic()
    failed_list = []
    for person in mention_list:  # todo 暂时还是使用群聊名做记录吧, 还是担心id可能会变
        if person.contact_id not in _admin_user_dict[room_topic]:
            is_changed = True
            _admin_user_dict[room_topic].append(person.contact_id)
        failed_list.append(person.name)
    if failed_list:
        await room.say(f"添加{' '.join(failed_list)}管理员身份失败")
    await room.say(f"操作完成")
    if is_changed:
        _update_room_admin_json()


@sv.on_full_match("删除管理员", only_to_me=True)
async def del_admin(event: "Message", msg: str):
    room = event.room()
    if room is None:
        await event.talker().say("请在群聊内使用该命令")
        return
    # user_priv = await get_user_priv(event)
    # if not check_priv(user_priv, priv.OWNER):
    #     await event.room().say(f"权限不足, 修改所需要的权限为{priv.OWNER}, 而您的权限为{user_priv}")
    #     return
    mention_list = set(await event.mention_list())
    if not mention_list:
        await event.room().say("请@要添加的人")
        return
    is_changed = False  # 记录本次更改是否改变了管理员的设置的flag
    room_topic: str = await room.topic()
    failed_list = []
    for person in mention_list:  # todo 暂时还是使用群聊名做记录吧, 还是担心id可能会变
        if person.contact_id in _admin_user_dict[room_topic]:
            is_changed = True
            _admin_user_dict[room_topic].remove(person.contact_id)
            continue
        failed_list.append(person.name)
    if failed_list:
        await room.say(f"取消{' '.join(failed_list)}管理员身份失败")
    await room.say(f"操作完成")
    if is_changed:
        _update_room_admin_json()


@on_command("管理员列表", only_to_me=True)
async def admin_list(event: "Message", msg: str):
    room = event.room()
    if room is None:
        await event.talker().say("请在群聊内使用该命令")
        return
    room_admin_list = _admin_user_dict[await room.topic()]
    # for contact_id in room_admin_list:
    #     await room.find(RoomMemberQueryFilter())
    await room.say("本群Bot管理员为\n" + "\n".join(room_admin_list))
