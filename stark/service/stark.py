# -*- coding:utf-8 -*-
__author__ = 'Qiushi Huang'

import csv
import json
from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from stark.utils.page import Pagination
from django.db.models import Q
from django.db.models.fields.related import ManyToManyField, ForeignKey


class ShowList(object):
    """展示页面类"""
    def __init__(self, config, data_list, request):
        self.config = config   # 接收传递过来的配置类对象 ModelStark的实例对象
        self.data_list = data_list   # 接收传递过来的当前表的所有对象
        self.request = request   #  <WSGIRequest: GET '/stark/app01/book/?page=2'>
        # 分页
        data_count = self.data_list.count()
        current_page = int(self.request.GET.get("page", 1))  # 默认是第一页
        base_path = self.request.path   # /stark/app01/book/

        self.pagination = Pagination(
            current_page,
            data_count,
            base_path,
            self.request.GET,
            per_page_num=10,
            pager_count=11
        )
        # print("data_list", self.data_list)   # data_list <QuerySet [<Book: python葵花宝典>, <Book: go>, <Book: java>]>
        self.page_data = self.data_list[self.pagination.start:self.pagination.end]
        # print("page_data", self.page_data)   # page_data <QuerySet [<Book: python葵花宝典>]>

        # actions
        # self.actions = self.config.actions   # 拿到配置好的函数对象列表  [patch_init,]
        self.actions = self.config.new_actions()   # 拿到方法运行的返回结果

    def get_filter_linktags(self):
        """获取过滤字段"""
        link_dic = {}
        print("list_filter", self.config.list_filter)   # list_filter ['publish', 'authors']

        for filter_field in self.config.list_filter:
            """循环每一个过滤字段"""
            import copy
            # self.request.GET   # GET请求的所有数据
            params = copy.deepcopy(self.request.GET)
            # print("params", params)   # <QueryDict: {'publish__id': ['1']}>
            # cid是当前字段传过来的值
            cid = self.request.GET.get(filter_field, 0)
            # 没有值的时候默认为None，None是不能进行int()转换的，因此在这里给它设置默认值为0

            # print(filter_field)   # 'publish'  'authors'
            # 获取字段对象
            filter_field_obj = self.config.model._meta.get_field(filter_field)
            # print(filter_field_obj)  # app01.Book.publish   app01.Book.authors
            # 拿到关联表下的所有数据
            # print("rel...", filter_field_obj.rel.to.objects.all())   # 版本问题失效
            # print("rel...", filter_field_obj.related_model.objects.all())  # <QuerySet [<Publish: 苹果出版社>, <Publish: 香蕉出版社>]>

            if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj, ManyToManyField):
                data_list = filter_field_obj.related_model.objects.all()  # <QuerySet [<Publish: 苹果出版社>
            else:
                # 普通字段直接查询
                data_list = self.config.model.objects.all().values("pk", filter_field)  # 主键值  字段对象值

            temp = []

            # 处理all标签
            if params.get(filter_field):
                # print("_url", params.urlencode)
                del params[filter_field]
                temp.append("<a href='?%s'>all</a>" % params.urlencode())
            else:
                temp.append("<a class='active' href='#'>all</a>")  # 默认是all的状态

            # 处理数据标签
            for obj in data_list:   # obj是每一个对象（或者是数组）
                """循环每一个过滤字段关联的数据"""
                if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj, ManyToManyField):
                    # <QuerySet [<Publish: 苹果出版社>, <Publish: 香蕉出版社>]>
                    pk = obj.pk
                    text = str(obj)
                    params[filter_field] = pk   # 过滤字段：当前对象主键值
                else:
                    # 列表里面套着字典 data_list=[{"pk":1, "title":"go"},....]
                    pk = obj.get("pk")
                    text = obj.get(filter_field)
                    params[filter_field] = text   # 过滤字段：当前对象字段值

                # 利用urlencode将键值对转化为a=1&b=2的格式
                _url = params.urlencode()

                if cid == str(pk) or cid == text:
                    # get请求数据int转换后与对象主键值匹配，匹配成功添加active类
                    link_tag = "<a class='active' href='?%s'>%s</a>" % (_url, text)
                else:
                    # print(obj)  # 苹果出版社 香蕉出版社  alex  egon
                    # print(type(obj))   # <class 'app01.models.Publish'>  <class 'app01.models.Author'>
                    link_tag = "<a href='?%s'>%s</a>" % (_url, text)
                    # print(link_tag)  # <a href=>苹果出版社</a>

                temp.append(link_tag)

            link_dic[filter_field] = temp
            # print(link_dic)   # {'publish': ['<a href=>苹果出版社</a>', '<a href=>香蕉出版社</a>'], 'authors': ['<a href=>alex</a>', '<a href=>egon</a>']}

        return link_dic

    def get_action_list(self):
        """获取自定义批量操作"""
        temp = []
        for action in self.actions:
            temp.append({
                "name": action.__name__,    # 函数.__name__：拿到函数名
                "desc": action.short_description
            })  # [{"name": "patch_init", "desc": "批量处理"}]
        return temp

    def get_header(self):
        """构建表头"""
        header_list = []
        print("header", self.config.new_list_display())  # [checkbox ,"__str__", edit ,deletes]

        for field in self.config.new_list_display():

            if callable(field):
                # 如果是函数
                val = field(self, header=True)
                header_list.append(val)

            else:
                # 如果是字符串
                if field == "__str__":
                    header_list.append(self.config.model._meta.model_name.upper())  # 当前模型表名
                else:
                    # 如果不是"__str__"
                    # header_list.append(field)
                    val = self.config.model._meta.get_field(field).verbose_name
                    header_list.append(val)
        return header_list

    def get_body(self):
        """构建表单数据"""
        new_data_list = []
        # for obj in self.data_list:
        for obj in self.page_data:   # 当前页面的数据
            temp = []
            for field in self.config.new_list_display():  # ["__str__", ]   ["pk","name","age",edit]
                if callable(field):
                    val = field(self.config, obj)
                else:
                    try:    # 如果是普通字段
                        field_obj = self.config.model._meta.get_field(field)   # 拿到字段对象
                        if isinstance(field_obj, ManyToManyField):  # 判断是否是多对多
                            # 反射处理  增加.all
                            # 多对多的情况  obj.field.all()
                            ret = getattr(obj, field).all()  # <QuerySet [<Author: alex>, <Author: egon>]>
                            t = []
                            for mobj in ret:   # 多对多的对象
                                t.append(str(mobj))
                            val = ",".join(t)   # 用join方法实现拼接   alex,egon

                        else:
                            # 非多对多的情况
                            val = getattr(obj, field)   # 拿到的关联对象  处理不了多对多
                            if field in self.config.list_display_links:
                                # _url = reverse("%s_%s_change" % (app_label, model_name), args=(obj.pk,))
                                _url = self.config.get_change_url(obj)

                                val = mark_safe("<a href='%s'>%s</a>" % (_url, val))
                    except Exception as e:   # 如果是__str__
                        val = getattr(obj, field)   # 反射拿到对象__str__函数的返回值 self.name  武汉大学出版社
                        print(val)  # <bound method Publish.__str__ of <Publish: 武汉大学出版社>>
                temp.append(val)

            new_data_list.append(temp)
        return new_data_list


class ModelStark(object):
    """默认类，定制配置类"""
    list_display = ["__str__",]
    list_display_links = []
    modelform_class = []
    search_fields = []
    actions = []  # 调用self.actions拿到的是函数
    list_filter = []

    def __init__(self, model, site):
        self.model = model
        self.site = site

    def patch_delete(self, request, queryset):
        """默认批量删除操作"""
        queryset.delete()
    patch_delete.short_description = "批量删除"

    # 删除、编辑，复选框
    def edit(self, obj=None, header=False):
        """编辑"""
        if header:
            # 如果是表头显示操作
            return "操作"

        _url = self.get_change_url(obj)
        return mark_safe("<a href='%s'>编辑</a>" % _url)

    def deletes(self, obj=None, header=False):
        """删除"""
        if header:
            # 如果是表头显示操作
            return "操作"

        _url = self.get_delete_url(obj)
        # return mark_safe("<a href='%s/change'>删除</a>" % obj.pk)
        return mark_safe("<a href='%s/'>删除</a>" % _url)

    def checkbox(self, obj=None, header=False):
        """复选框"""
        if header:
            # 如果是表头显示操作
            return mark_safe("<input id='choice' type='checkbox'>")

        return mark_safe("<input class='choice_item' type='checkbox' name='selected_pk' value='%s'>" % obj.pk)

    def get_modelform_class(self):
        """用来获取modelform类"""
        if not self.modelform_class:
            # 如果没有值
            from django.forms import ModelForm
            from django.forms import widgets as wid

            class ModelFormDemo(ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"

            return ModelFormDemo
        else:
            # 如果有值说明在用户已经自己定制过了,直接取值
            return self.modelform_class

    def get_new_form(self, form):
        """form调整，给特殊字段添加属性修改url"""
        for bound_field in form:   # 拿到每一个字段
            # from django.forms.boundfield import BoundField
            # print(bound_field.field)  # 字段对象
            print(bound_field.name)   # title\publishDate\publish  字段名称
            # print(type(bound_field.field))  # 字段类型
            from django.forms.models import ModelChoiceField     # ModelMultipleChoiceField继承ModelChoiceField
            if isinstance(bound_field.field, ModelChoiceField):  # 通过这个判断是否是一对多或多对多的字段对象
                bound_field.is_pop = True   # 给所有一对多、多对多对象添加is_pop这个属性
                # 需要拿到的不是当前表而是字段关联表
                print("===》", bound_field.field.queryset.model)
                """
                一对多或者多对多字段的关联模型表
                <class 'app01.models.Publish'>  
                <class 'app01.models.Author'>
                """
                # 拿到模型名和应用名
                related_model_name = bound_field.field.queryset.model._meta.model_name
                related_app_label = bound_field.field.queryset.model._meta.app_label
                # 拼出添加页面地址
                _url = reverse("%s_%s_add" % (related_app_label, related_model_name))
                # url拿到后，再在后面拼接字段名称
                bound_field.url = _url + "?pop_res_id=id_%s" % bound_field.name   # /?pop_res_id=id_authors
        return form

    def add_view(self, request):
        """添加页面视图"""
        ModelFormDemo = self.get_modelform_class()
        form = ModelFormDemo()  # 实例化步骤提前不管是post请求还是get请求都会传递到模板中
        form = self.get_new_form(form)

        if request.method == "POST":
            form = ModelFormDemo(request.POST)
            if form.is_valid():  # 校验字段全部合格
                obj = form.save()   # 将数据保存到数据库
                print(obj)   # 拿到返回值：当前生成的记录
                pop_res_id = request.GET.get("pop_res_id")   # 拿到window.open打开页面后面的get请求

                if pop_res_id:
                    # 当属于window.open页面post请求
                    res = {"pk": obj.pk, "text": str(obj), "pop_res_id": pop_res_id}
                    return render(request, "pop.html", {"res": res})
                else:
                    # 跳转到当前访问表的查看页面
                    return redirect(self.get_list_url())
                    # 校验有错误返回页面，且包含了错误信息
            else:
                print('字段符合要求: %s' % form.cleaned_data)
                print('字段不符合要求: %s' % form.errors)

        return render(request, "add_view.html", locals())

    def delete_view(self, request, id):
        url = self.get_list_url()
        if request.method == "POST":
            self.model.objects.filter(pk=id).delete()
            return redirect(url)

        # self.model.objects.filter(pk=id).delete()
        return render(request, "delete_view.html", locals())

    def change_view(self, request, id):
        """编辑视图"""
        ModelFormDemo = self.get_modelform_class()   # 获取当前配置类
        # 拿到编辑对象
        edit_obj = self.model.objects.filter(pk=id).first()

        if request.method == "POST":
            form = ModelFormDemo(request.POST, instance=edit_obj)  # instance就是给这个记录更改为最新的数据
            if form.is_valid():  # 校验字段全部合格
                form.save()
                return redirect(self.get_list_url())  # 跳转到当前访问表的查看页面

            # （精髓）校验有错误返回页面，且包含了错误信息
            return render(request, "add_view.html", locals())

        form = ModelFormDemo(instance=edit_obj)   # 用instance放入编辑对象就有了编辑数据
        form = self.get_new_form(form)

        return render(request, "change_view.html", locals())

    def new_list_display(self):
        """返回新的列表"""
        temp = []
        temp.append(ModelStark.checkbox)  # 在列表中放一个checkbox名字
        temp.extend(self.list_display)  # 扩展进一个列表["pk","name","age"]

        if not self.list_display_links:
            # 如果没有值
            temp.append(ModelStark.edit)

        # temp.append(ModelStark.edit)    # edit函数名
        temp.append(ModelStark.deletes)   # deletes函数名

        return temp   # 返回新的列表

    def new_actions(self):
        """返回所有批量操作"""
        temp = []
        # 默认添加批量删除
        temp.append(ModelStark.patch_delete)
        # 添加自定义action
        temp.extend(self.actions)
        return temp

    def get_change_url(self,obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_change" % (app_label, model_name), args=(obj.pk,))

        return _url

    def get_delete_url(self, obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_delete" % (app_label, model_name), args=(obj.pk,))

        return _url

    def get_add_url(self):

        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_add" % (app_label, model_name))

        return _url

    def get_list_url(self):

        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_list" % (app_label, model_name))

        return _url

    def get_search_condition(self, request):
        """拿到搜索条件"""
        key_word = request.GET.get("q", "")   # 取不到q则直接取空
        self.key_word = key_word
        search_connection = Q()

        if key_word:  # 判断key_word是否为空
            search_connection.connector = "or"  # 查询条件设置为或
            for search_field in self.search_fields:  # self.search_fields   # ['title', "price"]
                search_connection.children.append((search_field + "__contains", key_word))
        return search_connection

    def get_filter_condition(self, request):
        """拿到过滤条件"""
        filter_condition = Q()  # 默认查询条件为且 and
        for filter_field, val in request.GET.items():   # 过滤字段、查询的值  去除fitler_field拼接的__id
            if filter_field in self.list_filter:    # 只处理filter过滤列表的键值（分页等排除）
            # if filter_field != "page":            # (分页等排除) ?page=2&
                filter_condition.children.append((filter_field, val))
        return filter_condition

    def list_view(self, request):
        if request.method == "POST":    # action
            print("POST:", request.POST)
            action = request.POST.get("action")
            selected_pk = request.POST.getlist("selected_pk")  # 拿到列表
            # 反射
            # self这里是配置类BookConfig，要在类中找到对应的函数
            action_func = getattr(self, action)   # patch_init
            # 拿到选中状态的pk值对象
            queryset = self.model.objects.filter(pk__in=selected_pk)  # <QuerySet [<Book: go>]>
            action_func(request, queryset)

        # 获取search的Q对象
        search_condition = self.get_search_condition(request)

        # 获取filter构建Q对象
        filter_condition = self.get_filter_condition(request)

        # 筛选当前表获取的数据
        data_list = self.model.objects.all().filter(search_condition).filter(filter_condition)  # 链式操作，二次过滤

        # 获取showlist展示页面
        show_list = ShowList(self, data_list, request)

        header_list = show_list.get_header()
        new_data_list = show_list.get_body()

        # 构建一个查看url
        add_url = self.get_add_url()
        print("add_url", add_url)
        return render(request, "list_view.html", locals())

    def extra_url(self):
        # 扩展路由
        return []

    def get_urls_2(self):
        temp = []
        # 用name取别名app名+model名+操作名可以保证别名不会重复
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        temp.append(url(r"^add/", self.add_view, name="%s_%s_add" % (app_label, model_name)))
        temp.append(url(r"^(\d+)/delete/", self.delete_view, name="%s_%s_delete" % (app_label, model_name)))
        temp.append(url(r"^(\d+)/change/", self.change_view, name="%s_%s_change" % (app_label, model_name)))
        temp.append(url(r"^$", self.list_view, name="%s_%s_list" % (app_label, model_name)))

        # 添加扩展路由接口
        temp.extend(self.extra_url())
        return temp

    @property
    def urls_2(self):
        return self.get_urls_2(), None, None  # [], None, None


class StarkSite(object):
    """site单例类"""
    def __init__(self):
        self._registry = {}

    def register(self, model, stark_class=None, **options):
        """注册"""
        if not stark_class:
            # 如果注册的时候没有自定义配置类,执行
            stark_class = ModelStark   # 配置类

        # 将配置类对象加到_registry字典中，键为模型类
        self._registry[model] = stark_class(model, self)   # _registry={'model':admin_class(model)}

    def get_urls(self):
        """构造一层url"""
        temp = []
        for model, stark_class_obj in self._registry.items():
            # model:一个模型表
            # stark_class_obj:当前模型表相应的配置类对象

            model_name = model._meta.model_name
            app_label = model._meta.app_label

            # 分发增删改查
            temp.append(url(r"^%s/%s/" % (app_label, model_name), stark_class_obj.urls_2))

        return temp

    @property
    def urls(self):
        return self.get_urls(), None, None


site = StarkSite()    # 使用python模块的方式实现单例模式
