# -*- coding: utf-8 -*-
from django.urls import path

from . import views

urlpatterns = [
    path('payment/index/', views.index),  # 给templates返回数据，利用django模板进行测试，正常情况下由前端发起请求，参考接口get_pay_url即可
    path('payment/pay_url/', views.get_pay_url),  # 获取支付宝支付链接
    path('payment/get_result/', views.pay_result),  # 支付宝处理完成后同步回调通知
    path('payment/update_order/', views.update_order),  # 支付宝处理完成后支付宝服务器异步回调通知
]
