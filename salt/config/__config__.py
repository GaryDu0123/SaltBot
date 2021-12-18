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
GOOGLE_TRANSLATE_API_KEY = "133044047cmsh226606af44aff6ep1681f7jsn40eb376c1397"

# 放置资源图片的文件夹
res_dir = "D:\\Project\\SaltBot\\res"

# 选择开启的模块
modules_on = [
    "repeat",
    "manage",
    "translate"
]
