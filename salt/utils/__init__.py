# !/usr/bin/env python
# -*-coding:utf-8 -*-
import os
from wechaty import Room, Contact
from typing import Union
from salt.utils.text_filter.filter import DFAFilter

dfa_filter = DFAFilter()


def init_utils():
    # 初始化dfa敏感词查找树
    dfa_filter.parse(os.path.join(os.path.dirname(__file__), 'text_filter/sensitive_words.txt'))


async def safety_say(conversation: Union["Room", "Contact"], message: str,
                     advance_mode: bool = False, repl="*"):
    """
    该函数会通过敏感词筛选模块对需要发送的消息进行筛选, 将敏感词替换
    :param repl: 敏感词被替换的字符, 注意该字符只能长度为1,否则结果会发生错误
    :param conversation: 需要发送的群聊或者人
    :param message: 需要进行筛选的消息
    :param advance_mode: 是否使用增强模式, 无视敏感词之间的特殊字符
    :return: None
    """
    if advance_mode:
        await conversation.say(dfa_filter.adv_filter(message, repl=repl))
    else:
        await conversation.say(dfa_filter.filter(message, repl=repl))

