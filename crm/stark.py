# -*- coding:utf-8 -*-
__author__ = 'Qiushi Huang'

import os
import datetime
import xlrd
from xlwt import *
from io import  BytesIO
from django.db import transaction   # 数据库事务操作
from django.conf.urls import url
# 使用mark_safe函数标记后，django将不再对该函数的内容进行转义
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponse, redirect, render
from stark.service.stark import site, ModelStark
from . import models


# 注册部门到stark
class DepartmentConfig(ModelStark):
    list_display = ['title', 'code']
    search_fields = ['title', 'code']
site.register(models.Department, DepartmentConfig)


# 注册用户到stark
class UserConfig(ModelStark):
    list_display = ["name", "tel", "depart", "code"]
    search_fields = ['name', 'depart', 'code']
site.register(models.UserInfo, UserConfig)


# 注册学校到stark
class SchoolConfig(ModelStark):
    list_display = ['title']
site.register(models.School, SchoolConfig)


# 注册专业到stark
class CourseConfig(ModelStark):
    list_display = ['name']
site.register(models.Course, CourseConfig)


# 注册客户(学生)到stark
class CustomerConfig(ModelStark):
    def display_gender(self, obj=None, header=False):
        if header:
            return "性别"
        return obj.get_gender_display()  # 取到choices属性的值

    def display_course(self, obj=None, header=False):   # obj是客户对象
        """专业(定制展示字段a标签)"""
        if header:
            return "专业"
        temp = []
        for course in obj.course.all():    # 遍历所有专业
            s = "<a href='/stark/crm/customer/cancel_course/%s/%s' " \
                "style='border:1px solid #369;padding:3px 6px;'>" \
                "<span>%s</span></a>&nbsp;" % (obj.pk, course.pk, course.name)
            temp.append(s)
        return mark_safe("".join(temp))

    def extra_url(self):
        """扩展路由"""
        temp = []
        temp.append(url(r"mycustomer/", self.mycustomer))
        temp.append(url(r'export/', self.excel_export))
        temp.append(url(r'import/', self.excel_import))
        return temp

    def mycustomer(self, request):
        """我的客户视图"""
        user_id = request.session.get("user_id")
        print(user_id)
        my_customer_list = models.Customer.objects.filter(consultant__id=user_id)
        print(my_customer_list)
        return render(request, "mycustomer.html", locals())

    def excel_import(self, request):
        """批量导入数据"""
        if request.method == 'GET':
            return render(request, 'excel_import.html', locals())
            # return JsonResponse({'msg': '不是post请求'})
        else:
            user_id = request.session.get("user_id")
            file_obj = request.FILES.get('my_file')
            type_excel = file_obj.name.split('.')[1]
            if 'xls' == type_excel:
                # 开始解析上传的excel表格
                wb = xlrd.open_workbook(filename=None, file_contents=file_obj.read())
                table = wb.sheets()[0]
                nrows = table.nrows    # 行数
                # ncole = table.ncols  # 列数
                try:
                    # 正常的数据库操作应该是原子性操作
                    with transaction.atomic():
                        for i in range(1, nrows):
                            # i/o
                            row_value = table.row_values(i)   # 一行的数据
                            models.Customer.objects.create(
                                name=row_value[0],
                                gender=row_value[1],
                                nation=row_value[2],
                                birth_place=row_value[3],
                                identity_num=row_value[4],
                                address=row_value[5],
                                postcode=row_value[6],
                                tel=row_value[7],
                                stu_school=models.School.objects.filter(id=1).first(),
                                # course=models.Course.objects.first(),
                                create_time=datetime.datetime.now(),
                                consultant=models.UserInfo.objects.filter(id__in=[1]).first()
                            )
                except Exception as e:
                    return HttpResponse('出现错误...%s' % e)
                return HttpResponse("上传成功")
            return HttpResponse('上传文件格式不是xlsx')

    def excel_export(self, request):
        """导出excel表格"""
        list_obj = models.Customer.objects.all().order_by("create_time")
        if list_obj:
            # 创建工作薄
            ws = Workbook(encoding="UTF-8")
            w = ws.add_sheet(u'数据报表第一页')
            w.write(0, 0, 'id')
            w.write(0, 1, u'姓名')
            w.write(0, 2, u'性别')
            w.write(0, 3, u'民族')
            w.write(0, 4, u'籍贯')
            w.write(0, 5, u'身份证号')
            w.write(0, 6, u'通知书邮寄地址')
            w.write(0, 7, u'邮编')
            w.write(0, 8, u'联系电话')
            w.write(0, 9, u'院校')
            w.write(0, 10, u'专业')
            w.write(0, 11, u'创建日期')
            w.write(0, 12, u'销售码')
            # 写入数据
            excel_row = 1
            for obj in list_obj:
                data_id = obj.id
                data_name = obj.name
                data_gender = obj.gender
                data_nation = obj.nation
                data_birth = obj.birth_place
                data_identity_num = obj.identity_num
                data_address = obj.address
                data_postcode = obj.postcode
                data_tel = obj.tel
                data_school = obj.stu_school.title
                data_course = obj.course.name
                data_time = obj.create_time.strftime("%Y-%m-%d")[:10]
                data_consultant = obj.consultant.code
                w.write(excel_row, 0, data_id)
                w.write(excel_row, 1, data_name)
                w.write(excel_row, 2, data_gender)
                w.write(excel_row, 3, data_nation)
                w.write(excel_row, 4, data_birth)
                w.write(excel_row, 5, data_identity_num)
                w.write(excel_row, 6, data_address)
                w.write(excel_row, 7, data_postcode)
                w.write(excel_row, 8, data_tel)
                w.write(excel_row, 9, data_school)
                w.write(excel_row, 10, data_course)
                w.write(excel_row, 11, data_time)
                w.write(excel_row, 12, data_consultant)
                excel_row += 1
                # 检测文件是否存在
                # 方框中代码是保存本地文件使用，如不需要请删除该代码
                ###########################
            exist_file = os.path.exists("stu_info.xls")
            if exist_file:
                os.remove(r"stu_info.xls")
            ws.save("customer_info.xls")
            ############################
            sio = BytesIO()
            ws.save(sio)
            sio.seek(0)
            response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=stu_info.xls'
            response.write(sio.getvalue())
            return response

    list_display = ["name", display_gender, "nation",
                    "identity_num", "tel", "course", "consultant"]
    search_fields = ['name', 'consultant', 'gender', 'nation']
site.register(models.Customer, CustomerConfig)