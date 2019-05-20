# -*- coding:utf-8 -*-
__author__ = 'Qiushi Huang'

import re
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect, render


class ValidPermission(MiddlewareMixin):

    def process_request(self, request):
        # 当前访问路径
        current_path = request.path_info  # 当前路径的属性

        ########### 检查是否属于白名单 #############
        valid_url_list = ['/login/', '/reg/', '/admin/.*', '/logout/']
        for valid_url in valid_url_list:
            ret = re.match(valid_url, current_path)
            if ret:
                return   # 等同于return none

        ############### 检验是否登录 ##############
        user_id = request.session.get("user_id")

        if not user_id:
            return redirect("/login/")

        ################ 校验权限1 #################
        # permission_list = request.session.get("permission_list")
        #
        # flag = False
        # for permission in permission_list:
        #     permission = "^%s$" % permission
        #     ret = re.match(permission, current_path)  # 第一个参数是匹配规则，第二个参数是匹配项
        #     if ret:
        #         flag = True
        #         break
        # if not flag:
        #     # 如果没有访问权限
        #     return HttpResponse("没有访问权限！")

        ################ 校验权限2 #################
        permission_dict = request.session.get('permission_dict')

        for item in permission_dict.values():  # 循环只取字典的值
            urls = item["urls"]
            for reg in urls:
                reg = "^%s$" % reg
                ret = re.match(reg, current_path)
                if ret:
                    print("actions", item["actions"])
                    request.actions = item["actions"]
                    return None

        return HttpResponse("没有访问权限！")
        # return render(request, "not_found.html")   # 没有权限跳转到登录页面
