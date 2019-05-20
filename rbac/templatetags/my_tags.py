# -*- coding:utf-8 -*-
__author__ = 'Qiushi Huang'

from django import template


register = template.Library()


@register.inclusion_tag("menu.html")
def get_menu(request):
    # 获取当前用户应该放到菜单栏中的权限
    menu_permission_list = request.session["menu_permission_list"]

    return {"menu_permission_list": menu_permission_list}
