#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-04-29 19:16:24

import requests
import json
import os

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'

APP_ID = "df626fdc9ad84d3a95633c10124df358"
SECRE_KEY = "D8FE427008F065C1B781917E82E1EC1E"
headers = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9",
    "accesstoken": "null",
    "applyid": APP_ID,
    "secretkey": SECRE_KEY,
    'User-Agent': USER_AGENT
}
jsonHeader = headers.copy()
jsonHeader['Content-Type'] = 'application/json; charset=utf-8'

ACCESS_JSON_FILE_PATH = 'ncov_auto_report.json'


class ReportInfo:
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
    def __init__(self):
        self.report_info = ReportInfo()

    def start(self):
        self.login()
        self.get_report_status()

        pass

    def login(self):

        data = {
            'mobile': (None, '18180560355'),
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
            self.user_ifno = result['userInfo']
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

        pass


if __name__ == "__main__":
    AutoReport().start()
