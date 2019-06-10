# 公用的自定义工具类

def to_index_class(index):
    """
    返回指定索引对应的类名
    自定义过滤器类
    """
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    return ""