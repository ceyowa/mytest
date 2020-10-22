#!/usr/bin/python3
import os
from pathlib import Path


def get_cur_dir_name():
    """
    :return: 获取当前执行目录
    """
    p = Path(os.getcwd()).parent
    return p.name


def create_test_bat():
    cur_dir = os.getcwd()
    print(cur_dir)
    file_name = cur_dir + '/test.bat'
    if os.path.exists(file_name):
        print('文件已经存在')
        return

    f = open(file_name, 'w', encoding='utf-8')
    f.write('set SOURCE_DIR=' + cur_dir+'''
set TEST_DIR= % ~dp0
set TARGET=staff-manager-webapi-0.0.1-SNAPSHOT.jar
cd /d %SOURCE_DIR%

:: 由于mvn本身也是BAT文件，并且其结束时执行了exit命令。要让mvn命令不使当前脚本自动退出，只需要在mvn之前加上call命令
:: cls是清除当前界面信息（如果不想看到maven打包信息，可添加）
call mvn clean package
cd /d %TEST_DIR%
copy /Y "%SOURCE_DIR%\webapi\target\%TARGET%" "%TEST_DIR%\%TARGET%"
call start.bat''')
    f.close()
    return '文件创建成功'


create_test_bat()

# Q-Dir配置
# python/Test_a.bat=%sysdir%/cmd.exe=/k python "D:\04Git\10Private\mytest\script\python\create_test_bat.py"
