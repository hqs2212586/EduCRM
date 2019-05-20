## Educrm

基于`python3.6`和`Django2.1`的学生管理系统。

## 安装

`pip install -Ur requirements.txt`

如果没有pip，使用如下方式安装：    
OS X / Linux 电脑，终端下执行:  

    curl http://peak.telecommunity.com/dist/ez_setup.py | python
    curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python

windows电脑：  
 下载 http://peak.telecommunity.com/dist/ez_setup.py 和 https://raw.github.com/pypa/pip/master/contrib/get-pip.py 这两个文件，双击运行

## 配置
配置都是在`setting.py`中.部分配置迁移到了后台配置中。

很多`setting`配置我都是写在环境变量里面的.并没有提交到`github`中来.例如`SECRET_KEY`,`OAHUTH`,`mysql`以及邮件部分的配置等.你可以直接修改代码成你自己的,或者在环境变量里面加入对应的配置就可以了.

`test`目录中的文件都是为了`travis`自动化测试使用的.不用去关注.或者直接使用.这样就可以集成`travis`自动化测试了.

`bin`目录是在`linux`环境中使用`Nginx`+`Gunicorn`+`virtualenv`+`supervisor`来部署的脚本和`Nginx`配置文件.可以参考我的文章:

>[使用Nginx+Gunicorn+virtualenv+supervisor来部署django项目](https://www.lylinux.org/%E4%BD%BF%E7%94%A8nginxgunicornvirtualenvsupervisor%E6%9D%A5%E9%83%A8%E7%BD%B2django%E9%A1%B9%E7%9B%AE.html)

有详细的部署介绍.

### 数据库连接

 修改`EduCRM/setting.py` 修改数据库配置，如下所示：

     DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'educrm',
            'USER': 'root',
            'PASSWORD': 'password',
            'HOST': 'host',
            'PORT': 3306,
        }
    }
    
### 数据库迁移和创建超级用户
终端下执行:

    source educrm_env/bin/activate
    python3 manage.py makemigrations
    python3 manage.py migrate
    python3 createsuperuser

问题处理：
`
执行 python3 manage.py makemigrations
  File "/home/huangqs/educrm_env/lib/python3.6/site-packages/django/db/backends/mysql/operations.py", line 146, in last_executed_query
    query = query.decode(errors='replace')
AttributeError: 'str' object has no attribute 'decode'
代码问题：（line146）：query = query.encode(errors='replace')，把decode改为encode即可
`

### 项目运行
终端下执行:
    
    (educrm_env) [huangqs@huas EduCRM]$ python3 manage.py runserver
    (educrm_env) [huangqs@huas EduCRM]$ sudo /etc/init.d/uwsgi stop
        Stopping uwsgi: 
        /usr/bin/uwsgi STOPED.
    (educrm_env) [huangqs@huas EduCRM]$ sudo killall nginx                    
    (educrm_env) [huangqs@huas EduCRM]$ sudo uwsgi --ini /etc/uwsgi/uwsgi.ini 
        [uWSGI] getting INI configuration from /etc/uwsgi/uwsgi.ini
    (educrm_env) [huangqs@huas EduCRM]$ sudo /usr/local/nginx/sbin/nginx

### 权限组

```bash
PERMISSION GROUP
专业管理
招生老师管理
权限管理
部门管理
院校管理
学生管理
用户管理
```

### 权限（permission）

```bash
TITLE         URL                                GROUP        ACTION
修改用户	    /stark/rbac/user/(\d+)/change/	    用户管理	      edit
删除用户	    /stark/rbac/user/(\d+)/delete/	    用户管理	      delete
添加用户	    /stark/rbac/user/add/	            用户管理	      add
查看用户	    /stark/rbac/user/	                用户管理	      list
删除专业	    /stark/crm/course/(\d+)/delete/	    专业管理	      delete
修改专业	    /stark/crm/course/(\d+)/change/	    专业管理	      edit
添加专业	    /stark/crm/course/add/	            专业管理	      add
查看专业   	/stark/crm/course/	                专业管理	      list
删除招生老师	/stark/crm/userinfo/(\d+)/delete/	招生老师管理	  delete
添加招生老师	/stark/crm/userinfo/add/	        招生老师管理	  add
修改招生老师	/stark/crm/userinfo/(\d+)/change/	招生老师管理	  edit
查看招生老师	/stark/crm/userinfo/	            招生老师管理	  list
删除部门	    /stark/crm/department/(\d+)/delete/	部门管理	      delete
修改部门	    /stark/crm/department/change/	    部门管理	      edit
添加部门	    /stark/crm/department/add/	        部门管理	      add
查看部门	    /stark/crm/department/	            部门管理	      list
删除院校	    /stark/crm/school/(\d+)/delete/	    院校管理	      delete
编辑学院	    /stark/crm/school/change/	        院校管理	      edit
添加院校	    /stark/crm/school/add/	            院校管理	      add
查看院校	    /stark/crm/school/	                院校管理	      list
我的学生	    /stark/crm/customer/mycustomer/	    学生管理	      list
删除学生	    /stark/crm/customer/(\d+)/delete/	学生管理	      delete
修改学生	    /stark/crm/customer/(\d+)/change/	学生管理	      edit
添加学生	    /stark/crm/customer/add/	        学生管理	      add
查看学生	    /stark/crm/customer/	            学生管理	      list
```
