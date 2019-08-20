#!/usr/bin/python3
import os
from pathlib import Path


    
def getCurDirName():
    """
    :return: 获取当前执行目录
    """
    p=Path(os.getcwd())
    return p.name
    
def create_md():
    dirName = getCurDirName()
    print(dirName)
    mdFileName = dirName + '.md'
    if (os.path.exists(mdFileName)):
        print('文件已经存在')
        return

    f = open(dirName + '.md','w')
    f.write('#!/user/bin/python')
    f.close()
    return '文件创建成功'
    

create_md()

# Q-Dir配置
# python/CreateMD_a.py=%sysdir%/cmd.exe=/k python "D:\04Git\10Private\mytest\script\python\create_md.py"