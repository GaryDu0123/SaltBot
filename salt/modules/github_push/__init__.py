import asyncio
import os
import re
import aiohttp
from collections import defaultdict
from wechaty import Room, Message
from typing import List, Dict
from salt import config
from salt.service import Service, SchedulerTrigger

try:
    import ujson as json
except ImportError:
    import json

sv = Service("Github推送", enable_on_default=False)

_config_dir_git = os.path.expanduser(f'{config.CONFIG_DIR}/github_push_config/'
                                     if config.CONFIG_DIR is not None else
                                     "~/.SaltBot/github_push_config/")
config_path = os.path.join(_config_dir_git, f'github_push_config.json')
os.makedirs(_config_dir_git, exist_ok=True)


class GithubConfig:
    def __init__(self, rep_name, service_room: str, token: str = None, enable: bool = True, last_sha: str = None):
        self.rep_name = rep_name
        self.service_room = service_room
        self.token = token
        self.enable = enable
        self.last_sha = last_sha


github_config_list: Dict[str, List[GithubConfig]] = defaultdict(list)


def _load_from_file():
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            json_config = json.load(f)
            for item in json_config:
                try:
                    github_config_list[item["service_room"]].append(
                        GithubConfig(item["rep_name"], item["service_room"], item["token"], item["enable"],
                                     item["last_sha"]))
                except Exception as e:
                    sv.logger.warning(f"Error {e} occur when loading config {str(item)}")
    except FileNotFoundError as e:
        sv.logger.info(f"Not found the config file of {sv.name}")
    except Exception as e:
        sv.logger.warning(f"Error {e} occur when loading config file @{sv.name}")


_load_from_file()  # 配置文件的内容只在初始化的时候读取


def _save_to_file():
    """
    保存当前列表状态到config文档
    :return:
    """
    temp = []
    for service_room in github_config_list:
        for obj in github_config_list[service_room]:
            temp.append({
                "rep_name": obj.rep_name,
                "service_room": obj.service_room,
                "token": obj.token,
                "enable": obj.enable,
                "last_sha": obj.last_sha
            })
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(temp, f, indent=2, ensure_ascii=False)


async def github_request(obj: "GithubConfig"):
    try:
        async with aiohttp.request("GET",
                                   headers=({"Authorization": f"bearer {obj.token}"} if obj.token is not None else {}),
                                   url=f"https://api.github.com/repos/{obj.rep_name}/commits") as request:
            j = await request.json()
            return {
                "sha": j[0]['sha'],
                "author": j[0]["commit"]['author'],
                "message": j[0]["commit"]['message'],
                "rep_name": obj.rep_name,
                "service_room": obj.service_room
            }
    except Exception as e:
        sv.logger.warning(f'{e} occur when process the request to {obj.rep_name} services for {obj.service_room}')
        return {}


# todo bug不能检查仓库名是否重复

@sv.on_scheduler(SchedulerTrigger.IntervalTrigger, seconds=60)
async def github_push():
    from salt import salt_bot
    is_changed = False  # 检测到有仓库更新后, 要求重新写入文件的标志
    task = []
    for service_room in github_config_list:
        if await sv.check_service_enable(service_room):  # 检查是否开启服务
            for obj in github_config_list[service_room]:
                if obj.enable:  # 检查是否开启此条配置的推送
                    task.append(asyncio.create_task(github_request(obj)))
    if len(task) == 0:
        return  # 如果日程为0的话直接返回, 防止ValueError: Set of coroutines/Futures is empty.
    done, _ = await asyncio.wait(task, timeout=None)
    for d in done:
        respond = d.result()
        if len(respond) == 0:
            continue

        for service_room in github_config_list:
            # 如果对象的服务房间与追溯的仓库名一致, 说明是正确的对象
            if service_room == respond["service_room"]:
                for config_obj in github_config_list[service_room]:
                    if config_obj.rep_name == respond["rep_name"]:
                        if config_obj.last_sha == respond["sha"]:  # 如果本次的sha值与原来的值一致, 说明没有更新, 断掉循环执行下个发送
                            break
                        # 不等于sha的时候表示仓库更新了
                        is_changed = True  # 改变flag, 准备让后面重新写入
                        room = await salt_bot.Room.find(respond["service_room"])  # 获取room名字
                        if room is None:  # 如果获取不到房间
                            sv.logger.warning(f"Cannot get room {config_obj.service_room}, skipped")
                            continue
                        # await room.ready()  # 根据规定, 要求自动发送的时候要等待ready
                        await room.say(f"检测到{respond['rep_name']}仓库更新\n"
                                       f"提交者: {respond['author']['name']}\n"
                                       f"日期: {respond['author']['date']}\n"
                                       f"提交信息: {respond['message']}"
                                       )
                        config_obj.last_sha = respond["sha"]  # 更新记录的sha值
                        break  # 执行完毕准备执行下一个
            # todo done?
    if is_changed:
        _save_to_file()


# hard coding 了一下, 不打算改了

@sv.on_regex(re.compile("^github推送 *添加 *.*$", re.I))
async def github_set_up(event: "Message", msg: str):
    room: "Room" = event.room()
    room_name = await room.topic()
    message = re.match(re.compile("^github推送 *添加 *(?P<message>.*)$", re.I), msg).group("message").strip()

    if message == "":
        await room.say("添加推送请以[github推送 添加 账户名 仓库名 TOKEN]的形式发送, 中间以空格隔开")
        return
    match = re.match(r"^(?P<profile>\w+) +(?P<repo_name>\w+) *(?P<token>\w+)?$", message)
    if match is None:
        await room.say("格式不合法, 请重新添加")
        return
    config_file: dict = match.groupdict()
    config_obj = GithubConfig(f"{config_file['profile']}/{config_file['repo_name']}",
                              room_name,
                              config_file['token'])
    if len(await github_request(config_obj)) == 0:
        sv.logger.info(f"{room_name} attempt to add configuration failed")
        await room.say("添加失败, 配置不合法或者仓库提交为空")
        return
    for c in github_config_list[room_name]:
        if c.rep_name == config_obj.rep_name:  # 检查是不是已经有该监测的仓库
            c.token = config_obj.token  # 仓库有可能是token过期重新添加, 直接更新token
            await room.say("监测的仓库已经存在, 已成功更新token")
            _save_to_file()
            return
    github_config_list[room_name].append(config_obj)
    _save_to_file()
    await room.say("添加成功")


@sv.on_regex(re.compile("^github推送 *删除 *.*$", re.I))
async def github_delete_config(event: "Message", msg: str):
    room: "Room" = event.room()
    room_name = await room.topic()
    message = re.match(re.compile("^github推送 *删除 *(?P<message>.*)$", re.I), msg).group("message").strip()
    if message == "":
        await room.say("删除推送设置请以[github推送 删除 账户名 仓库名]的形式发送, 中间以空格隔开")
        return
    match = re.match(r"^(?P<profile>\w+) +(?P<repo_name>\w+)$", message)
    if match is None:
        await room.say("格式不合法, 请重新发送")
        return
    config_file: dict = match.groupdict()
    if room_name in github_config_list:
        for config_obj in github_config_list[room_name]:
            if config_obj.rep_name.lower() == f"{config_file['profile']}/{config_file['repo_name']}".lower():
                github_config_list[room_name].remove(config_obj)
                await room.say(f"已成功删除{config_obj.rep_name}")
                sv.logger.info(f"{room_name} remove {config_obj.rep_name} push successfully")
                _save_to_file()
                return
    await room.say(f"未找到{config_file['profile']}/{config_file['repo_name']}")
    sv.logger.info(f"{room_name} remove {config_file['profile']}/{config_file['repo_name']} failed")


@sv.on_regex(re.compile("^github推送 *(列表|all) *$", re.I))
async def github_list_all(event: "Message", msg: str):
    room: "Room" = event.room()
    room_name = await room.topic()
    if room_name in github_config_list:
        temp = [
            f"|{'○' if config_obj.enable else '×'}| {config_obj.rep_name}"
            for config_obj in github_config_list[room_name]
        ]
        await room.say("\n".join(temp))
        return
    await room.say("未找到相关配置, 请再次添加或者联系Bot维护者")


@sv.on_regex(re.compile("^github推送 *(开启|关闭) *.*$", re.I))
async def github_open_close(event: "Message", msg: str):
    room: "Room" = event.room()
    room_name = await room.topic()
    message = re.match(re.compile("^github推送 *(?P<status>(开启|关闭)) *(?P<message>.*)$", re.I), msg)
    status = message.group("status")
    message_config = message.group("message").strip()
    if message == "":
        await room.say("开启关闭推送请以[github推送 开启|关闭 账户名 仓库名]的形式发送, 中间以空格隔开")
        return
    match = re.match(r"^(?P<profile>\w+) +(?P<repo_name>\w+)$", message_config)
    if match is None:
        await room.say("格式不合法, 请重新发送")
        return
    config_file: dict = match.groupdict()
    if room_name in github_config_list:
        for config_obj in github_config_list[room_name]:
            if config_obj.rep_name.lower() == f"{config_file['profile']}/{config_file['repo_name']}".lower():
                if status == "开启":
                    config_obj.enable = True
                elif status == "关闭":
                    config_obj.enable = False
                else:
                    sv.logger.error(f"Unknown status {status}")
                    await room.say(f"未知错误, 出现了不应该出现的{status}, 请联系维护组")
                    return
                _save_to_file()
                await room.say(f"已成功{status} {config_obj.rep_name}")
                return
    await room.say(f"未找到{config_file['profile']}/{config_file['repo_name']}")
    sv.logger.info(f"{room_name} remove {config_file['profile']}/{config_file['repo_name']} failed")

# class GithubConfig:
#     def __init__(self, token: str = None, enable: bool = True, last_sha: str = None):
#         # self.rep_name = rep_name
#         # self.service_room = service_room
#         self.token = token
#         self.enable = enable
#         self.last_sha = None
#
#
# def default_dict_dict():
#     return defaultdict(GithubConfig)
#
#
# # 这个的结构是
# # {
# #   "仓库名1": GithubConfig对象1,
# #   "仓库名2": GithubConfig对象2,
# # }
# github_config_list: Dict[str, Dict[str, "GithubConfig"]] = defaultdict(default_dict_dict)
#
#
# # JSON保持这样的一个格式，方便数据多的时候进行查询
# # {
# #   "群聊名": {
# #     "仓库名1": {
# #       "token": "",
# #       "enable": true,
# #       "last_sha": ""
# #     },
# #     "仓库名2": {
# #       "token": "",
# #       "enable": true,
# #       "last_sha": ""
# #     }
# #   }
# # }
#
# def _load_from_file():
#     try:
#         with open(config_path, "r", encoding="utf-8") as f:
#             json_config = json.load(f)
#             for room_name in json_config:
#                 for rep_name in json_config[room_name]:
#                     try:
#                         config_obj = GithubConfig(
#                             json_config[room_name][rep_name]["token"],
#                             json_config[room_name][rep_name]["enable"],
#                             json_config[room_name][rep_name]["last_sha"]
#                         )
#                         github_config_list[room_name][rep_name] = config_obj
#                     except Exception as e:
#                         sv.logger.warning(f"Error {e} occur when loading config of {rep_name} in {room_name}")
#     except FileNotFoundError:
#         sv.logger.info(f"Not found the config file of {sv.__name__}")
#     except Exception as e:
#         sv.logger.warning(f"Error {e} occur when loading config file @{sv.__name__}")
#
#
# _load_from_file()  # 配置文件的内容只在初始化的时候读取
#
#
# def _save_to_file():
#     """
#     保存当前列表状态到config文档
#     :return:
#     """
#     temp = {
#         {
#             {
#                 "token": github_config_list[room_name][rep_name].token,
#                 "enable": github_config_list[room_name][rep_name].enable,
#                 "last_sha": github_config_list[room_name][rep_name].last_sha
#             }
#             for rep_name in github_config_list[room_name]
#         }
#         for room_name in github_config_list
#     }
#     with open(config_path, "w", encoding="utf-8") as f:
#         json.dump(temp, f, indent=2, ensure_ascii=False)
#
#
# async def github_request(obj: "GithubConfig", rep_name: str, service_room: str):
#     try:
#         async with aiohttp.request("GET",
#                                    headers={"Authorization": obj.token},
#                                    url=f"https://api.github.com/repos/{rep_name}/commits") as request:
#             j = await request.json()
#             return {
#                 "sha": j[0]['sha'],
#                 "author": j[0]["commit"]['author'],
#                 "message": j[0]["commit"]['message'],
#                 "rep_name": rep_name,
#                 "service_room": service_room
#             }
#     except Exception as e:
#         sv.logger.warning(f'{e} occur when process the request to {rep_name} services for {service_room}')
#         return {}
#
#
# #
#
# @sv.on_scheduler(SchedulerTrigger.IntervalTrigger, seconds=60)
# async def github_push():
#     from salt import salt_bot
#     is_changed = False  # 检测到有仓库更新后, 要求重新写入文件的标志
#     task = []
#     for room in github_config_list:
#         for rep_name in github_config_list[room]:
#             task.append(asyncio.create_task(github_request(github_config_list[room][rep_name],
#                                                            rep_name,
#                                                            room)))
#     done, _ = await asyncio.wait(task, timeout=None)
#     for d in done:
#         respond = d.result()
#         if len(respond) == 0:
#             continue
#         for room_name in github_config_list:
#             # 如果对象的服务房间与追溯的仓库名一致, 说明是正确的对象
#             if room_name == respond["service_room"]:
#                 for rep_name in github_config_list[room_name]:
#                     if rep_name == respond["rep_name"]:
#                         config_obj = github_config_list[room_name][rep_name]
#                         if config_obj.last_sha == respond["sha"]:  # 如果本次的sha值与原来的值一致, 说明没有更新, 断掉循环执行下个发送
#                             break
#                         # 不等于sha的时候表示仓库更新了
#                         is_changed = True  # 改变flag, 准备让后面重新写入
#
#                         room = await salt_bot.Room.find(respond["service_room"])  # 获取room名字
#                         if room is None:  # 如果获取不到房间
#                             sv.logger.warning(f"Cannot get room {room_name}, skipped")
#                             continue
#                         # await room.ready()  # 根据规定, 要求自动发送的时候要等待ready
#                         await room.say(f"检测到{rep_name}仓库更新\n"
#                                        f"提交者: {respond['author']['name']}\n"
#                                        f"日期: {respond['author']['date']}\n"
#                                        f"提交信息: {respond['message']}"
#                                        )
#                         config_obj.last_sha = respond["sha"]  # 更新记录的sha值
#                         break  # 执行完毕准备执行下一个
#     if is_changed:
#         _save_to_file()
#
#     # for obj in github_config_list:
#     #     room = await salt_bot.Room.find(obj.service_room)
#     #     if room is None:  # 如果获取不到房间
#     #         sv.logger.warning(f"Cannot get room {obj.service_room}, skipped")
#     #         continue
#     #
#     #
#     #     sha = None
#     #     if obj.last_sha != sha:
#     #         obj.last_sha = sha
#     #         return
#     #     print("一样的")
#
#
# @sv.on_regex(re.compile("^github推送 *.*", re.I))
# async def github_set_up(event: "Message", msg: str):
#     conversation: "Room" = event.room()
#     message = re.match(re.compile("^github推送 *(?P<message>.*)", re.I), msg).group("message").strip()
#
#     if message == "":
#         await conversation.say("添加推送请以[github推送 仓库名 TOKEN]的形式发送")
