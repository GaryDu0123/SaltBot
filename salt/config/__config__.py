from salt import __version__
"""
配置文件, 用于放置各种参数配置
"""


WECHATY_PUPPET_SERVICE_TOKEN = "wechaty-puppet-wechat"
WECHATY_TOKEN = "python-wechaty-97b5ee4f-f9bb-44d2-af1e-919b7d122539"
WECHATY_PUPPET_SERVICE_ENDPOINT = 'localhost:8080'

# bot的名字, 用来调用bot的功能
BOT_NAME = ["salt", "盐"]

# 超级用户的名单列表
SUPER_USER_LIST = ["wxid_5rxffo4dnb0612", "wxid_bx4vxdwc8hkg11"] #

# Google Translate API
# https://rapidapi.com 去这里申请
GOOGLE_TRANSLATE_API_KEY = "b5f1e29348msh64543d188edb2dap1db263jsn41c444cdbac8"

# https://glot.io/account/token
GLOT_TOKEN = "1d2b9f31-44ef-494f-a823-e1af39cffb55"

# 放置资源图片的`文件夹`
RES_DIR = "D:\\Project\\SaltBot\\res"
CONFIG_DIR = "D:\\Project\\SaltBot\\config_for_test"  # None  # 默认留空, 自定义配置文件的文件夹

# 选择开启的模块
MODULES_ON = [
    "repeat",
    "manage",
    "translate",
    "nbnhhsh",
    "github_push",
    "glotcode",
    "random_group_friends"
]

# 功能清单
MANUAL = f"""
功能清单
Version: {__version__}
[复读] 复读所发送的文本
[翻译] 翻译一些文字到中文 
[?nbnhhsh] 试试?能不能好好说话
Github自动提交推动

服务管理请发送 [开启|关闭 服务名]
查看群开启的功能请使用 [服务列表]
部分服务的使用需要加bot名使用, 比如
{BOT_NAME[0]}复读 Hello,world
"""
