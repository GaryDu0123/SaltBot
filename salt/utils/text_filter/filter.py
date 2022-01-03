#!/usr/bin/env python
# -*- coding:utf-8 -*-
# reference: https://github.com/observerss/textfilter

from collections import defaultdict
import re

__all__ = ['NaiveFilter', 'BSFilter', 'DFAFilter']
__author__ = 'observer'
__date__ = '2012.01.05'


class NaiveFilter():
    '''Filter Messages from keywords

    very simple filter implementation

    >>> f = NaiveFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keywords = set([])

    def parse(self, path):
        for keyword in open(path, encoding='utf8'):
            self.keywords.add(keyword.strip().decode('utf-8').lower())

    def filter(self, message, repl="*"):
        message = message.lower()
        for kw in self.keywords:
            message = message.replace(kw, repl)
        return message


class BSFilter:
    '''Filter Messages from keywords

    Use Back Sorted Mapping to reduce replacement times

    >>> f = BSFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keywords = []
        self.kwsets = set([])
        self.bsdict = defaultdict(set)
        self.pat_en = re.compile(r'^[0-9a-zA-Z]+$')  # english phrase or not

    def add(self, keyword):
        # if not isinstance(keyword, unicode):
        #     keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        if keyword not in self.kwsets:
            self.keywords.append(keyword)
            self.kwsets.add(keyword)
            index = len(self.keywords) - 1
            for word in keyword.split():
                if self.pat_en.search(word):
                    self.bsdict[word].add(index)
                else:
                    for char in word:
                        self.bsdict[char].add(index)

    def parse(self, path):
        with open(path, 'r', encoding='utf8') as f:
            for keyword in f:
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        # if not isinstance(message, unicode):
        #     message = message.decode('utf-8')
        message = message.lower()
        for word in message.split():
            if self.pat_en.search(word):
                for index in self.bsdict[word]:
                    message = message.replace(self.keywords[index], repl)
            else:
                for char in word:
                    for index in self.bsdict[char]:
                        message = message.replace(self.keywords[index], repl)
        return message


class DFAFilter:
    '''Filter Messages from keywords

    Use DFA to keep algorithm perform constantly

    >>> f = DFAFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'
        self.stop_list = [" "]

    def add(self, keyword):
        # if not isinstance(keyword, unicode):
        #     keyword = keyword.decode('utf-8')
        # keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, 'r', encoding='utf8') as f:
            for keyword in f:
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        assert len(repl) == 1, "Then length of replace word must be 1"
        # if not isinstance(message, unicode):
        #     message = message.decode('utf-8')
        # message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)

    def adv_filter(self, message, repl="*"):
        assert len(repl) == 1, "Then length of replace word must be 1"
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            test_word = set()
            for char in message[start:]:
                if char in self.stop_list:
                    test_word.add(step_ins)
                    step_ins += 1
                    continue
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret_text = [repl for _ in range(step_ins)]
                        for index in test_word:
                            ret_text[index] = message[index + start]
                        ret.append("".join(ret_text))
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1
        return ''.join(ret)


def test_first_character():
    gfw = DFAFilter()
    gfw.add("1989年")
    assert gfw.filter("1989", "*") == "1989"


if __name__ == "__main__":
    # gfw = NaiveFilter()
    # gfw = BSFilter()
    gfw = DFAFilter()
    gfw.parse("sensitive_words.txt")
    import time

    t = time.time()
    print(gfw.filter("法 轮 功 我操操操", "*"))
    print(gfw.adv_filter("法 轮功 我操操操", "*"))
    print()
    print(gfw.filter("针孔 摄像机 我操操操", "*"))
    print(gfw.adv_filter("针孔 摄像机 我操操操", "*"))
    print()
    print(gfw.filter("售假人 民币 我操操操", "*"))
    print(gfw.adv_filter("售假人 民币 我操操操", "*"))
    # print()
    print(gfw.filter("传世私 服 我操操操", "*"))
    print(gfw.adv_filter("传世私 服 我操操操", "*"))
    print("消耗时间" + str(time.time() - t))
    test_first_character()
