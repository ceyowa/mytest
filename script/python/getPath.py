import os

def get_root():
    """
    :return: 返回当前项目的根目录
    """
    return  os.path.dirname(os.path.abspath( __file__ ))

def get_parent(path):
    """
    :param path: 传入路径，不需要传入文件名
    :return: 返回传入路径的父目录
    """
    return os.path.dirname(os.path.abspath(path))