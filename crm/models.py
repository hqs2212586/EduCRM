# -*- coding:utf-8 -*-
__author__ = 'Qiushi Huang'

from django.db import models
from rbac.models import *
from fernet_fields import EncryptedCharField


class Department(models.Model):
    """
    部门
    武汉工大部     1001
    荆楚理工部     1002
    湖北二师部     1003
    """
    title = models.CharField(verbose_name='部门名称', max_length=16)
    code = models.IntegerField(verbose_name='部门编号', unique=True, null=False)

    def __str__(self):
        return self.title


class UserInfo(models.Model):
    """
    员工表(与rbac.User做一对一关联)
    """
    code = models.CharField(verbose_name='验证码', max_length=16, unique=True)
    name = models.CharField(verbose_name='员工姓名', max_length=16)
    # username = models.CharField(verbose_name='用户名', max_length=32, unique=True)
    # password = models.Field(verbose_name='密码', max_length=64)
    tel = models.CharField(verbose_name='手机号', max_length=64)
    # 模仿 SQL 约束 ON DELETE CASCADE 的行为，换句话说，删除一个对象时也会删除与它相关联的外键对象。
    depart = models.ForeignKey(verbose_name='部门', to="Department", to_field="code", on_delete=models.CASCADE)
    # 员工表Userinfo与rbac.User表做一对一关联
    # 临时添加字段，设置参数null=True
    user = models.OneToOneField(to=User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.code    # 销售码


class School(models.Model):
    """
    校区表
    如：
        武汉工大
        湖北二师
        荆楚理工
    """
    title = models.CharField(verbose_name='院校', max_length=32)

    def __str__(self):
        return self.title


class Course(models.Model):
    """
    专业表
    如：
        计算机科学与技术
        动画
        工程管理
        工商管理
        电子商务
        会计学
    """
    name = models.CharField(verbose_name='专业名称', max_length=32)

    def __str__(self):
        return self.name


class Customer(models.Model):
    """ 客户(学生)表 """
    name = EncryptedCharField(verbose_name='姓名', max_length=64)
    gender_choices = (
        (1, '男'),
        (2, '女')
    )
    gender = models.SmallIntegerField(verbose_name='性别', choices=gender_choices)
    nation = models.CharField(verbose_name='民族', max_length=64, default='汉族')
    birth_place = models.CharField(verbose_name='籍贯', max_length=64, default='湖北武汉')
    identity_num = models.CharField(verbose_name='身份证号', max_length=64, unique=True)
    address = models.CharField(verbose_name='通知书邮寄地址', max_length=128)
    postcode = models.CharField(verbose_name='邮编', max_length=12)
    tel = EncryptedCharField(verbose_name='联系电话', max_length=64, help_text='必填')
    # 学生的学校
    stu_school = models.ForeignKey(verbose_name='院校', to='School', on_delete=models.CASCADE)
    # 报读专业
    course = models.ManyToManyField(verbose_name='报读专业', to='Course')
    # auto_now_add：创建时间不用复制，默认使用当前时间赋值
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    # 验证码(销售码)
    consultant = models.ForeignKey(verbose_name="验证码", to='UserInfo', to_field='code',
                                on_delete=models.CASCADE)

    def __str__(self):
        return self.name


