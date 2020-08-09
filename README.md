# Alipay_demo
### 一、说明：
- 本Demo使用的是python-alipay-sdk，github连接：https://github.com/fzlee/alipay
- 本Demo下载即用，对以下支付功能兼容：（只需更改对应的方法即可）
    - 电脑网站支付: alipay.trade.page.pay
    - 手机网站支付: alipay.trade.wap.pay
    - App支付: alipay.trade.app.pay
- 如需其他支付功能，可根据上述提供的SDK地址进行扩展

### 二、开发环境：
- Django 2.0
- python 3.6 
- python-alipay-sdk 1.7.1

注意：本Demo使用1.7.1版本的SDK，2.0版本以上的SDK，AliPay对象去掉了app_private_key_path、alipay_public_key_path属性，用app_private_key_string、alipay_public_key_string代替

### 三、博客
- CSDN地址： [Django 对接支付宝电脑网站、手机网站、App支付步骤详解](https://blog.csdn.net/PY0312/article/details/107890120)
