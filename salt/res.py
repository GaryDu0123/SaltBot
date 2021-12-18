# coding = utf-8
"""


"""
import os
from wechaty import FileBox


class Resource:
    def __init__(self, res_path):
        from config import res_dir
        res_dir = os.path.expanduser(res_dir)  # 处理linux目录下 "~" 等类型的路径
        full_path = os.path.abspath(os.path.join(res_dir, res_path))
        self.__path = full_path

    @property
    def img(self, name=None):
        return FileBox.from_file(self.__path, name)
