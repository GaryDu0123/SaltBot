import salt
import os
import re
from functools import wraps
from typing import Union, Dict, Callable, Set
from wechaty import Room, Contact
from salt import priv
from salt import trigger, log, config

try:
    import ujson as json
except ImportError:
    import json

_loaded_service: Dict[str, "Service"] = {}
_config_dir = os.path.expanduser(f'{config.CONFIG_DIR}/service_config/'
                                 if config.CONFIG_DIR is not None else
                                 "~/.SaltBot/service_config/")

os.makedirs(_config_dir, exist_ok=True)


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
                 name: str,
                 enable_on_default: bool = False,
                 visible: bool = True,
                 user_priv: int = priv.NORMAL,
                 manage_priv: int = priv.ADMIN
                 ):
        self.name = name
        self.logger = log.new_logger(name, config.DEBUG)

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
        self.disabled_room.discard(room.room_id)
        self.enabled_room.add(room.room_id)
        _save_service_config(self)
        self.logger.info(f"Service {self.name} is enabled in Room {await room.topic()}")

    async def disable_service(self, room: "Room"):
        self.enabled_room.discard(room.room_id)
        self.disabled_room.add(room.room_id)
        _save_service_config(self)
        self.logger.info(f"Service {self.name} is disabled in Room {await room.topic()}")

    def check_service_enable(self, room_id: str) -> bool:  # todo
        """
        返回true如果服务开启, false如果服务关闭
        :param room_id: 群聊号码
        :return: 布尔值
        """
        return (room_id in self.enabled_room) or (self.enable_on_default and room_id not in self.disabled_room)

    @staticmethod
    def get_all_services_status(room_id: str) -> Dict[str, bool]:
        ret: Dict[str, bool] = {}
        for service in _loaded_service.values():
            ret[service.name] = service.check_service_enable(room_id)
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
            async def wrapper(conversation: Union[Room, Contact], msg: str):
                # 此处可以加日志记录或者判断
                return await func(conversation, msg)

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
            async def wrapper(conversation: Union[Room, Contact], msg: str):
                return await func(conversation, msg)

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
            async def wrapper(conversation: Union[Room, Contact], msg: str):
                # 此处可以加日志记录或者判断
                return await func(conversation, msg)

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
            async def wrapper(conversation: Union[Room, Contact], msg: str):
                # 此处可以加日志记录或者判断
                return await func(conversation, msg)
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
