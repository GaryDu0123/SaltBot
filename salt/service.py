from functools import wraps
from typing import Union, Dict, Callable
from wechaty import Room, Contact
import re

from salt import trigger, log, config

_loaded_service: Dict[str, "Service"] = {}


class ServiceFunc:
    def __init__(self, service: "Service", only_to_me: bool, func: Callable):
        self.func = func
        self.service = service
        self.only_to_me = only_to_me
        self.__name__ = func.__name__


class Service:
    def __init__(self, name: str):
        self.name = name
        self.logger = log.new_logger(name, config.DEBUG)
        assert self.name not in _loaded_service  # 重复注册服务名, 直接break掉
        _loaded_service[self.name] = self
        # init的时候要将该对象添加到bot处理部分, 从而显示bot状态

    @staticmethod
    def get_loaded_services() -> Dict[str, "Service"]:
        return _loaded_service

    @DeprecationWarning  # 待定
    def on_message(self):
        """
        自由触发, 但是理论上要实现的功能和full_match一致, 感觉没必要实现
        :return:
        """
        pass

    def on_prefix(self, *word, only_to_me=False):
        """
        前缀触发器
        :param word: 触发词
        :param only_to_me: 是不是比如叫我才触发(还没想好怎么实现
        :return: None
        """

        def registrar(func):
            @wraps(func)
            async def wrapper(conversation: Union[Room, Contact], msg: str):
                # 此处可以加日志记录或者判断
                return await func(conversation, msg)

            # 在此处执行function(service)注册
            sf = ServiceFunc(self, False, func)
            for w in word:
                if isinstance(w, str):
                    trigger.prefixTrigger.add(w, sf)
                    self.logger.info(f"Success bind prefix trigger function {sf.__name__} to keyword {w} @{self.name}")
                else:
                    self.logger.error(f'Failed to add prefix trigger `{w}`, expecting `str` but `{type(w)}` given!')
            return wrapper

        return registrar

    def on_regex(self, *regex: Union[str, re.Pattern], only_to_me=False):
        def registrar(func):
            @wraps(func)
            async def wrapper(conversation: Union[Room, Contact], msg: str):
                return await func(conversation, msg)

            sf = ServiceFunc(self, False, func)
            for r in regex:
                if isinstance(r, str):
                    r_rex: "re.Pattern" = re.compile(r)
                    trigger.regexTrigger.add(r_rex, sf)
                    self.logger.debug(f"Success bind regex match trigger {sf.__name__} to keyword {r_rex} @{self.name}")
                elif isinstance(r, re.Pattern):
                    trigger.regexTrigger.add(r, sf)
                    self.logger.debug(f"Success bind regex match trigger {sf.__name__} to keyword {r} @{self.name}")
                else:
                    self.logger.error(f'Failed to add full match trigger `{r}`, expecting `str` or `re.Pattern` but `{type(r)}` given!')
            return wrapper
        return registrar

    def on_full_match(self, *word):
        def registrar(func):
            @wraps(func)
            async def wrapper(conversation: Union[Room, Contact], msg: str):
                # 此处可以加日志记录或者判断
                return await func(conversation, msg)

            # 在此处执行function(service)注册
            sf = ServiceFunc(self, False, func)
            for w in word:
                if isinstance(w, str):
                    trigger.fullTrigger.add(w, sf)
                    self.logger.debug(f"Success bind full match trigger {sf.__name__} to keyword {w} @{self.name}")
                else:
                    self.logger.error(f'Failed to add full match trigger `{w}`, expecting `str` but `{type(w)}` given!')
            return wrapper

        return registrar

    def on_keyword(self, *word):
        def registrar(func):
            async def wrapper(conversation: Union[Room, Contact], msg: str):
                # 此处可以加日志记录或者判断
                return await func(conversation, msg)
                # 在此处执行function(service)注册
            sf = ServiceFunc(self, False, func)
            for w in word:
                if isinstance(w, str):
                    trigger.keywordTrigger.add(w, sf)
                    self.logger.debug(f"Success bind keyword trigger {sf.__name__} to keyword {w} @{self.name}")
                else:
                    self.logger.error(
                        f'Failed to add keyword trigger `{w}`, expecting `str` but `{type(w)}` given!')
            return wrapper
        return registrar
