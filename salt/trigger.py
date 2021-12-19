"""
此处的想法是做一个触发器, 每个function的触发词都要通过装饰器放到里面去注册, 然后打包为一个对象放入触发器列表中,
在 wechaty on_message的时候去触发这个触发器, 从而实现模块可拔插
"""
from typing import Dict, List
import re
import salt
from salt.service import ServiceFunc


class Trigger:
    def add(self, prefix: str, func: "ServiceFunc"):
        raise NotImplementedError

    def search_handler(self, msg: str) -> List["ServiceFunc"]:
        raise NotImplementedError


# 前缀匹配触发器
class PrefixTrigger(Trigger):
    def __init__(self):
        self.key_dict: Dict[str, List["ServiceFunc"]] = {}

    def add(self, prefix: str, func: "ServiceFunc"):
        """
        { 触发词(str) : [ 服务对象 ] }的结构
        每个触发词对应的列表中正常只含有一个func -> 走else分支
        当触发词注册了多个func的时候log进行警告

        :param prefix:
        :param func:
        :return:
        """
        if prefix in self.key_dict:
            self.key_dict[prefix].append(func)
            salt.logger.warning(
                f"Prefix trigger `{prefix}` added multiple handlers: {func.__name__}@{func.service.name}")
        else:
            self.key_dict[prefix] = [func]
            salt.logger.debug(f"Succeed to add prefix trigger `{prefix}`")

    def search_handler(self, msg: str) -> List["ServiceFunc"]:
        ret = []  # todo 需要添加细节
        for k, v in self.key_dict.items():
            if msg.startswith(k):
                ret.extend(v)
        return ret


# 全部匹配触发器
class FullTrigger(Trigger):
    def __init__(self):
        self.key_dict: Dict[str, List["ServiceFunc"]] = {}

    def add(self, prefix: str, func: "ServiceFunc"):
        if prefix in self.key_dict:
            self.key_dict[prefix].append(func)
            salt.logger.warning(
                f"Full match trigger `{prefix}` added multiple handlers: {func.__name__}@{func.service.name}")
        else:
            self.key_dict[prefix] = [func]
            salt.logger.debug(f"Succeed to add full match trigger `{prefix}` to {func.__name__}@{func.service.name}")

    def search_handler(self, msg: str) -> List["ServiceFunc"]:
        ret = []
        if msg in self.key_dict:
            ret.extend(self.key_dict[msg])
        return ret


# 正则匹配触发器
class RegexTrigger(Trigger):
    def __init__(self):
        self.key_dict: Dict[re.Pattern, List["ServiceFunc"]] = {}

    def add(self, prefix: "re.Pattern", func: "ServiceFunc"):
        """

        :param prefix:
        :param func:
        :return:
        """
        if prefix in self.key_dict:
            self.key_dict[prefix].append(func)
            salt.logger.warning(
                f"Regex trigger `{prefix}` added multiple handlers: {func.__name__}@{func.service.name}")
        else:
            self.key_dict[prefix] = [func]
            salt.logger.debug(f"Succeed to add regex trigger `{prefix}` to {func.__name__}@{func.service.name}")
        """
        这种方式好像可以判断是否重复, 或者是因为缓存的问题? 存疑
        >>> import re
        >>> a = re.compile("ab")
        >>> b = re.compile("ab")
        >>> l = [a]
        >>> print(b in l)
        """

    def search_handler(self, msg: str) -> List["ServiceFunc"]:
        ret = []
        for reg in self.key_dict:
            if re.match(reg, msg):
                ret.extend(self.key_dict[reg])
        return ret


# 关键词匹配触发器
class KeywordTrigger(Trigger):
    def __init__(self):
        self.key_dict: Dict[str, List["ServiceFunc"]] = {}

    def add(self, prefix: str, func: "ServiceFunc"):
        if prefix in self.key_dict:
            self.key_dict[prefix].append(func)
            salt.logger.warning(
                f"Keyword trigger `{prefix}` added multiple handlers: {func.__name__}@{func.service.name}")
        else:
            self.key_dict[prefix] = [func]
            salt.logger.debug(f"Succeed to add keyword trigger `{prefix}` to {func.__name__}@{func.service.name}")

    def search_handler(self, msg: str) -> List["ServiceFunc"]:
        ret = []
        for keyword in self.key_dict:
            if keyword in msg:
                ret.extend(self.key_dict[keyword])
        return ret


fullTrigger = FullTrigger()
prefixTrigger = PrefixTrigger()
regexTrigger = RegexTrigger()
keywordTrigger = KeywordTrigger()

handle_list: List["Trigger"] = [fullTrigger, prefixTrigger, regexTrigger, keywordTrigger]
