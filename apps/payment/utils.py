# -*- coding: utf-8 -*-
import os

from alipay import AliPay
from django.conf import settings


def my_ali_pay(notify_url=None):
    """
    支付宝支付对象
    :param notify_url:
    支付成功支付宝服务器异步通知默认回调url，会向这个地址发送POST请求，接口实现校验是否支付已经完成，注意：此地址需要能在公网进行访问
    :return: 支付对象
    """
    ali_pay_obj = AliPay(
        appid=settings.ALI_PAY_APP_ID,
        app_notify_url=notify_url,  # 支付成功支付宝服务器异步通知默认回调url, 即会向这个地址发送POST请求
        app_private_key_path=os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem"),
        # 支付宝的公钥，验证支付宝回传消息使用
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem"),
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=settings.ALI_PAY_DEBUG  # 是否是沙箱环境, 默认False
    )

    return ali_pay_obj


def is_app_pay(order_string):
    """
    判断是否是App支付
    :param order_string: 签名后的订单信息
    :return: True or False
    支付宝支付功能对应的方法:
    注意: App支付不需要传支付网关ALI_PAY_URL
    电脑网站支付: alipay.trade.page.pay
    手机网站支付: alipay.trade.wap.pay
    App支付: alipay.trade.app.pay
    小程序支付: alipay.trade.create
    当面付(条码支付): alipay.trade.pay
    交易预创建(扫码支付): alipay.trade.precreate
    """
    order_dict = dict()
    for i in order_string.split('&'):
        temp_list = i.split("=")
        order_dict[temp_list[0]] = temp_list[1]

    method = order_dict.get("method")

    return True if "app" in method else False
