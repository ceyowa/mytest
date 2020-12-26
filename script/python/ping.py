import time
import os


def pingComputer():
    for i in range(1, 256):
        host = '192.168.2.' + str(i)
        status1 = 'ping success'
        status2 = 'ping faild'

        nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        p = os.popen("ping " + host + " -n 2")
        line = p.read()
        if "无法访问目标主机" in line:
            print(nowTime, host, status2)
        else:
            print(nowTime, host, status1)


def getNotUseIp():
    for i in range(1, 256):
        host = '192.168.1.' + str(i)
        status1 = 'ping success'
        status2 = 'ping faild'

        # nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        p = os.popen("ping " + host + " -n 2 -w 1000")
        line = p.read()
        print(line)
        if "无法访问目标主机" in line or "请求超时" in line:
            print(host)


if __name__ == "__main__":
    getNotUseIp()
