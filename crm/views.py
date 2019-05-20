# -*- coding:utf-8 -*-
__author__ = 'Qiushi Huang'


from django.shortcuts import render, redirect, HttpResponseRedirect
from rbac.models import User
from rbac.service.permissions import initial_session


def login(request):
    """登陆"""
    if request.method == 'POST':
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        # 拿到当前用户对象
        user = User.objects.filter(name=user, pwd=pwd).first()
        if user:
            # 登录成功
            request.session["user_id"] = user.pk
            request.session["username"] = user.name
            # 注册权限到session中
            initial_session(user, request)
            return redirect("/stark/crm/customer/mycustomer/")
        else:
            # 用户不存在
            return render(request, "not_found.html")
    return render(request, "login.html", locals())


def logout(request):
    """登出"""
    request.session.flush()
    return redirect("/login/")





