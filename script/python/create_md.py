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
    f = open(dirName + '.md','w')
    f.write('#!/user/bin/python')
    f.close()
    
    
print(getCurDirName())
create_md()