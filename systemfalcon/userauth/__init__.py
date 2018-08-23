#!-*- coding:UTF-8 -*-
"""
用户登录后的三个可调用方法:
1,判断是否在模块,接收 request 和 模块名称 参数(判断第一个参数)， 返回真假值(这里返回 0、1)
2,返回模块 去重列表，只接收 request的话,可返回当前用户关联的用户列表; 接收 用户id参数, 可覆盖request的用户id，达成
    返回任意用户的模块情况.
3,返回用户关联的设备组信息
"""

#from userauth.in_module import in_module, return_module, return_device_group