#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author. ceyowa
# Created on 2020-04-29 19:16:24

import argparse
import base64
import hashlib
import Crypto
import sys
import signal
from Crypto.Cipher import AES
from binascii import b2a_hex

# 创建md5对象
md5 = hashlib.md5()

SPACEON_KEY = 'spaceon'

# 此处必须声明encode
# 若写法为hl.update(str)  报错为： Unicode-objects must be encoded before hashing
md5.update(SPACEON_KEY.encode(encoding='utf-8'))

SPACEON_KEY_MD5 = md5.hexdigest()
print("key=", SPACEON_KEY_MD5)


class EncryptDate:
    def __init__(self, key):
        self.key = key  # 初始化密钥
        self.length = AES.block_size  # 初始化数据块大小
        self.aes = AES.new(self.key, AES.MODE_ECB)  # 初始化AES,ECB模式的实例
        # 截断函数，去除填充的字符
        self.unpad = lambda date: date[0:-ord(date[-1])]

    def pad(self, text):
        """
        #填充函数，使被加密数据的字节码长度是block_size的整数倍
        """
        count = len(text.encode('utf-8'))
        add = self.length - (count % self.length)
        entext = text + (chr(add) * add)
        return entext

    def encrypt(self, encrData):  # 加密函数
        res = self.aes.encrypt(self.pad(encrData).encode("utf8"))
        msg = str(base64.b64encode(res), encoding="utf8")
        return msg

    def decrypt(self, decrData):  # 解密函数
        res = base64.decodebytes(decrData.encode("utf8"))
        msg = self.aes.decrypt(res).decode("utf8")
        return self.unpad(msg)


def quit(signum, frame):
    print('')
    print('stop success')
    sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="Help Infomation.", description="Press Ctrl+C to exist this program.")
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    en = EncryptDate(SPACEON_KEY_MD5.encode())
    while True:
        opt = input("请输入选项:e=加密,d=解密,默认为e") or 'e'
        if opt=='d':
            # admin->dqitDsL6I9vwLZ4iyzaT3g==
            data = input("请输入待解密内容：")
            print("解密结果：", en.decrypt(data))
        elif opt=='e':
            data = input("请输入待加密内容：")
            result = en.encrypt(data)
            print("加密结果：", result)
            print("解密结果：", en.decrypt(result))
        else:
            print("不支持的选项")
