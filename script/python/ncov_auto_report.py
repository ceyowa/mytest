#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-04-29 19:16:24
# 郑重声明:本脚本仅限用于学习和研究目的；不得将上述内容用于商业或者非法用途，否则，一切后果请自负! -- by ceyowa
import codecs
import json
import os
import random
import time
from datetime import datetime
from PIL import Image
from io import BytesIO

import requests

import urllib3

import argparse


# 控制台输出InsecureRequestWarning的问题
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BASE_URL = 'https://asst.cetccloud.com'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
headers = {
    "accept": "application/json",
    "accesstoken": "null",
    'User-Agent': USER_AGENT,
}
jsonHeader = headers.copy()
# ; charset=utf-8
jsonHeader['Content-Type'] = 'application/json'

ACCESS_JSON_FILE_PATH = 'ncov_auto_report.json'

BIG_IMG_WIDTH = 300
BIG_IMG_HEIGHT = 150
SLICE_IMG_WIDTH = 40

import logging
import logging.config
import yaml

LOG_FILE = 'ncov_auto_report.log'
# 清理原始日志
with open(LOG_FILE, 'w'):
    pass

with open('ncov_auto_report_logging.yml', 'r', encoding='UTF-8') as f_conf:
    dict_conf = yaml.full_load(f_conf)
dict_conf['handlers']['file']['filename'] = LOG_FILE
logging.config.dictConfig(dict_conf)
logger = logging.getLogger()


class ReportInfo:
    access_info: object

    def __init__(self):
        pass

    def access_token(self):
        if os.path.exists(ACCESS_JSON_FILE_PATH):
            try:
                with open(ACCESS_JSON_FILE_PATH, 'r') as f:
                    self.access_info = json.load(f)
            except:
                return None
            if self.access_info and 'accessToken' in self.access_info:
                return self.access_info['accessToken']
        return

    def save_access_info(self, info):
        if not isinstance(info, str):
            info = json.dumps(info)
        with codecs.open(ACCESS_JSON_FILE_PATH, 'w', 'utf-8') as f:
            f.write(info)
        pass


class ReportRequestError(RuntimeError):
    name: str
    msg: str

    def __init__(self, name, msg):
        self.name = name
        self.msg = msg

    def __str__(self):
        return self.name + ' : ' + self.msg


# 滑动块的外边框颜色
COLOR_BORDER_OUT = (255, 255, 0)
COLOR_BORDER_IN = (0, 0, 0)
COLOR_FILL = (128, 128, 128)


def check_border_color(img_data, x, y, width, color):
    x1 = x + width - 1
    y1 = y + width - 1

    for step in range(0, width):
        pix = img_data[y][x + step]
        if pix != color:
            return False
        pix = img_data[y + step][x]
        if pix != color:
            return False
        pix = img_data[y1][x1 - step]
        if pix != color:
            return False
        pix = img_data[y1 - step][x1]
        if pix != color:
            return False
    return True


def check_out_border(img_data, x, y):
    if check_border_color(img_data, x, y, SLICE_IMG_WIDTH, COLOR_BORDER_OUT):
        logger.debug("find out border")
        return True
    return False


def check_in_border(img_data, x, y):
    if check_border_color(img_data, x + 1, y + 1, SLICE_IMG_WIDTH - 2, COLOR_BORDER_IN):
        logger.debug("find in border")
        return True
    return False
    pass


def is_fill_color(img_data, x, y):
    x = x + 2
    y = y + 2
    width = SLICE_IMG_WIDTH - 4
    for i in range(0, width):
        for j in range(0, width):
            pix = img_data[y + j][x + i]
            if pix != COLOR_FILL:
                return False
    return True
    pass


def is_slice_block(img_data, x, y):
    return check_out_border(img_data, x, y) and check_in_border(img_data, x, y) and is_fill_color(img_data, x, y)


def get_slice_x_position(img, start_y=0):
    width = img.size[0]
    height = img.size[1]
    img_data = split_array(list(img.getdata()), BIG_IMG_WIDTH)
    for x in range(0, width - SLICE_IMG_WIDTH):
        for y in range(start_y, min(start_y + SLICE_IMG_WIDTH, height - SLICE_IMG_WIDTH)):
            pix = img_data[y][x]
            if COLOR_BORDER_OUT == pix and is_slice_block(img_data, x, y):
                return x
    return -1


def split_array(src, split_len: 10):
    result = []
    for i in range(0, len(src), split_len):
        result.append(src[i:i + split_len])
    return result


def request_result(request_name, r, raise_fail=True):
    if r.status_code != 200:
        raise ReportRequestError(request_name, "% s Request failed, response code=%d" % r.status_code)
    r_json = r.json()
    if r_json['code'] == 200 or r_json['code'] == '200':
        if 'data' in r_json:
            return r_json['data']
        else:
            return r_json
    elif not raise_fail:
        return r_json
    raise ReportRequestError(request_name, "Request fail, response =%s" % r_json)


NEED_RANDOM_SLEEP = True


def sleep_random(a=1, b=5):
    def before_proxy(func):
        def sleep_on_before(*arguments):
            if NEED_RANDOM_SLEEP:
                randint = random.randint(a, b)
                logger.info("random sleep %ds" % randint)
                time.sleep(randint)
            return func(*arguments)

        return sleep_on_before

    return before_proxy


class AutoReport:
    user_info: object

    def __init__(self, mobile, password):
        self.report_info = ReportInfo()
        self.mobile = mobile
        self.password = password

    def logged(self):
        return self.user_info

    @sleep_random(0, 600)
    def start(self):
        logger.debug("start func begin")
        try:
            # 检查已有的token
            if not self.verify_token():
                # 获取滑动验证码
                if self.get_captcha() and self.slide_verify():
                    # 登录
                    self.login()
            if self.logged():
                # 检查是否已经报告
                if self.get_report_status() == 1:
                    logger.debug('今日已上报')
                    return
                self.report_today()
        except ReportRequestError as e:
            logger.debug(str(e))
        else:
            pass
        pass

    @sleep_random(0, 3)
    def get_captcha(self):
        # slide_ypos = 53
        # image = Image.open("ncov_auto_report_big.png")
        # slice_x = get_slice_x_position(image, slide_ypos)
        # print("slice_y=%d" % slice_x)

        data = {
            'model': "login"
        }
        # 获取id
        # {"code": 200, "data": {"slideID": "d05fed35b9fa486fa3e85b302909a151", "ypos": 82}, "errcode": 200,
        #  "errmsg": "成功", "msg": "成功"}
        result = request_result("getCaptcha",
                                requests.post(BASE_URL + '/oort/oortcloud-sso/sso/v1/getCaptcha',
                                              json=data, verify=False,
                                              headers=headers))
        if result and 'slideID' in result:
            self.slide_id = result['slideID']
            slide_ypos = result['ypos']

            # 获取图片
            get_big_img_response = requests.get(
                BASE_URL + '/oort/oortcloud-sso/slide/v1/%s/big.png?1596675762545' % self.slide_id)
            image = Image.open(BytesIO(get_big_img_response.content))
            self.slice_x = get_slice_x_position(image, slide_ypos)
            logger.debug("slice_y=%d" % self.slice_x)
            return True
        raise ReportRequestError("getCaptcha", "获取验证码id失败")

    @sleep_random(1, 5)
    def slide_verify(self):
        data = {
            'xpos': self.slice_x,
            'slideid': self.slide_id
        }

        result = request_result("slide_verify",
                                requests.post(BASE_URL + '/oort/oortcloud-sso/sso/v1/slideverify',
                                              json=data, verify=False,
                                              headers=headers))
        if result:
            return True
        raise ReportRequestError("slide_verify", "验证码验证失败")

    @sleep_random(0, 3)
    def login(self):

        #     var
        #     t = new
        #     u["JSEncrypt"]
        #     , i = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCgZmNj7QvhbpgdqxN7ZCR+r874KZb/qRvlHRieJJREH+i5/hPbpPH5KheEFxoo7nyAkPIcQYPshHvC4UJBe1HrHjdhjFnMA967aebBtioXBOB0qR4ql0DtWA0PrJWtDABeTpPXedqmzMcYIxr1Wq/viIPsjCHRiyRx6mhYqT5P6wIDAQAB";
        #
        # t.setPublicKey(i);
        # var
        # a = t.encrypt(e);
        # return a
        data = {
            'mobile': (None, self.mobile),
            'password': (None, self.password),
            'client': (None, 'h5'),
            'slideID': (None, self.slide_id)
        }

        result = request_result("login",
                                requests.post(BASE_URL + '/ncov/login', files=data, verify=False,
                                              headers=headers))
        if result and 'userInfo' in result:
            self.user_info = result['userInfo']
            self.report_info.save_access_info(self.user_info)
            logger.debug("login success")
            return True
        raise ReportRequestError("login", "登录失败")

    @sleep_random(1, 5)
    def verify_token(self):
        _token = self.report_info.access_token()

        if not _token:
            return False
        jsonHeader['accesstoken'] = _token
        data = {
            'accessToken': _token
        }

        result = request_result("verifyToken",
                                requests.post(BASE_URL + '/oort/oortcloud-sso/sso/v1/verifyToken',
                                              json=data,
                                              verify=False, headers=jsonHeader), False)
        logger.debug('verify_token success')
        if result and 'userInfo' in result:
            self.user_info = result['userInfo']
            jsonHeader['accesstoken'] = _token
            return True

        return False

    @sleep_random(0, 3)
    def get_report_status(self):
        if not self.logged():
            raise ReportRequestError("get_report_status", "无accessToken,请先登录")
        _token = self.user_info['accessToken']
        headers['accesstoken'] = _token
        data = {
            "accessToken": _token,
            "phone": self.mobile
        }
        # logger.debug(headers)
        # logger.debug(data)
        result = request_result("report_status",
                                requests.post(
                                    BASE_URL + '/oort/oortcloud-2019-ncov-report/2019-nCov/report/reportstatus',
                                    json=data, verify=False, headers=headers))
        logger.debug('get_report_status success')
        return result['state']

    @sleep_random(1, 5)
    def report_today(self):
        if not self.logged():
            raise ReportRequestError("get_report_status", "无accessToken,请先登录")
        _token = self.user_info['accessToken']
        now = datetime.today()
        start = datetime(now.year, month=now.month, day=now.day, hour=8, minute=30)
        end = datetime(now.year, month=now.month, day=now.day, hour=20, minute=30)
        data = {
            "phone": self.mobile,
            "Traffic_data": {
                "bike": 0,
                "bike_way": "",
                "bus": 0,
                "bus_number": "",
                "car": 0,
                "car_way": "",
                "metro": 0,
                "metro_number": "",
                "other": 0,
                "other_way": "",
                "walk": 0,
                "walk_way": "",
                "phone": self.mobile
            },
            "physical_data": {
                "type1": 0,
                "type1_state": "0",
                "type2": 0,
                "type3": 0,
                "type4": 0,
                "type5": 0,
                "type6": 0,
                "type7": 0,
                "type7_state": "",
                "phone": self.mobile
            },
            "track_data": {
                "tracks": json.dumps([
                    {
                        "area": "中国 四川省 成都市-#-",
                        "start": ('%d000' % start.timestamp()),
                        "end": ('%d000' % end.timestamp())
                    }
                ]),
                "phone": self.mobile
            },
            "work_way": 0,
            "touch": 0,
            "accessToken": _token
        }

        headers['accesstoken'] = _token
        result = request_result("everyday_report",
                                requests.post(
                                    BASE_URL + '/oort/oortcloud-2019-ncov-report/2019-nCov/report/everyday_report',
                                    json=data, verify=False, headers=headers))
        logger.debug('report_today success')
        pass

if __name__ == "__main__":
    print("郑重声明:本脚本仅限用于学习和研究目的；不得用于任何商业或者非法用途，否则，一切后果请自负! -- by ceyowa")
    logger.debug("main start")
    parser = argparse.ArgumentParser(usage="it's usage tip.", description="help info.")

    parser.add_argument("-u", required=True, dest="user", help="the login user name.")
    parser.add_argument("-p", required=True, dest="password", help="the login password.")
    parser.add_argument("-s", dest="secret_key", default='D8FE427008F065C1B781917E82E1EC1E',
                        help="the 'secretKey' in header.")
    parser.add_argument("-a", dest="app_id", default='df626fdc9ad84d3a95633c10124df358',
                        help="the 'applyId' in header.")
    args = parser.parse_args()

    headers['secretKey'] = args.secret_key
    headers['applyID'] = args.secret_key

    AutoReport(args.user, args.password).start()
    # AutoReport().get_captcha()
    # now = datetime.today()
    # start = datetime(now.year, month=now.month, day=now.day, hour=8, minute=30)
    # print('%d' % start.timestamp())
    # print(time.strftime("%Y-%m-%d %H:%M:%S", start.time()))
    pass
