#!/usr/bin/env python
# -*-coding:utf-8 -*-
import html


parser_dict = {
    "<br/>": "\n"
}


def clean_text(message: str) -> str:
    for tag in parser_dict:
        message = message.replace(tag, parser_dict[tag])
    return html.unescape(message)


if __name__ == '__main__':
    print(clean_text("salt复读 a&lt;/br&gt;<br/>啊这"))