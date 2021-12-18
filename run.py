import os
import asyncio
from salt import init
from salt import log, config

os.environ["WECHATY_PUPPET_SERVICE_TOKEN"] = config.WECHATY_PUPPET_SERVICE_TOKEN
os.environ["WECHATY_TOKEN"] = config.WECHATY_TOKEN
os.environ['WECHATY_PUPPET_SERVICE_ENDPOINT'] = config.WECHATY_PUPPET_SERVICE_ENDPOINT
# os.environ['WECHATY_LOG'] = "silent"
logger = log.new_logger('__run__', config.DEBUG)
logger.info("Bot Start")
asyncio.run(init().start())

# ################### 测试程序 #####################
# import importlib
# import salt.trigger as trigger
# importlib.import_module("salt.modules.repeat")
# print(trigger.list_p)