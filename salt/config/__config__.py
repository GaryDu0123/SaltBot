from salt import __version__
"""
配置文件, 用于放置各种参数配置
"""


WECHATY_PUPPET_SERVICE_TOKEN = "wechaty-puppet-wechat"
WECHATY_TOKEN = "python-wechaty-97b5ee4f-f9bb-44d2-af1e-919b7d122539"
WECHATY_PUPPET_SERVICE_ENDPOINT = 'localhost:8080'

# bot的名字, 用来调用bot的功能
BOT_NAME = ["salt", "盐"]

# Google Translate API
# https://rapidapi.com/googlecloud/api/google-translate1/ 去这里申请
GOOGLE_TRANSLATE_API_KEY = ""

# 放置资源图片的`文件夹`
RES_DIR = "D:\\Project\\SaltBot\\res"
CONFIG_DIR = "D:\\Project\\SaltBot\\config_for_test"  # None  # 默认留空, 自定义配置文件的文件夹

# 选择开启的模块
MODULES_ON = [
    "repeat",
    "manage",
    "translate"
]

# 功能清单
MANUAL = f"""
功能清单
Version: {__version__}
[复读] 复读所发送的文本
[翻译] 翻译一些文字到中文 

"""
