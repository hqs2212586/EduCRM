from django.test import TestCase

# Create your tests here.

# class A(object):
#     x = 12
#
#     def func(self):
#         print(self.x)
#
# class B(A):
#     x = 5
#
#
# b = B()
# b.func()  # 5
# 从调用者类里去找x，如果调用者中没有x，去父类找


#
# class Person(object):
#     def __init__(self, name):
#         self.name = name
#
# alex = Person("alex")
#
# s = "name"
#
# # 直接alex.s  或者alex."name"都是取不到值的
# print(getattr(alex, s))   # alex



# class Person(object):
#     def __init__(self, name):
#         self.name = name
#
#     def eat(self):
#         print(self)
#         print("eat.....")
#
# # 实例方法
# egon = Person("egon")
# egon.eat()
# """
# <__main__.Person object at 0x10401ae48>
# eat.....
# """
#
# # 函数
# Person.eat(123)
# """
# 123
# eat.....
# """



# class Persoon(object):
#
#     def __init__(self, name):
#         self.name = name
#
#     def __str__(self):
#         return self.name
#
#
# alex = Persoon("alex")
# print(alex.__str__)
# print(alex.__str__())
# print(str(alex))
"""'
<bound method Persoon.__str__ of <__main__.Persoon object at 0x10401ae48>>
alex
alex
"""


def foo():
    return

print(foo.__name__)   # foo

