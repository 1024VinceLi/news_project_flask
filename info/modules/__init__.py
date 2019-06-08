from flask import Blueprint

# 创建蓝图对象
index_blu = Blueprint("index",__name__)



from .views import *
# 将views中的视图函数反导入到蓝图模块中