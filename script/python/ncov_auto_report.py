#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-04-29 19:16:24
import json
import os
from datetime import datetime

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
        self.access_info = info
        with open(ACCESS_JSON_FILE_PATH, 'w') as f:
            json.dump(info, f)
        pass


class AutoReport:
    user_info: object

    def __init__(self):
        self.report_info = ReportInfo()

    def start(self):
        self.login()
        if self.get_report_status() == 1:
            print('今日已上报')
            return
        self.report_today()
        pass

    def login(self):

        data = {
            'mobile': (None, LOGIN_MOBILE),
            'password': (None, 'cetc159357'),
            'client': (None, 'h5')
        }

        def login_result(r):
            print('login result:=%s' % r)
            if r.status_code != 200:
                raise Exception("Request failed, response code=%d" % r.status_code)
            r_json = r.json()
            if r_json and not r_json['success']:
                raise Exception("Request fail, response code=%d" % r_json['message'])
            if 'data' not in r_json:
                raise Exception("Request fail, have no data=%d" % r_json)
            return r_json['data']

        result = login_result(
            requests.post('https://asst.cetccloud.com/ncov/login', files=data, verify=False, headers=headers))
        if result and 'userInfo' in result:
            self.user_info = result['userInfo']
            self.report_info.save_access_info(self.user_info)
            return True
        raise Exception("登录失败")

    def verify_token(self):
        _token = self.report_info.access_token()
        print('Exist token:=%s' % _token)
        if not _token:
            return False
        jsonHeader['accesstoken'] = _token
        data = {
            'accessToken': _token
        }

        def refresh_token_result(r):
            print('refresh result:=%s' % r)
            if r.status_code != 200:
                raise Exception("Request failed, response code=%d" % r.status_code)
            r_json = r.json()
            if r_json and not r_json['success']:
                raise Exception("Request fail, response code=%d" % r_json['message'])
            if 'data' not in r_json:
                raise Exception("Request fail, have no data=%d" % r_json)
            return r_json['data']

        result = refresh_token_result(
            requests.post('https://asst.cetccloud.com/oort/oortcloud-sso/sso/v1/verifyToken', data=data,
                          verify=False, headers=jsonHeader))
        print('verify_token result:=%s' % result)
        jsonHeader['accesstoken'] = _token
        pass

    def get_report_status(self):
        def report_status(r):
            print('report_status :=%s' % r)
            if r.status_code != 200:
                raise Exception("Request failed, response code=%d" % r.status_code)
            r_json = r.json()
            # if r_json and not r_json['success']:
            #     raise Exception("Request fail, response code=%d" % r_json['message'])
            if r_json['code'] != 200:
                raise Exception("Request failed : %s, \r\n%s" % (r_json['msg'], r_json))
            if 'data' not in r_json:
                raise Exception("Request fail, have no data=%d" % r_json)
            return r_json['data']
            pass

        _token = self.user_info['accessToken']
        headers['accesstoken'] = _token
        data = {
            "accessToken": _token,
            "phone": LOGIN_MOBILE
        }
        print(headers)
        print(data)
        result = report_status(
            requests.post('https://asst.cetccloud.com/oort/oortcloud-2019-ncov-report/2019-nCov/report/reportstatus',
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

        def report_result(r):
            print('report_result :=%s' % r)
            if r.status_code != 200:
                raise Exception("Request failed, response code=%d" % r.status_code)
            r_json = r.json()
            if r_json['code'] != 200:
                raise Exception("Request failed : %s, \r\n%s" % (r_json['msg'], r_json))
            if 'msg' not in r_json:
                raise Exception("Request fail, have no data=%d" % r_json)
            return r_json['msg']
            pass

        headers['accesstoken'] = _token
        # print(headers)
        print(json.dumps(data))
        result = report_result(
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
