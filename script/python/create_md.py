#!/usr/bin/python3
import os
from pathlib import Path


def get_cur_dir_name():
    """
    :return: 获取当前执行目录
    """
    p = Path(os.getcwd())
    return p.name


def create_md():
    dir_name = get_cur_dir_name()
    if len(dir_name) == 0 : 
        print('目录为空，使用默认文件名')
        dir_name = 'README'
    print(dir_name)
    md_name = dir_name + '.md'
    if os.path.exists(md_name):
        print('文件已经存在')
        return

    f = open(dir_name + '.md', 'w')
    f.write('# '+dir_name)
    f.close()
    return '文件创建成功'


create_md()

# Q-Dir配置
# python/CreateMD_a.py=%sysdir%/cmd.exe=/k python "D:\04Git\10Private\mytest\script\python\create_md.py"
