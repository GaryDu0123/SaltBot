#!/usr/bin/env python
# -*-coding:utf-8 -*-


from salt import Service
from wechaty import Message
import aiohttp
import re

from salt.config import GLOT_TOKEN

language_list = {
    'assembly': ['assembly', 'asm'],
    'ats': ['ats'],
    'bash': ['bash'],
    'c': ['c'],
    'clojure': ['clojure'],
    'cobol': ['cobol'],
    'coffeescript': ['coffeescript'],
    'cpp': ['cpp', 'c++'],
    'crystal': ['crystal'],
    'csharp': ['csharp', "c#"],
    'd': ['d'],
    'elixir': ['elixir'],
    'elm': ['elm'],
    'erlang': ['erlang'],
    'fsharp': ['fsharp'],
    'go': ['go'],
    'groovy': ['groovy'],
    'haskell': ['haskell'],
    'idris': ['idris'],
    'java': ['java'],
    'javascript': ['javascript', 'js'],
    'julia': ['julia'],
    'kotlin': ['kotlin'],
    'lua': ['lua'],
    'mercury': ['mercury'],
    'nim': ['nim'],
    'nix': ['nix'],
    'ocaml': ['ocaml'],
    'perl': ['perl'],
    'php': ['php'],
    'python': ['python', 'py', 'python3'],
    'raku': ['raku'],
    'ruby': ['ruby'],
    'rust': ['rust'],
    'scala': ['scala'],
    'swift': ['swift'],
    'typescript': ['typescript', 'ts']
}

suffix_list = {
    'assembly': "asm",
    'ats': "dats",
    'bash': "sh",
    'c': "c",
    'clojure': "clj",
    'cobol': "cob",
    'coffeescript': "coffee",
    'cpp': "cpp",
    'crystal': "cr",
    'csharp': "cs",
    'd': "d",
    'elixir': "ex",
    'elm': "elm",
    'erlang': "erl",
    'fsharp': "fs",
    'go': "go",
    'groovy': "groovy",
    'haskell': "hs",
    'idris': "idr",
    'java': "java",
    'javascript': "js",
    'julia': "jl",
    'kotlin': "kt",
    'lua': "lua",
    'mercury': "m",
    'nim': "nim",
    'nix': "nix",
    'ocaml': "ml",
    'perl': "pl",
    'php': "php",
    'python': "py",
    'raku': "raku",
    'ruby': "rb",
    'rust': "rs",
    'scala': "scala",
    'swift': "swift",
    'typescript': "ts"
}

search_dict = {}
for key, value in language_list.items():
    for alias in value:
        search_dict[alias] = key

sv = Service("CodeOnline", enable_on_default=True, _help="""


""")


@sv.on_prefix("运行", only_to_me=True)
async def run_code(event: "Message", msg: str):
    match_obj = re.match(r"^运行 *(?P<codeType>.+) *\n(?P<code>[\W\w]*)$", msg)
    code_type = match_obj.group("codeType").strip()
    code = match_obj.group("code").strip()
    if code_type not in search_dict:
        await event.room().say(f"找不到{code_type}, 请检查你的输入")
        return
    if len(code) == 0:
        await event.room().say(f"运行代码不能为空~")
        return

    type_name = search_dict[code_type]

    header = {
        "Authorization": f"Token {GLOT_TOKEN}",
        "Content-type": "application/json"
    }
    data = {
        "files": [
            {
                'name': f'main.{suffix_list[type_name]}',
                'content': code
            }
        ]
    }
    try:
        async with aiohttp.TCPConnector(ssl=False) as connector:
            async with aiohttp.request("POST", headers=header,
                                       json=data,
                                       url=f"https://glot.io/api/run/{type_name}/latest",
                                       connector=connector
                                       ) as resp:
                rep_json = await resp.json()
                if 'message' in rep_json:
                    await event.room().say(rep_json['message'])
                    return
                result = "运行结果:\n"
                stdout = rep_json['stdout'].rstrip()
                error = rep_json["error"].rstrip()
                stderr = rep_json["stderr"].rstrip()
                if stdout:
                    result += f"{stdout}\n"
                if stderr:
                    result += f"{stderr}\n"
                if error:
                    result += f"{error}\n"
                if len(result) > 500 or result.count("\n") > 15:
                    await event.room().say("返回值过长, 暂时屏蔽, 请等待链接显示实现")
                    return
                await event.room().say(result)
    except Exception as e:
        await event.room().say(f"请求失败...请联系维护者")
        sv.logger.error(f"{e} occurred when request l: {code_type} c:{code}")
