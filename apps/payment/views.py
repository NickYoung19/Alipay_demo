# Create your views here.
import json
import random

from urllib import parse

from django.conf import settings
from django.db.transaction import atomic
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from apps.payment.utils import my_ali_pay, is_app_pay
from utils.common import get_domain, Redis

# redis连接对象
redis = Redis().connection()


@csrf_exempt
def index(request):
    """
    给template返回数据，利用django模板进行测试，正常开发情况下由前端发起请求，参考接口get_pay_url即可
    :param request:
    :return:
    """

    if request.method == "GET":
        return render(request, 'index.html')

    money = float(request.POST.get('price'))  # 保留俩位小数  前端传回的金额数据
    # 组织订单编号：当前时间字符串 + 6位随机数 ---> 20200808154711123456
    out_trade_no = timezone.now().strftime('%Y%m%d%H%M%S') + ''.join(map(str, random.sample(range(0, 9), 6)))

    # 生成支付宝支付链接地址
    domain_name = get_domain(request)
    notify_url = domain_name + '/payment/update_order/'
    ali_pay = my_ali_pay(notify_url)
    order_string = ali_pay.api_alipay_trade_page_pay(
        out_trade_no=out_trade_no,  # 订单编号
        total_amount=str(money),  # 交易金额(单位: 元 保留俩位小数)   这里一般是从前端传过来的数据
        subject=f"产品名称-{out_trade_no}",  # 商品名称或产品名称
        return_url=domain_name + "/payment/get_result/",  # 支付成功后跳转的页面，App支付此参数无效，集成支付宝SDK自带跳转
    )
    # 拼接支付链接，注意：App支付不需要返回支付宝网关
    ali_pay_url = order_string if is_app_pay(order_string) else settings.ALI_PAY_URL + "?" + order_string

    # 设置redis key空间过期事件，实现key过期自动取消订单，这里过期时间模拟设为10秒
    prefix = 'nick_'
    key_name = f"{prefix}{out_trade_no}"  # 拼接key：自定义前缀'nick_' + '订单编号'
    seconds = 30 * 60  # 30分钟订单自动取消
    redis.setex(key_name, 10 if settings.DEBUG else seconds, "use_cancel_order")  # key, seconds, value

    return redirect(ali_pay_url)


@csrf_exempt
def get_pay_url(request):
    """
    获取支付宝支付链接
    :param request:
    :return: 支付链接ali_pay_url
    """
    if request.method == "GET":
        order_id = request.GET.get('order_id', 0)  # 前端传回的订单id
        money = request.GET.get('price')  # 前端传回的金额数据

        if not all([order_id, money]):
            return JsonResponse(dict(message="参数错误"))

        # 此处可增加根据订单id查询判断该订单是否存在相关业务逻辑

        # 组织订单编号：当前时间字符串 + 6位随机数 ---> 20200808154711123456
        out_trade_no = timezone.now().strftime('%Y%m%d%H%M%S') + ''.join(map(str, random.sample(range(0, 9), 6)))

        # 生成支付宝支付链接地址
        domain_name = get_domain(request)
        notify_url = domain_name + '/payment/update_order/'
        ali_pay = my_ali_pay(notify_url)
        order_string = ali_pay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,  # 订单编号
            total_amount=str(money),  # 交易金额(单位: 元 保留俩位小数)   这里一般是从前端传过来的数据
            subject=f"产品名称-{out_trade_no}",  # 商品名称或产品名称
            return_url=domain_name + "/payment/get_result/",  # 支付成功后跳转的页面，App支付此参数无效，集成支付宝SDK自带跳转
        )
        # 拼接支付链接，注意：App支付不需要返回支付宝网关
        ali_pay_url = order_string if is_app_pay(order_string) else settings.ALI_PAY_URL + "?" + order_string

        return JsonResponse(dict(ali_pay_url=ali_pay_url))

    return JsonResponse(dict(ali_pay_url=""))


@csrf_exempt
def pay_result(request):
    """
    支付完成后，前端同步通知回调
    :param request:
    :return: 根据业务需求自定义返回信息
    """
    if request.method == "GET":
        data = request.GET.dict()
        # 同步验签data参数转换字典后示例如下：
        """
        {
            'charset': 'utf-8', 
            'out_trade_no': '20200808154711123456', 
            'method': 'alipay.trade.page.pay.return', 
            'total_amount': '0.01', 
            'sign': 'OBCdRRpUHtjAR15v9s26cU1juP+ub0COKRe3hJg2kCsMZIhCT3Kx......meYt0G2Kir/Ld77gp+OFLza2G5HrIrA==', 
            'trade_no': '2020080622001460481437011111', 
            'auth_app_id': '2016101000655892', 
            'version': '1.0', 
            'app_id': '2016101000655892', 
            'sign_type': 'RSA2', 
            'seller_id': '2078131328364326', 
            'timestamp': '2020-08-06 14:47:25'
        }
        """
        ali_pay = my_ali_pay()
        sign = data.pop('sign', None)
        success = ali_pay.verify(data, sign)
        print("同步回调验签状态: ", success)
        if success:
            # 此处写支付验签成功的相关业务逻辑
            return JsonResponse(dict(message="支付成功"))

        return JsonResponse(dict(message="支付失败"))

    return JsonResponse(dict(message="支付失败"))


@csrf_exempt
@atomic()
def update_order(request):
    """
    支付成功后，支付宝服务器异步通知回调（用于修改订单状态）
    :param request:
    :return: success or fail
    """
    if request.method == "POST":

        body_str = request.body.decode('utf-8')
        data = parse.parse_qs(body_str)
        # data = parse.parse_qs(parse.unquote(body))  # 回传的url中如果发现被编码，这里可以用unquote解码再转换成字典
        # 异步通知data参数转换字典后示例如下：
        """
        {
            'auth_app_id': '2016101000655892', 
            'version': '1.0', 
            'charset': 'utf-8', 
            'subject': '产品名称-20200808154711123456', 
            'trade_status': 'TRADE_SUCCESS', 
            'app_id': '2016101000655892', 
            'total_amount': '0.01', 
            'buyer_pay_amount': '0.01', 
            'receipt_amount': '0.01', 
            'point_amount': '0.00', 
            'invoice_amount': '0.01', 
            'trade_no': '2020080622001460481436956490', 
            'sign_type': 'RSA2', 
            'buyer_id': '2083402614260483', 
            'notify_time': '2020-08-06 12:38:06', 
            'notify_id': '2020080600125143806060481455916209', 
            'notify_type': 'trade_status_sync', 
            'fund_bill_list': '[{"amount":"0.01","fundChannel":"PCREDIT"}]', 
            'gmt_create': '2020-08-06 12:38:02', 
            'gmt_payment': '2020-08-06 12:38:06', 
            'seller_id': '2078131328364326', 
            'out_trade_no': '20200808154711123456', 
            'sign': 'YNeo9DqaKZzCLwN+7zYMCeYn6+pmo5fxCv/KtCWa8zBzNNKowRc23......iU30qCPFSzq/t4UtJ4TwA5/pfHo9cNlbKQA=='
        }
        """

        data = {k: v[0] for k, v in data.items()}

        ali_pay = my_ali_pay()
        sign = data.pop('sign', None)
        success = ali_pay.verify(data, sign)  # 返回验签结果, True/False
        print("异步通知验证状态: ", success)
        if success:
            # 此处写支付验签成功修改订单状态相关业务逻辑
            return HttpResponse('success')  # 返回success给支付宝服务器, 若支付宝收不到success字符会重复发送通知
        return HttpResponse('fail')

    return HttpResponse('fail')


@csrf_exempt
@atomic()
def cancel_order(request):
    if request.method == "POST":
        post = json.loads(request.body, strict=False)
        order_id = post.get("order_id", 0)
        if not order_id:
            return JsonResponse(dict(message="参数错误"))
        # 取消订单业务逻辑实现
        # 校验订单，查询订单是否存在
        # 存在即更新订单状态
        return JsonResponse(dict(message="取消订单成功"))

    return JsonResponse(dict(message="请求方法错误，取消订单失败"))
