import os
import re
from typing import Union

from wechaty import Room, Contact, Message

from salt import config
from salt.service import Service, SchedulerTrigger

sv = Service("Github推送", enable_on_default=False)

_config_dir_git = os.path.expanduser(f'{config.CONFIG_DIR}/github_push_config/'
                                     if config.CONFIG_DIR is not None else
                                     "~/.SaltBot/github_push_config/")

os.makedirs(_config_dir_git, exist_ok=True)


@sv.on_scheduler(SchedulerTrigger.CronTrigger, minute='*/5')
async def github_push():
    pass


@sv.on_regex(re.compile("^github推送 *.*", re.I))
async def github_set_up(event: "Message", msg: str):
    conversation: "Room" = event.room()
    message = re.match(re.compile("^github推送 *(?P<message>.*)", re.I), msg).group("message").strip()

    if message == "":
        await conversation.say("添加推送请以[github推送 仓库名 TOKEN]的形式发送")


