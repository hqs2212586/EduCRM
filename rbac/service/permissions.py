# -*- coding:utf-8 -*-
__author__ = 'Qiushi Huang'


def initial_session(user, request):
    """
    注册权限到session中
    :param user:
    :param request:
    :return:
    """
    # 方案1：
    # permissions = user.roles.all().values("permissions__url").distinct()
    # print(permissions)  # <QuerySet [{'permissions__url': '/users/'}, {'permissions__url': '/users/add'}]>
    #
    # permission_list = []
    # for item in permissions:
    #     permission_list.append(item["permissions__url"])
    #
    # print(permission_list)
    #
    # request.session["permission_list"] = permission_list


    # 方案2：
    # 角色表跨到权限表查找
    permissions = user.roles.all().values("permissions__url", "permissions__group_id", "permissions__action").distinct()
    print("permissions", permissions)  # 有一个权限QuerySet中就有一个字典
    """
    permissions <QuerySet [{'permissions__url': '/users/', 
                            'permissions__group_id': 1, 
                            'permissions__action': 'list'}]>
    """
    # 对上述数据进行处理： 以组为键，以字典为值
    permission_dict = {}
    for item in permissions:
        gid = item.get("permissions__group_id")

        if not gid in permission_dict:
            permission_dict[gid] = {
                "urls": [item["permissions__url"], ],
                "actions": [item["permissions__action"], ]

            }
        else:
            # 组id已经在字典中
            permission_dict[gid]["urls"].append(item["permissions__url"])
            permission_dict[gid]["actions"].append(item["permissions__action"])

    print(permission_dict)  # {1: {'urls': ['/users/', '/users/add', '/users/delete/(\\d+)', '/users/edit/(\\d+)'],
    #                              'actions': ['list', 'add', 'delete', 'edit']}}

    request.session['permission_dict'] = permission_dict

    # 注册菜单权限
    # permissions = user.roles.all().values("permissions__url", "permissions__group_id", "permissions__action", "permissions__group__title").distinct()
    # 将权限组名改为权限名
    permissions = user.roles.all().values("permissions__url", "permissions__group_id", "permissions__action", "permissions__title").distinct()
    print("permissions", permissions)

    menu_permission_list = []   # 菜单栏中权限列表：空列表
    for item in permissions:
        # item是里面的字典
        if item["permissions__action"] == "list" or \
                item["permissions__action"] == "add" or \
                item["permissions__action"] == "export" or \
                item["permissions__action"] == "import":
            # 列表里面套一个个的元组，每个元组包含url和权限组title
            # menu_permission_list.append((item["permissions__url"], item["permissions__group__title"]))
            # 改为权限名
            menu_permission_list.append((item["permissions__url"], item["permissions__title"]))

    print("menu_permission_list", menu_permission_list)
    # menu_permission_list [('/stark/crm/studyrecord/', '学习记录'), ('/stark/crm/student/', '学生管理'),
    #  ('/stark/crm/customer/', '客户管理'), ('/stark/crm/customer/public', '客户管理'),
    # ('/stark/crm/customer/mycustomer/', '客户管理')]

    # 注册到session中
    request.session["menu_permission_list"] = menu_permission_list


