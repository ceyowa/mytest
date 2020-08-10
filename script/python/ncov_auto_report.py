#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-04-29 19:16:24
import codecs
import json
import os
from datetime import datetime
from PIL import Image
from io import BytesIO

import requests

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
LOGIN_MOBILE = '18180560355'
APP_ID = "df626fdc9ad84d3a95633c10124df358"
SECRE_KEY = "D8FE427008F065C1B781917E82E1EC1E"
headers = {
    "accept": "application/json",
    "accesstoken": "null",
    "applyid": APP_ID,
    "secretkey": SECRE_KEY,
    'User-Agent': USER_AGENT,
}
jsonHeader = headers.copy()
# ; charset=utf-8
jsonHeader['Content-Type'] = 'application/json'

ACCESS_JSON_FILE_PATH = 'ncov_auto_report.json'

BIG_IMG_WIDTH = 300
BIG_IMG_HEIGHT = 150
SLICE_IMG_WIDTH = 40


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


class AutoReport:
    user_info: object

    def __init__(self):
        self.report_info = ReportInfo()

    def start(self):
        try:
            self.login()
            if self.get_report_status() == 1:
                print('今日已上报')
                return
            self.report_today()
        except ReportRequestError as e:
            print(e.msg)
            self.report_info.save_access_info(str(e))
        else:
            pass
        pass

    @staticmethod
    def request_result(request_name, r):
        print('%s result:=%s' % (request_name, r))
        if r.status_code != 200:
            raise ReportRequestError(request_name, "% s Request failed, response code=%d" % r.status_code)
        r_json = r.json()
        if r_json and not r_json['success']:
            raise ReportRequestError(request_name, "Request fail, response message=%s" % r_json['message'])
        if 'data' not in r_json:
            raise ReportRequestError(request_name, "Request fail, response =%s" % r_json)
        return r_json['data']

    def getCaptcha(self):
        result = self.request_result("getCaptcha",
                                     requests.post('https://asst.cetccloud.com/oort/oortcloud-sso/sso/v1/getCaptcha', files=data, verify=False,
                                                   headers=headers))
        if result and 'slideID' in result:
            self.slide_id = result['slideID']
            self.slide_ypos = result['ypos']

            get_big_img_response = requests.get('https://asst.cetccloud.com/oort/oortcloud-sso/slide/v1/%s/big.png?1596675762545' % self.slide_id)
            image = Image.open(BytesIO(get_big_img_response.content))

            return True
        raise ReportRequestError("getCaptcha", "获取验证码id失败")

    def login(self):

        data = {
            'model': "login"
        }

        result = self.request_result("login",
                                     requests.post('https://asst.cetccloud.com/ncov/login', files=data, verify=False,
                                                   headers=headers))
        if result and 'userInfo' in result:
            self.user_info = result['userInfo']
            self.report_info.save_access_info(self.user_info)
            return True
        raise ReportRequestError("login", "登录失败")

    def verify_token(self):
        _token = self.report_info.access_token()
        print('Exist token:=%s' % _token)
        if not _token:
            return False
        jsonHeader['accesstoken'] = _token
        data = {
            'accessToken': _token
        }

        result = self.request_result("refresh_token",
                                     requests.post('https://asst.cetccloud.com/oort/oortcloud-sso/sso/v1/verifyToken',
                                                   data=data,
                                                   verify=False, headers=jsonHeader))
        print('verify_token result:=%s' % result)
        jsonHeader['accesstoken'] = _token
        pass

    def get_report_status(self):
        _token = self.user_info['accessToken']
        headers['accesstoken'] = _token
        data = {
            "accessToken": _token,
            "phone": LOGIN_MOBILE
        }
        print(headers)
        print(data)
        result = self.request_result("report_status",
                                     requests.post(
                                         'https://asst.cetccloud.com/oort/oortcloud-2019-ncov-report/2019-nCov/report/reportstatus',
                                         json=data, verify=False, headers=headers))
        print('report data=%s' % result)
        return result['state']

    def report_today(self):
        _token = self.user_info['accessToken']
        now = datetime.today()
        start = datetime(now.year, month=now.month, day=now.day, hour=8, minute=30)
        end = datetime(now.year, month=now.month, day=now.day, hour=20, minute=30)
        data = {
            "phone": LOGIN_MOBILE,
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
                "phone": LOGIN_MOBILE
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
                "phone": LOGIN_MOBILE
            },
            "track_data": {
                "tracks": json.dumps([
                    {
                        "area": "中国 四川省 成都市-#-",
                        "start": ('%d000' % start.timestamp()),
                        "end": ('%d000' % end.timestamp())
                    }
                ]),
                "phone": LOGIN_MOBILE
            },
            "work_way": 0,
            "touch": 0,
            "accessToken": _token
        }

        headers['accesstoken'] = _token
        # print(headers)
        print(json.dumps(data))
        result = self.request_result("everyday_report",
            requests.post('https://asst.cetccloud.com/oort/oortcloud-2019-ncov-report/2019-nCov/report/everyday_report',
                          json=data, verify=False, headers=headers))
        print('report data=%s' % result)
        pass


if __name__ == "__main__":
    AutoReport().start()
    # now = datetime.today()
    # start = datetime(now.year, month=now.month, day=now.day, hour=8, minute=30)
    # print('%d' % start.timestamp())
    # print(time.strftime("%Y-%m-%d %H:%M:%S", start.time()))
    pass
