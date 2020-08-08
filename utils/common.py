# -*- coding: utf-8 -*-


def get_domain(request):
    """获取域名"""
    # 这里的域名应该为当前项目的域名，使用request.scheme 获取协议类型，使用request.META['HTTP_HOST'] 获取当前项目的域名
    domain = request.scheme + "://" + request.META['HTTP_HOST']

    return domain
