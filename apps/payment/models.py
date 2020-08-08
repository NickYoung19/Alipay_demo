from django.db import models

# Create your models here.


class PaymentRecords(models.Model):
    """
    支付信息记录表
    """
    # order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, verbose_name='订单')
    trade_id = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='支付编号')
    ali_trade_id = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='支付宝订单号')
    pay_time = models.DateTimeField("支付时间")  # 订单支付完成时间

    class Meta:
        db_table = 'payment_records'
        verbose_name = '支付记录'
