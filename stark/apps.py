from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class StarkConfig(AppConfig):
    name = 'stark'

    def ready(self):   # 让django在启动时，自动扫描每个app下面的stark.py文件
        autodiscover_modules('stark')
