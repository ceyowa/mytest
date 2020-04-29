# 配置阿里镜像源
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 简单的本地服务器:
python -m http.server 8888

# 生成项目依赖包和版本列表文件

```pip freeze > requirements.txt```  

如果项目更新了依赖包，那么再次执行此命令更新

在新的虚拟环境中，一键安装requirements.txt文件中的依赖包：

`pip install -r requirements.txt`

# 文件列表

|文件名  |说明   |
|---------|---------|
|GetBaiduPanCookies.py  | 获取百度网盘cookies         |
|getPath.py         |获取当前路径       |
|get_tv_link.py     |获取下载链接  |