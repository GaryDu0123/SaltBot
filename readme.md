# SaltBot使用以及开发文档



## 设计

[![Powered by Wechaty](https://img.shields.io/badge/Powered%20By-Wechaty-brightgreen.svg)](https://wechaty.js.org) 
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/) 
[![GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-orange)](https://github.com/GaryDu0123/SaltBot/blob/master/LICENSE)
[![Hoshino](https://img.shields.io/badge/ProjectDesign-Hoshino-000066)](https://github.com/Ice-Cirno/HoshinoBot)

项目构建设计思路来源自[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot), 使用wechaty作为载体进行设计重写

社团需要, 非面向pcr玩家, 个人非常喜欢hoshino的生态, yyds~

## 安装

### 首先安装依赖

```bash
pip3 install -r requirement.txt
```

### 启动程序

1. docker运行, 并登陆微信

```shell
bash wechaty.sh
```

2. 启动项目

   **linux**

   ```shell
   python3 run.py
   ```

   **windows**

   ```shell
   py run.py
   ```

   

## 项目结构

```
SaltBot
├── LICENSE
├── readme.md
├── requirements.txt # 依赖
├── run.py          # 程序入口
├── salt
│   ├── __init__.py # 初始化
│   ├── config      # 用于存放配置文件
│   │   │     
│   │   ...
│   ├── message_processor.py  
│   ├── modules     # 存放插件
│   │   │
│   │   ...
│   ├── priv.py     # 权限控制
│   ├── res.py      # 图像资源发送
│   ├── service.py  # 服务模块的注册类
│   └── trigger.py  # 消息处理的触发器
├── wechaty.sh
└── 使用文档.md
```

<!-- tree -I "需要忽略的文件"-->

<!-- tree -I "venv|config_for_test|log*|res|__pycache__|test" -->



## 使用命令

命令前有可能需要加入bot名字或者指定字符触发例如:

```
[bot名字]为salt
salt帮助列表
salt开启 聊天
```



## 获取Bot帮助列表

```
help
帮助列表
```



### 获取分模块的详细帮助

```
帮助[模块名]
帮助github推送
```



### 启用关闭服务

```
开启 service-name
关闭 service-name
```



### 查看群内所有服务的状态

```
服务列表
lssv
```



## 开发帮助

### 初始化

<details>
    <summary>启动顺序</summary>
     <ul>
         <li>__init__初始化开始</li>
         <li>config加载</li>
         <li>log模块初始化</li>
         <li>trigger初始化</li>
         <li>service服务模块加载</li>
         <li>priv权限控制加载</li>
         <li>Scheduler定时调用服务启动</li>
         <li>trigger文本触发器加载</li>
         <li>message_processor初始化</li>
         <li>Service __System__ 加载</li>
         <li>异步开始执行初始化init()函数</li>
         <li>加载所有插件模块(modules), 装饰器开始注册函数以及服务到trigger内</li>
         <li>新建Wechaty对象, saltBot启动</li>
         <li>on_login加载SuperUser完毕</li>
         <li>消息处理开始</li>
    </ul>
</details>

### 添加模块

添加在salt/modules目录下的`python包(Python package)`, 在config文件内的MOUDELS_ON添加包名后会自动在Bot开启后导入

> [何为Python package?](https://www.jianshu.com/p/178c26789011)
>
> 在当前目录下有`__init__.py`文件的目录即为一个package。

**一个正确的模块结构**

```
salt/modules/repeat/
├──  ...
└──  __init__.py
```

### 如何新建一个服务(插件/模块)?

一个简单的例子

```python
from salt.service import Service
from wechaty import Room, Message
import re

sv = Service("复读", _help=f"发送 [{config.BOT_NAME[0]}复读 需要复读的消息]\n"
                         f"群 友 都 是 复 读 机")

@sv.on_prefix("复读")
async def repeat(event: "Message", msg: str):
    conversation: "Room" = event.room()
    msg = re.match(r"^复读(?P<message>.*)", msg)
    message = msg.group("message").strip()
    if message == "":
        message = "w复读内容是空的!!!(•́へ•́╬)"
    await conversation.say(message)

```



**先从Service类看起**

首先从service文件内`import`来`Service`类

```python
from salt.service import Service
```

新建一个Service对象

```python
sv = Service("复读")
```

Service对象内的参数可以为该模块提供更多的设置

```python
class Service:
    def __init__(self,
                 name: str,  # 服务名
                 enable_on_default: bool = False,  # 是否默认开启
                 visible: bool = True,  # 是否可见(系统级)
                 user_priv: int = priv.NORMAL,  # 用户可以使用该服务的权限
                 manage_priv: int = priv.ADMIN,  # 可以管理此模块的权限
                 _help: str = ""  # 该服务的详细帮助文档
                 ):
        ...
```

服务对象建立后, 我们便可以使用该服务对象下的`装饰器`进行函数的绑定与注册

```python
@sv.on_prefix("复读")
async def repeat(event: "Message", msg: str):
    ...
```

> [**什么是python装饰器？**](https://blog.csdn.net/qq_26442553/article/details/82226657)
> python装饰器就是用于拓展原来函数功能的一种函数，这个函数的特殊之处在于它的返回值也是一个函数，使用python装饰器的好处就是在不用更改原函数的代码前提下给函数增加新的功能。

**Service对象都提供了哪些触发方法呢**

```python
# 前缀触发
@sv.on_prefix(*word, only_to_me: bool = True)

# 正则触发
@sv.on_regex(*regex: Union[str, re.Pattern], only_to_me: bool = True)

# 全部匹配触发
@sv.on_full_match(*word, only_to_me: bool = True)

# 关键字触发
@sv.on_keyword(*word, only_to_me: bool = False)

# 定时任务
@sv.on_scheduler(*args, **kwargs)
```

**函数内各参数详解**

```python
*word: Any #  可变数量参数, 用于放置触发词或者触发规则 
*regex: Union[str, re.Pattern] # 传入正则字符串或者re.compile后的正则表达式, 用于正则触发
only_to_me: bool # 是否在消息前加了bot的名字, 类似于@bot触发
```



**:warning: 这个装饰器扮演了什么角色?**

```python
# Class Service 类的实例方法
def on_prefix(self, *word, only_to_me: bool = True):
    def registrar(func):
        #### start 这一部分是进入到trigger内function的状态
        @wraps(func)
        async def wrapper(event: "Message", msg: str):
            return await func(event, msg)  # 调用被装饰的函数
		#### end 
        
        # 在此处执行function(service)注册, 这一部分是在Bot启动就执行完毕的
        sf = ServiceFunc(self, only_to_me, func)
        for w in word:
            if isinstance(w, str):
                trigger.prefixTrigger.add(w, sf)
                self.logger.info(f"...")
            else:
                self.logger.error(f'...')
        return wrapper
    return registrar
```

装饰器会在程序启动后完成函数的装饰, 并且仅执行一次, 往后调用`func`均为被修饰后的function

不过我们开发模块时并不需要专注于这个是如何实现的, 只需要调用装饰器, 写入相应的触发词, 消息处理器便会将匹配到的消息准确分配给你的函数~好诶~

**关于函数方法体**

```python
@sv.on_prefix("复读")
async def repeat(event: "Message", msg: str):
    conversation: "Room" = event.room()
    msg = re.match(r"^复读(?P<message>.*)", msg)
    message = msg.group("message").strip()
    if message == "":
        message = "w复读内容是空的!!!(•́へ•́╬)"
    await conversation.say(message)
```

使用装饰器装饰后, 我们便可以拿到对应的消息了, 举个栗子:chestnut:

> 用户`Gary`在群聊`智乃屋`里发送了: `复读 栗子`
>
> 因为使用了装饰器on_prefix(前缀触发), 并以 "复读" 作为触发词, 所有以"复读"开头的对话都会触发这个函数, 而且传给我们一个Message对象, 也就是这里的event变量. 而有些时候因为要使用`bot名字+命令`的方式去使用服务, 为了省去开发者每次都要处理`bot名字`的麻烦, 对消息进行了处理, 所以msg拿到的永远为纯指令的消息
>
> 所以说此时:
>
> ```python
> event.room() == "智乃屋"
> event.takler() == "Gary"
> msg == "复读 栗子"
> ```
>
> 另外来说, 如果bot名字叫`salt`
>
> 用户`Gary`在群聊`智乃屋`里发送了: `salt复读 栗子`
>
> 那么此时我们还是可以获得相同的结果
>
> ```python
> event.room() == "智乃屋"
> event.takler() == "Gary"
> msg == "复读 栗子"
> ```

最后, 将消息发送出去

Room对象里面有`say(some_thing: Union[str, Contact, FileBox, MiniProgram, UrlLink])`这个方法, 可以向来源信息的群聊发送消息, 更详细的请参阅[wechaty文档](https://wechaty.readthedocs.io/zh_CN/latest/).



### 协程与异步

要完全理解这些模块是如何运行的, 你可能需要了解一下`asyncio`这个包的运行模式, 只需要基本的知识便可以快乐的编写了. 但是记住哦, 这里面所有的网络请求都要用异步的方式(`aiohttp`)进行~ <del>阻塞请求就有意思了(千万不要</del>



## Todo List :ice_cream:
- [x] 服务分群管理
- [x] 分群管理记录恢复(可能有bug)
- [x] 插件管理
- [x] 消息触发
- [x] 帮助列表扩展, 分模块的详细帮助
- [ ] 权限控制
- [ ] 对say的方法进行封装, 发送消息时对敏感词进行筛选




## 局限性

1. 因为Wechaty本身无法获取群号的限制(微信不存在群号), 权限控制的永久性存储使用的键为群名, 这可能导致在有多个重名的群时服务管理发生混乱.

2. 程序会在启动后对通讯录进行搜索并获取`Superuser`对象, 但Web版可能不具备登录后通讯录完全加载完毕的`ready`事件, 所以在`login`事件发生后对程序进行了一段时间的`睡眠`从而等待所有通讯录加载完毕, 但是当通讯录人数过多时, 预想有概率还是会出现没加载完毕导致获取对象失败`None`的问题. 当通讯录人数过多时, 建议超级用户与bot保持一定的联系, 从而减少加载Superuser失败的可能性.

   > 后续可能会尝试在事件内部做个循环, 在未加载超级用户成功前不允许bot启动
