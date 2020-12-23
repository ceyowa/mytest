# 配置阿里镜像源
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 简单的本地服务器:
python -m http.server 8888

# 生成项目依赖包和版本列表文件

```pip freeze > requirements.txt```  

如果项目更新了依赖包，那么再次执行此命令更新

在新的虚拟环境中，一键安装requirements.txt文件中的依赖包：

`pip install -r requirements.txt`

# 生成可执行文件
- [Python PyInstaller安装和使用教程（详解版）](http://c.biancheng.net/view/2690.html)
```shell script
#生成无console的exe,-w只对windows有效
pyinstaller -F -w get_tv_link.py
```
| 选项  | 说明   |
|---------|---------|
|-h，--help |	查看该模块的帮助信息 |
|-F，-onefile |	产生单个的可执行文件  |
|-D，--onedir	|产生一个目录（包含多个文件）作为可执行程序    |
|-a，--ascii	|不包含 Unicode 字符集支持        |
|-d，--debug	|产生 debug 版本的可执行文件        |
|-w，--windowed，--noconsolc|	指定程序运行时不显示命令行窗口（仅对 Windows 有效） |
|-c，--nowindowed，--console|	指定使用命令行窗口运行程序（仅对 Windows 有效）      |
|-o DIR，--out=DIR|	指定 spec 文件的生成目录。如果没有指定，则默认使用当前目录来生成 spec 文件   |
|-p DIR，--path=DIR	|设置 Python 导入模块的路径（和设置 PYTHONPATH 环境变量的作用相似）。也可使用路径分隔符（Windows 使用分号，Linux 使用冒号）来分隔多个路径|
|-n NAME，--name=NAME|	指定项目（产生的 spec）名字。如果省略该选项，那么第一个脚本的主文件名将作为 spec 的名字 |



# 文件列表

|文件名  |说明   |
|---------|---------|
|GetBaiduPanCookies.py  | 获取百度网盘cookies         |
|getPath.py         |获取当前路径       |
|get_tv_link.py     |获取下载链接  |