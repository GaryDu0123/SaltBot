import salt
import os
import re
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from functools import wraps
from typing import Union, Dict, Callable, Set
from wechaty import Room, Contact, Message
from salt import priv
from salt import trigger, log, config
from .priv import check_is_block_room, check_is_block_user, get_user_priv, check_priv

try:
    import ujson as json
except ImportError:
    import json

_loaded_service: Dict[str, "Service"] = {}
_config_dir = os.path.expanduser(f'{config.CONFIG_DIR}/service_config/'
                                 if config.CONFIG_DIR is not None else
                                 "~/.SaltBot/service_config/")

os.makedirs(_config_dir, exist_ok=True)


class Scheduler(AsyncIOScheduler):
    pass


scheduler = Scheduler()  # timezone='Asia/Shanghai'
scheduler.configure({'apscheduler.timezone': 'Asia/Shanghai'})


class SchedulerTrigger:
    DateTrigger = "date"
    IntervalTrigger = "interval"
    CronTrigger = "cron"


def _load_service_config(sv_name: str):
    config_path = os.path.join(_config_dir, f'{sv_name}.json')
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        salt.logger.error(e)
        return {}


def _save_service_config(sv: "Service"):
    config_path = os.path.join(_config_dir, f'{sv.name}.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(
            {
                "name": sv.name,
                "use_priv": sv.user_priv,
                "manage_priv": sv.manage_priv,
                "enable_on_default": sv.enable_on_default,
                "visible": sv.visible,
                "enable_group": list(sv.enabled_room),
                "disable_group": list(sv.disabled_room)
            },
            f,
            ensure_ascii=False,
            indent=4
        )


class ServiceFunc:
    def __init__(self, service: "Service", only_to_me: bool, func: Callable):
        self.func = func
        self.service = service
        self.only_to_me = only_to_me
        self.__name__ = func.__name__


class Service:
    def __init__(self,
                 name: str,  # 服务名
                 enable_on_default: bool = False,  # 是否默认开启
                 visible: bool = True,  # 是否可见(系统级)
                 user_priv: int = priv.NORMAL,  # 用户使用权限
                 manage_priv: int = priv.ADMIN,  # 管理权限
                 _help: str = ""  # 帮助文档
                 ):
        self.name = name
        self.logger = log.new_logger(name, config.DEBUG)
        self.help = _help

        if self.name in _loaded_service:
            self.logger.critical(f"Duplicate service naming => {self.name}")
            assert self.name not in _loaded_service, f'Service name "{self.name}" already exist!'  # 重复注册服务名, 直接break掉

        self.enable_on_default = enable_on_default
        self.visible = visible
        self.user_priv = user_priv
        self.manage_priv = manage_priv
        config_file = _load_service_config(self.name)
        self.enabled_room: Set[str] = set(config_file.get('enable_group', []))
        self.disabled_room: Set[str] = set(config_file.get('disable_group', []))
        # init的时候要将该对象添加到bot处理部分, 从而显示bot服务状态
        _loaded_service[self.name] = self

    @staticmethod
    def get_loaded_services() -> Dict[str, "Service"]:
        return _loaded_service

    async def enable_service(self, room: "Room"):
        room_name = await room.topic()
        self.disabled_room.discard(room_name)
        self.enabled_room.add(room_name)
        _save_service_config(self)
        self.logger.info(f"Service {self.name} is enabled in Room {room_name}")

    async def disable_service(self, room: "Room"):
        room_name = await room.topic()
        self.enabled_room.discard(room_name)
        self.disabled_room.add(room_name)
        _save_service_config(self)
        self.logger.info(f"Service {self.name} is disabled in Room {room_name}")

    async def check_user_priv(self, event: "Message") -> bool:
        return check_priv(await get_user_priv(event), self.user_priv)

    async def check_admin_priv(self, event: "Message") -> bool:
        return check_priv(await get_user_priv(event), self.manage_priv)

    async def check_service_enable(self, event: Union["Message", str]) -> bool:  # todo
        """
        返回true如果服务开启, false如果服务关闭
        :param event:
        :return: 布尔值
        """
        if isinstance(event, Message):
            room_name = await event.room().topic()
        elif isinstance(event, str):
            room_name = event
        else:
            return False
        return (room_name in self.enabled_room) or (self.enable_on_default and room_name not in self.disabled_room)

    async def check_all_user_priv(self, event: "Message"):
        return await self.check_user_priv(event) and not check_is_block_user(event.talker()) and \
               not check_is_block_room(event.room()) and await self.check_service_enable(event)

    @staticmethod
    async def get_all_services_status(event: "Message", with_not_visible: bool = True) -> Dict[str, bool]:
        ret: Dict[str, bool] = {}
        for service in _loaded_service.values():
            if service.visible or with_not_visible:
                ret[service.name] = await service.check_service_enable(event)
        return ret

    def on_prefix(self, *word, only_to_me: bool = True):
        """
        前缀触发器
        :param word: 触发词
        :param only_to_me
        :return: None
        """

        def registrar(func):
            @wraps(func)
            async def wrapper(event: "Message", msg: str):
                # 此处可以加日志记录或者判断
                return await func(event, msg)

            # 在此处执行function(service)注册
            sf = ServiceFunc(self, only_to_me, func)
            for w in word:
                if isinstance(w, str):
                    trigger.prefixTrigger.add(w, sf)
                    self.logger.info(f"Success bind prefix trigger function {sf.__name__} to keyword {w} @{self.name}")
                else:
                    self.logger.error(f'Failed to add prefix trigger `{w}`, expecting `str` but `{type(w)}` given!')
            return wrapper

        return registrar

    def on_regex(self, *regex: Union[str, re.Pattern], only_to_me: bool = True):
        def registrar(func):
            @wraps(func)
            async def wrapper(event: "Message", msg: str):
                return await func(event, msg)

            sf = ServiceFunc(self, only_to_me, func)
            for r in regex:
                if isinstance(r, str):
                    r_rex: "re.Pattern" = re.compile(r)
                    trigger.regexTrigger.add(r_rex, sf)
                    self.logger.debug(f"Success bind regex match trigger {sf.__name__} to keyword {r_rex} @{self.name}")
                elif isinstance(r, re.Pattern):
                    trigger.regexTrigger.add(r, sf)
                    self.logger.debug(f"Success bind regex match trigger {sf.__name__} to keyword {r} @{self.name}")
                else:
                    self.logger.error(
                        f'Failed to add full match trigger `{r}`, expecting `str` or `re.Pattern` but `{type(r)}` given!')
            return wrapper

        return registrar

    def on_full_match(self, *word, only_to_me: bool = True):
        def registrar(func):
            @wraps(func)
            async def wrapper(event: "Message", msg: str):
                # 此处可以加日志记录或者判断
                return await func(event, msg)

            # 在此处执行function(service)注册
            sf = ServiceFunc(self, only_to_me, func)
            for w in word:
                if isinstance(w, str):
                    trigger.fullTrigger.add(w, sf)
                    self.logger.debug(f"Success bind full match trigger {sf.__name__} to keyword {w} @{self.name}")
                else:
                    self.logger.error(f'Failed to add full match trigger `{w}`, expecting `str` but `{type(w)}` given!')
            return wrapper

        return registrar

    def on_keyword(self, *word, only_to_me: bool = False):
        def registrar(func):
            @wraps(func)
            async def wrapper(event: "Message", msg: str):
                # 此处可以加日志记录或者判断
                return await func(event, msg)
                # 在此处执行function(service)注册

            sf = ServiceFunc(self, only_to_me, func)
            for w in word:
                if isinstance(w, str):
                    trigger.keywordTrigger.add(w, sf)
                    self.logger.debug(f"Success bind keyword trigger {sf.__name__} to keyword {w} @{self.name}")
                else:
                    self.logger.error(
                        f'Failed to add keyword trigger `{w}`, expecting `str` but `{type(w)}` given!')
            return wrapper

        return registrar

    def on_scheduler(self, *args, **kwargs):
        def registrar(func):
            @wraps(func)
            async def wrapper():
                # 此处可以加日志记录或者判断
                self.logger.info(f"Scheduler work {func.__name__} start")
                ret = await func()
                self.logger.info(f"Scheduler work {func.__name__} done")
                return ret

            # scheduler.add_job(wrapper, trigger_for_scheduler, args, kwargs, id, name, misfire_grace_time,
            #                   coalesce, max_instances, next_run_time, jobstore, executor, True, **trigger_args)
            scheduler.scheduled_job(*args, **kwargs)(wrapper)
            self.logger.info(f"Scheduler successful add job {func.__name__}")
            return wrapper

        return registrar
