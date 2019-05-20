from django.db import models


# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=32)
    pwd = models.CharField(max_length=32)
    roles = models.ManyToManyField(to="Role")

    def __str__(self):
        return self.name


class Role(models.Model):
    title = models.CharField(max_length=32)
    permissions = models.ManyToManyField(to="Permission")

    def __str__(self):
        return self.title


class Permission(models.Model):
    title = models.CharField(max_length=32)
    url = models.CharField(max_length=64)   # 32位不够用
    # 操作
    action = models.CharField(max_length=32, default="")  # 默认值为空
    # 分组
    group = models.ForeignKey("PermissionGroup", default=1, on_delete=True)

    def __str__(self):
        return self.title


class PermissionGroup(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title
