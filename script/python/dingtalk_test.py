# -*- coding: utf-8 -*-
'''
Created on 2018-9-17

@author: xiaoxuan.lp
'''
import dingtalk.api

req=dingtalk.api.OapiGettokenRequest("https://oapi.dingtalk.com/gettoken")

req.appkey="dingxcivkscrukvenwpe"
req.appsecret="TKI7ntNynl4zOvMXMxZ2LlV0qrvRT4OH67Uwy1z0E2jpZ2gfzl6QASip8lf5n2Rz"
try:
	resp= req.getResponse(access_token)
	print(resp)
except Exception,e:
	print(e)
# resp.access_token
request = dingtalk.api.OapiXiaoxuanPreTest1Request("https://oapi.dingtalk.com/topapi/xiaoxuan/pre/test1")
request.normalData="1"
request.systemData="2"

f = request.getResponse("******")
print(f)
    
