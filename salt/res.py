# coding = utf-8
"""
用于封装和处理图像资源

"""
import os
from wechaty import FileBox
from salt.config import RES_DIR


class Resource:
    def __init__(self, res_path):
        res_dir = os.path.expanduser(RES_DIR)  # 处理linux目录下 "~" 等类型的路径
        full_path = os.path.abspath(os.path.join(res_dir, res_path))
        self.__path = full_path

    @property
    def img(self, name: str = None):
        return FileBox.from_file(self.__path, name)
